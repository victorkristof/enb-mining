from abc import ABC, abstractmethod

from nltk.chunk.regexp import ChunkRule, RegexpChunkParser
from nltk.tree import Tree

from .data import Interaction, Intervention
from .utils import combine, flatten

ENTITY = set(['PAR', 'GRP'])


class Parser(ABC):
    def __init__(self, sentence, issue, parties, groupings):
        self.sentence = sentence
        self.issue = issue
        # Map (multi-word) tokens (see nlp.WordTokenizer) to Entity instances.
        entities = parties + groupings
        self._token2entity = {entity.token: entity for entity in entities}

    @abstractmethod
    def parse(self, tagged_sentence):
        ...

    @staticmethod
    def _preprocess(tagged_sentence, Chunkers):
        """Preprocesses a sentence with a list of chunkers."""
        for Chunker in Chunkers:
            chunker = Chunker()
            tagged_sentence = chunker.chunk(tagged_sentence)
        return tagged_sentence


class InterventionParser(Parser):
    def __init__(self, sentence, issue, parties, groupings, heading):
        super().__init__(sentence, issue, parties, groupings)
        self.heading = heading

    def parse(self, tagged_sentence):
        # Preprocess the sentence.
        Processors = [InParenthesisChunker, CityChunker]
        tagged_sentence = self._preprocess(tagged_sentence, Processors)
        # Collapse the 'on-behalf' interactions.
        tagged_sentence = OnBehalfParser.collapse(tagged_sentence)
        return self._to_interventions(
            set(
                [
                    self._token2entity[token]
                    for token, tag in tagged_sentence
                    if tag in ENTITY
                ]
            )
        )

    def _to_interventions(self, entities):
        return [
            Intervention(entity, self.sentence, self.issue, self.heading)
            for entity in entities
        ]


class InteractionParser(Parser):
    def __init__(self, sentence, issue, interaction_type, parties, groupings, heading):
        super().__init__(sentence, issue, parties, groupings)
        self.type = interaction_type
        self.heading = heading

    def parse(self, tagged_sentence):
        """Parses a tagged sentence and returns a list of Interactions."""

        # Preprocess the sentence.
        Processors = [CityChunker]
        tagged_sentence = self._preprocess(tagged_sentence, Processors)
        # Parse it.
        return flatten(
            [self._parse(cp, tagged_sentence) for cp in self.chunk_parsers]
        )

    def _parse(self, chunk_parser, tagged_sentence):
        """Parses a tagged sentence with a given parser and returns a list of
        Interactions."""

        args, aggregator, chunk_parser = (
            chunk_parser.get('args', {}),
            chunk_parser.get('aggregator'),
            chunk_parser['parser'],
        )
        # If an aggregator is not specified, we ignore the parser.
        if aggregator is None:
            return list()
        if self.type == 'agreement':
            tagged_sentence = OnBehalfParser.collapse(
                tagged_sentence, groupings=True, parties=False
            )
        # Collapse the 'on-behalf' interactions if it's not one.
        elif self.type != 'on-behalf':
            tagged_sentence = OnBehalfParser.collapse(tagged_sentence)
            # Collapse the 'agreement' interactions (depends on the collapse of
            # 'on-behalf' interactions, so it comes after).
            tagged_sentence = AgreementParser.collapse(tagged_sentence)

        tree = chunk_parser.parse(tagged_sentence)
        interactions = list()
        for subtree in tree.subtrees():
            if subtree.label() == self.tag:
                interactions.extend(getattr(self, aggregator)(subtree, **args))
        return interactions

    @staticmethod
    def index_of(target_tag, subtree):
        """Finds the index of a target tag in a subtree."""

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

    @classmethod
    def _collapse(cls, tagged_sentence, parser, collapse_func):
        """Collapses a tag using a parser and a collapse function.

        The collapse function takes a subtree as argument and returns a list of
        (token, tag) tuples.
        """
        tree = parser.parse(tagged_sentence)
        tagged_sentence = list()
        for node in tree:
            # The subtrees are chunks that we want to collapse.
            if type(node) == Tree:
                tagged_sentence.extend(collapse_func(node))
            # The others are kept as is.
            elif type(node) == tuple:
                tagged_sentence.append(node)
            else:
                print('Error with node', type(node), node)
        return tagged_sentence

    def markedsubtree2interactions(self, subtree, inverse=False):
        """Converts a subtree with a marker into a list of interactions.

        A marker is a specific tag that splits the sentence into two, e.g.,
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
        # And keep only the tokens, not the tags, and get the Entity
        # corresponding to the token.
        left = [self._token2entity[token] for token, _ in subtree[:index] if token in self._token2entity]
        right = [self._token2entity[token] for token, _ in subtree[index + 1 :] if token in self._token2entity]
        # Return instances of Interactions.
        if inverse:
            return [
                Interaction(rt, lt, self.sentence, self.issue, self.type, self.heading)
                for lt in left
                for rt in right
            ]
        else:
            return [
                Interaction(lt, rt, self.sentence, self.issue, self.type, self.heading)
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
            Interaction(
                self._token2entity[b],
                self._token2entity[a],
                self.sentence,
                self.issue,
                self.type,
                self.heading,
            )
            for b in bs
        ]

    def list2interactions(self, subtree):
        """Converts a subtree whose elements are in a list.

        This method is used to convert a list of parties and/or groupings that
        agree together, e.g., "A, B, and C"."""
        subtree = [token for token, tag in subtree if tag in ENTITY]
        return [
            Interaction(
                self._token2entity[a],
                self._token2entity[b],
                self.sentence,
                self.issue,
                self.type,
                self.heading,
            )
            for a, b in combine(subtree, subtree)
        ]


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
        'onbehalf of',  # Missing space due to PDF extraction by ENB.
        'of behalf of',  # Typo by ENB staff.
        'also on behalf',  # Typo by ENB staff ("of" missing).
    ]

    # Match "A, on behalf of B,", where A is a party and B is a grouping.
    cr = r'<PAR><,><OBH><GRP><,|\.>|'
    # Same without the commas.
    cr += r'<PAR><OBH><GRP>|'
    # With parentheses.
    cr += r'<PAR><\(><OBH><GRP><\)>'
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
    cr = r'<PAR><,|\(><OBH>((<PAR><,>)*<PAR><AND><PAR>|<PAR><,|\.|\)>)'
    chunk_rules = [ChunkRule(cr, 'Party on behalf other parties')]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2interactions',
        }
    )

    def __init__(self, sentence, issue, parties, groupings, heading):
        super().__init__(sentence, issue, 'on-behalf', parties, groupings, heading)

    @classmethod
    def collapse(cls, tagged_sentence, groupings=True, parties=True):
        if groupings:
            # First, collapse the case where a party represents a grouping
            # (keep the grouping only).
            tagged_sentence = cls._collapse_party_obh_grouping(tagged_sentence)
            # print('After collapse grouping:', tagged_sentence)
        if parties:
            # Second, collapse the case where a party represents other parties
            # (keep all the parties, including the one representing the
            # others).
            tagged_sentence = cls._collapse_party_obh_parties(tagged_sentence)
            # print('After collapse parties: ', tagged_sentence)
        return tagged_sentence

    @classmethod
    def _collapse_party_obh_grouping(cls, tagged_sentence):
        def collapse_func(subtree):
            # We find the index of the OBH tag that is a "pivot" to identify
            # the right-side of the interaction, i.e., the entities that are
            # being represented by one other entity.
            index = cls.index_of('OBH', subtree)
            # Remove the trailing parenthesis if it exists.
            return [
                (token, tag)
                for token, tag in subtree[index + 1 :]
                if tag != ')'
            ]

        # The first parser matches parties on behalf of groupings.
        parser = cls.chunk_parsers[0]['parser']
        return cls._collapse(tagged_sentence, parser, collapse_func)

    @classmethod
    def _collapse_party_obh_parties(cls, tagged_sentence):
        def collapse_func(subtree):
            # We find the index of the OBH tag and remove it from the subtree
            # to join the party on the left-side with the ones on the
            # right-side.
            index = cls.index_of('OBH', subtree)
            subtree = subtree[:index] + subtree[index + 1 :]
            # Remove the trailing parenthesis if it exists.
            return [(token, tag) for token, tag in subtree if tag != ')']

        # The second parser matches parties on behalf of other parties.
        parser = cls.chunk_parsers[1]['parser']
        return cls._collapse(tagged_sentence, parser, collapse_func)


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
            'args': {'inverse': True},  # Inverse entities A and B.
        }
    ]
    # Match "Supported by B[,C, and D], A".
    chunk_rules = [ChunkRule(r'^<SUP>(<AGR>|<PAR|GRP><,>)<PAR|GRP>', 'Support')]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'inversedsubtree2interactions',
        }
    )

    def __init__(self, sentence, issue, parties, groupings, heading):
        super().__init__(sentence, issue, 'support', parties, groupings, heading)


class OppositionParser(InteractionParser):

    tag = 'OPP'
    markers = [
        'Opposed by',
        'opposed by',
        'and opposed by',
        'but opposed by',
    ]

    # Match "A opposed by B[, C, and D]" and similar.
    chunk_rules = [
        ChunkRule(r'(<PAR|GRP>|<AGR>)<,>?<OPP>(<PAR|GRP>|<AGR>)', 'Opposition')
    ]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2interactions',
            'args': {'inverse': True},  # Inverse entities A and B.
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

    def __init__(self, sentence, issue, parties, groupings, heading):
        super().__init__(sentence, issue, 'opposition', parties, groupings, heading)


class WhileOppositionParser(InteractionParser):

    """A parser that handles cases where the opposition marker is not right next
    to the party/groupings/agreement markers, for example "A said this, while
    B said that"."""

    tag = 'WOPP'
    markers = ['while', 'whereas']

    # Match "A[, B, and C] ... while D[,E, and F] ..."
    chunk_rules = [
        ChunkRule(
            r'(<PAR|GRP>|<AGR>)<.*>*?<,><WOPP>(<PAR|GRP>|<AGR>)',
            'While opposition',
        )
    ]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2interactions',
            'args': {'inverse': True},  # Inverse entities A and B.
        }
    ]

    def __init__(self, sentence, issue, parties, groupings, heading):
        super().__init__(sentence, issue, 'opposition', parties, groupings, heading)


class AgreementParser(InteractionParser):

    tag = 'AGR'
    markers = list()  # No markers for agreements.

    # Match a list of entities, where multiple "and" or "with" can appear in the
    # list.
    chunk_rules = [
        ChunkRule(
            r'((<PAR|GRP><,>?)*<PAR|GRP><,>?<AND|WITH>?<PAR|GRP><,>?)+',
            'Agreement',
        )
    ]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'list2interactions',
        }
    ]

    def __init__(self, sentence, issue, parties, groupings, heading):
        super().__init__(sentence, issue, 'agreement', parties, groupings, heading)

    @classmethod
    def collapse(cls, tagged_sentence):
        def collapse_func(subtree):
            # Keep only the entities.
            entities = [(token, tag) for token, tag in subtree if tag in ENTITY]
            # Create new node whose tag is "AGR" and whose token is the list of
            # entities.
            return [(entities, cls.tag)]

        # There's only one parser for agreement interactions.
        parser = cls.chunk_parsers[0]['parser']
        return cls._collapse(tagged_sentence, parser, collapse_func)


class Chunker:

    """A class that chunks specific rules in a tagged sentence."""

    def __init__(self, tag, chunk_rules):
        self.tag = tag
        self.chunk_parser = RegexpChunkParser(chunk_rules, chunk_label=tag)

    def chunk(self, tagged_sentence):
        tree = self.chunk_parser.parse(tagged_sentence)
        tagged_sentence = list()
        for node in tree:
            # The subtree is the chunk; we transform it into tagged list.
            if type(node) == Tree:
                tagged_sentence.append((node[:], self.tag))
            # The others are kept as is.
            elif type(node) == tuple:
                tagged_sentence.append(node)
            else:
                print('Error with node', type(node), node)
        return tagged_sentence


class InParenthesisChunker(Chunker):

    """Chunks "(Country)", corresponding to people from a country being
    mentioned in the bulletin."""

    def __init__(self):
        chunk_rules = [ChunkRule(r'<\(><PAR><\)>', 'In parenthesis')]
        super().__init__(tag='PTH', chunk_rules=chunk_rules)


class CityChunker(Chunker):

    """Chunks "City, Country". This is otherwise identified as an intervention
    for the country; it is obviously not one."""

    def __init__(self):
        chunk_rules = [ChunkRule(r'<NNP><,><PAR>', 'City, Country')]
        super().__init__(tag='CTY', chunk_rules=chunk_rules)
