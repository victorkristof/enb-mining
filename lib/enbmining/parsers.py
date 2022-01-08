from abc import ABC, abstractmethod

from nltk.chunk.regexp import ChunkRule, RegexpChunkParser
from nltk.tree import Tree

from .data import Interaction, Intervention
from .utils import combine, flatten

ENTITY = set(['PAR', 'GRP'])


class Parser(ABC):
    def __init__(self, sentence, issue):
        self.sentence = sentence
        self.issue = issue

    @abstractmethod
    def parse(self, tagged_sentence):
        ...


class InterventionParser(Parser):
    def parse(self, tagged_sentence):
        # Remove patterns "(Country)", corresponding to people from a country
        # being mentionned in the bulletin.
        tagged_sentence = self._remove_in_parenthesis(tagged_sentence)
        # Collapse the 'on-behalf' interactions.
        tagged_sentence = OnBehalfParser.collapse(tagged_sentence)
        return self._to_interventions(
            set([token for token, tag in tagged_sentence if tag in ENTITY])
        )

    @staticmethod
    def _remove_in_parenthesis(tagged_sentence):
        parenthesis_chunker = InParenthesis()
        return parenthesis_chunker.chunk(tagged_sentence)

    def _to_interventions(self, entities):
        return [
            Intervention(entity, self.sentence, self.issue)
            for entity in entities
        ]


class InteractionParser(Parser):
    def __init__(self, sentence, issue, interaction_type):
        super().__init__(sentence, issue)
        self.type = interaction_type

    def parse(self, tagged_sentence):
        return flatten(
            [self._parse(cp, tagged_sentence) for cp in self.chunk_parsers]
        )

    def _parse(self, chunk_parser, tagged_sentence):
        args, aggregator, chunk_parser = (
            chunk_parser.get('args', {}),
            chunk_parser.get('aggregator'),
            chunk_parser['parser'],
        )
        # If an aggregator is not specified, we ignore the parser.
        if aggregator is None:
            return list()
        # Collapse the 'on-behalf' interactions if it's not one.
        if self.type != 'on-behalf':
            tagged_sentence = OnBehalfParser.collapse(tagged_sentence)
            # Collapse the 'agreement' interactions if it's not one (depends on
            # the collapse of 'on-behalf' interactions.
            if self.type != 'agreement':
                tagged_sentence = AgreementParser.collapse(tagged_sentence)

        tree = chunk_parser.parse(tagged_sentence)
        interactions = list()
        for subtree in tree.subtrees():
            if subtree.label() == self.tag:
                interactions.extend(getattr(self, aggregator)(subtree, **args))
        return interactions

    @staticmethod
    def index_of(target_tag, subtree):
        for i, (_, tag) in enumerate(subtree):
            if tag == target_tag:
                return i
        raise ValueError(f'Tag "{target_tag}" not found in subtree')

    @staticmethod
    def _unroll_agreement(subtree):
        """Unrolls <AGR> tokens into a list of parties and groupings."""

        new_subtree = list()
        for token, tag in subtree:
            if tag == 'AGR':
                new_subtree.extend(token)
            else:
                new_subtree.append((token, tag))
        return new_subtree

    def markedsubtree2interactions(self, subtree, inverse=False):
        """Converts a subtree with a marker into a list of interactions.

        A marker is a specific tag that splits the sentence in to two, e.g.,
        "A on behalf of B". The marker is "on behalf of" as it splits the
        sentence into two parts. Depending on the interaction, the order of
        A and B might be `inversed` (e.g, "A for B" and "B supported by A")"""

        # Unroll agreement tags into list of entities.
        subtree = self._unroll_agreement(subtree)
        # Keep only the entity tags and the parser's tag.
        keep = set(['PAR', 'GRP', self.tag])
        subtree = [(token, tag) for token, tag in subtree if tag in keep]
        # Find index of parser's tag that we will use as "pivot".
        index = self.index_of(self.tag, subtree)
        # And keep only the tokens, not the tags.
        left = [token for token, _ in subtree[:index]]
        right = [token for token, _ in subtree[index + 1 :]]
        # Return instances of Interactions.
        if inverse:
            return [
                Interaction(rt, lt, self.sentence, self.issue, self.type)
                for lt in left
                for rt in right
            ]
        else:
            return [
                Interaction(lt, rt, self.sentence, self.issue, self.type)
                for lt in left
                for rt in right
            ]

    def inversedsubtree2interactions(self, subtree):
        """Converts a subtree whose marker is inversed.

        An inversed marker means that the subtree starts with the marker, as in
        "Supported by B[, C, ...], A...". This creates interactions in the form
        "B supports A", "C supports A", etc."""

        # Unroll agreement tags into list of entities.
        subtree = self._unroll_agreement(subtree)
        subtree = [token for token, tag in subtree if tag in ENTITY]
        # We know the first nodes are B, C, ...
        bs = subtree[:-1]
        # ...and the the last one is entity A.
        a = subtree[-1]
        return [
            Interaction(b, a, self.sentence, self.issue, self.type) for b in bs
        ]

    def list2interactions(self, subtree):
        """Converts a subtree whose elements are in a list.

        This method is used to convert a list of parties and/or groupings that
        agree together, e.g., "A, B, and C"."""
        subtree = [token for token, tag in subtree if tag in ENTITY]
        return [
            Interaction(a, b, self.sentence, self.issue, self.type)
            for a, b in combine(subtree, subtree)
        ]


class InParenthesis:
    def __init__(self):
        self.tag = 'PTH'
        chunk_rules = [ChunkRule(r'<\(><PAR|GRP><\)>', 'In parenthesis')]
        self.chunk_parser = RegexpChunkParser(
            chunk_rules, chunk_label=self.tag
        )

    def chunk(self, tagged_sentence):
        tree = self.chunk_parser.parse(tagged_sentence)
        tagged_sentence = list()
        for node in tree:
            # The subtree is a "PTH" chunk; we transform them into tagged list.
            if type(node) == Tree:
                tagged_sentence.append((node[:], 'PTH'))
            # The others are kept as is.
            elif type(node) == tuple:
                tagged_sentence.append(node)
            else:
                print('Error with node', type(node), node)
        return tagged_sentence


class OnBehalfParser(InteractionParser):

    tag = 'OBH'
    markers = [
        'also on behalf of',
        'on behalf of',
        'speaking on behalf of',
        'speaking for',
        'also speaking for',
        'for',
        'for several',
        'for a number of members of',
    ]

    # Match "A, on behalf of B", where A is a party and B is a grouping.
    cr = r'<PAR><,><OBH><GRP><,>|'
    # Same without the commas.
    cr += r'<PAR><OBH><GRP>'
    chunk_rules = [ChunkRule(cr, 'Party on behalf grouping')]

    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': None,  # This type of interaction is collapsed.
        }
    ]

    # Match "A, on behalf of B[, C, and D],", using the first and last comma as
    # delimiter for the list of entities being represented. In this case,
    # a grouping can never appear on the right side of the regex.
    cr = r'<PAR><,><OBH>((<PAR><,>)*<PAR><CC><PAR>|<PAR><,>)'
    chunk_rules = [ChunkRule(cr, 'Party on behalf other parties')]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2interactions',
        }
    )

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'on-behalf')

    @classmethod
    def collapse(cls, tagged_sentence):
        # First, collapse the case where a party represents a grouping (keep
        # the grouping only).
        tagged_sentence = cls._collapse_party_obh_grouping(tagged_sentence)
        # Second, collapse the case where a party represents other parties
        # (keep all the parties, including the one representing the others).
        tagged_sentence = cls._collapse_party_obh_parties(tagged_sentence)
        return tagged_sentence

    @classmethod
    def _collapse_party_obh_grouping(cls, tagged_sentence):
        def collapse_func(subtree):
            # We find the index of the OBH tag that is a "pivot" to identify
            # the right-side of the interaction, i.e., the entities that are
            # being represented by one other entity.
            index = cls.index_of('OBH', subtree)
            return subtree[index + 1 :]

        # The first parser matches parties on behalf of groupings.
        parser = cls.chunk_parsers[0]['parser']
        return cls._collapse(tagged_sentence, parser, collapse_func)

    @classmethod
    def _collapse_party_obh_parties(cls, tagged_sentence):
        def collapse_func(subtree):
            # We find the index of the OBG tag and remove it from the subtree
            # to join the party on the left-side with the ones on the
            # right-side.
            index = cls.index_of('OBH', subtree)
            return subtree[:index] + subtree[index + 1 :]

        # The second parser matches parties on behalf of other parties.
        parser = cls.chunk_parsers[1]['parser']
        return cls._collapse(tagged_sentence, parser, collapse_func)

    @classmethod
    def _collapse(cls, tagged_sentence, parser, collapse_func):
        """Collapses an OBH tag using a parser and a collapse function."""
        tree = parser.parse(tagged_sentence)
        tagged_sentence = list()
        for node in tree:
            # The subtrees are "OBH" chunks; we collapse them.
            if type(node) == Tree:
                tagged_sentence.extend(collapse_func(node))
            # The others are kept as is.
            elif type(node) == tuple:
                tagged_sentence.append(node)
            else:
                print('Error with node', type(node), node)
        return tagged_sentence


class SupportParser(InteractionParser):

    tag = 'SUP'
    markers = [
        'Supported by',
        'supported by',
        'and supported by',
        'generally supported by',
    ]

    # Match "A supported by B[, C, and D]" and similar.
    chunk_rules = [
        ChunkRule(r'(<PAR|GRP>|<AGR>)<,>?<SUP>(<PAR|GRP>|<AGR>)', 'Support')
    ]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2interactions',
            'args': {'inverse': True},  # Inverse entites A and B.
        }
    ]
    # Match "Supported by B[,C, and D], A".
    chunk_rules = [
        ChunkRule(r'^<SUP>(<AGR>|<PAR|GRP><,>)<PAR|GRP>', 'Support')
    ]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'inversedsubtree2interactions',
        }
    )

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'support')


class OppositionParser(InteractionParser):

    tag = 'OPP'
    markers = [
        'Opposed by',
        'opposed by',
    ]

    # Match "A opposed by B[, C, and D]" and similar.
    chunk_rules = [
        ChunkRule(r'(<PAR|GRP>|<AGR>)<,>?<OPP>(<PAR|GRP>|<AGR>)', 'Opposition')
    ]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2interactions',
            'args': {'inverse': True},  # Inverse entites A and B.
        }
    ]
    # Match "Opposed by B[,C, and D], A".
    chunk_rules = [
        ChunkRule(r'^<OPP>(<AGR>|<PAR|GRP><,>)<PAR|GRP>', 'Opposition')
    ]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'inversedsubtree2interactions',
        }
    )

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'opposition')


class AgreementParser(InteractionParser):

    tag = 'AGR'
    markers = list()  # No markers for agreements.

    # Match a list of entities, where multiple "and"'s can appear in the list,
    # but it will necessarily by terminated by "and ENTITY".
    chunk_rules = [
        ChunkRule(
            r'((<PAR|GRP><,>)*<PAR|GRP><,>?<CC><PAR|GRP><,>?)+', 'Aggreement'
        )
    ]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'list2interactions',
        }
    ]

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'agreement')

    @classmethod
    def collapse(cls, tagged_sentence):
        # There's only one parser for agreement interactions.
        chunk_parser = cls.chunk_parsers[0]['parser']
        tree = chunk_parser.parse(tagged_sentence)
        tagged_sentence = list()
        for node in tree:
            # The subtrees (chunks) are the "AGR" tag; we collapse them.
            if type(node) == Tree:
                tagged_sentence.append(cls._collapse(node))
            # The others are kept as is.
            elif type(node) == tuple:
                tagged_sentence.append(node)
            else:
                print('Error with node', type(node), node)
        return tagged_sentence

    @staticmethod
    def _collapse(subtree):
        # Keep only the entities
        entities = [(token, tag) for token, tag in subtree if tag in ENTITY]
        # Create new node whose tag is "AGR" and whose token is the list of
        # entities.
        return (entities, 'AGR')
