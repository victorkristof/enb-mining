from nltk.chunk.regexp import ChunkRule, RegexpChunkParser

from .data import Interaction
from .utils import combine, flatten


class InteractionParser:
    def __init__(self, sentence, issue, interaction_type):
        self.sentence = sentence
        self.issue = issue
        self.type = interaction_type

    def identify(self, tagged_sentence):
        return flatten(
            [self._parse(cp, tagged_sentence) for cp in self.chunk_parsers]
        )

    def _parse(self, chunk_parser, tagged_sentence):
        args, aggregator, chunk_parser = (
            chunk_parser.get('args', {}),
            chunk_parser['aggregator'],
            chunk_parser['parser'],
        )
        tree = chunk_parser.parse(tagged_sentence)
        interactions = list()
        for subtree in tree.subtrees():
            if subtree.label() == self.tag:
                interactions.extend(getattr(self, aggregator)(subtree, **args))
        return interactions

    def markedsubtree2instances(self, subtree, inverse=False):
        """Converts a subtree with a marker into a list of instances.

        A marker is a specific tag that splits the sentence in to two, e.g.,
        "A on behalf of B". The marker is "on behalf of" as it splits the
        sentence into two parts. Depending on the interaction, the order of
        A and B might be `inversed` (e.g, "A for B" and "B supported by A")"""

        subtree = [token for token, tag in subtree if tag == 'ENT']
        # We know the first node is the entity A...
        a = subtree[0]
        # ...and the second node is the interaction, so we get rid of it and
        # keep only the entities B, C, etc.
        bs = subtree[1:]
        if inverse:
            return [
                Interaction(b, a, self.sentence, self.issue, self.type)
                for b in bs
            ]
        else:
            return [
                Interaction(a, b, self.sentence, self.issue, self.type)
                for b in bs
            ]

    def inversedsubtree2instances(self, subtree):
        """Converts a subtree whose marker is inversed.

        An inversed marker means that the subtree starts with the marker, as in
        "Supported by B[, C, ...], A...". This creates interactions in the form
        "B supports A", "C supports A", etc."""
        subtree = [token for token, tag in subtree if tag == 'ENT']
        # We know all nodes except the first one (interaction) and the last one
        # (entity A) are B, C, ...
        bs = subtree[:-1]
        # ...and the the last one is entity A.
        a = subtree[-1]
        return [
            Interaction(b, a, self.sentence, self.issue, self.type) for b in bs
        ]

    def list2instances(self, subtree):
        """Converts a subtree whose elements are in a list.

        This method is used to convert a list of parties and/or groupings that
        agree together, e.g., "A, B, and C"."""
        subtree = [token for token, tag in subtree if tag == 'ENT']
        return [
            Interaction(a, b, self.sentence, self.issue, self.type)
            for a, b in combine(subtree, subtree)
        ]


class OnBehalfParser(InteractionParser):

    tag = 'OBH'
    markers = [
        'also on behalf of',
        'on behalf of',
        'on behalf of the',
        'speaking on behalf of',
        'speaking on behalf of the',
        'speaking for',
        'speaking for the',
        'also speaking for',
        'for',
        'for the',
        'for several',
        'for a number of members of the',
    ]

    # Match "A on behalf of B[, C, and D]" and similar.
    # chunk_rules = [ChunkRule(r'<ENT><OBH><ENT>+(<CC><ENT>)?', 'On behalf')]
    chunk_rules = [
        # ChunkRule(r'<ENT><OBH>(?:<ENT>|<ENT><CC><ENT>)', 'On behalf')
        ChunkRule(r'<ENT><OBH>(?:<ENT>+<CC><ENT>|<ENT>)', 'On behalf')
    ]
    #
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2instances',
        }
    ]

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'on-behalf')


class SupportParser(InteractionParser):

    tag = 'SUP'
    markers = [
        'Supported by',
        'supported by',
        'supported by the',
    ]

    # Match "A supported by B[, C, and D]" and similar.
    chunk_rules = [ChunkRule(r'<ENT><SUP><ENT>+(<CC><ENT>)?', 'Support')]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2instances',
            'args': {'inverse': True},  # Inverse entites A and B.
        }
    ]
    # Match "Supported by B[,C, and D], A".
    chunk_rules = [ChunkRule(r'^<SUP><ENT>+(<CC><ENT>)?<ENT>', 'Support')]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'inversedsubtree2instances',
        }
    )

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'support')


class OppositionParser(InteractionParser):

    tag = 'OPP'
    markers = [
        'Opposed by',
        'opposed by',
        'opposed by the',
    ]

    # Match "A opposed by B[, C, and D]" and similar.
    chunk_rules = [ChunkRule(r'<ENT><OPP><ENT>+(<CC><ENT>)?', 'Opposed')]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2instances',
            'args': {'inverse': True},  # Inverse entites A and B.
        }
    ]
    # Match "Opposed by B[,C, and D], A".
    chunk_rules = [ChunkRule(r'^<OPP><ENT>+(<CC><ENT>)?<ENT>', 'Opposed')]
    chunk_parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'inversedsubtree2instances',
        }
    )

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'opposition')


class AgreementParser(InteractionParser):

    tag = 'AGR'
    markers = list()  # No markers for agreements.

    # Match a list of entities.
    chunk_rules = [ChunkRule(r'<ENT>+<CC><ENT>', 'Aggreement')]
    chunk_parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'list2instances',
        }
    ]

    def __init__(self, sentence, issue):
        super().__init__(sentence, issue, 'agreement')
