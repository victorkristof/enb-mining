from nltk.chunk.regexp import ChunkRule, RegexpChunkParser

from .utils import flatten, save_csv


class Interaction:
    def __init__(self, entity_a, entity_b, sentence, issue):
        self.entity_a = entity_a
        self.entity_b = entity_b
        self.sentence = sentence
        self.date = issue['issue_date']
        self.issue_id = int(issue['id'])

    @staticmethod
    def to_csv(interactions, path):
        keys = ['issue_id', 'entity_a', 'entity_b', 'type', 'date', 'sentence']
        # Create dicts of interventions.
        dicts = [{k: getattr(intv, k) for k in keys} for intv in interactions]
        # Add ID.
        dicts = [d | {'id': i + 1} for i, d in enumerate(dicts)]
        keys.insert(0, 'id')
        save_csv(dicts, path, keys=keys)

    @classmethod
    def identify(cls, tagged_sentence, sentence, issue):
        return flatten(
            [
                cls._parse(parser, tagged_sentence, sentence, issue)
                for parser in cls.parsers
            ]
        )

    @classmethod
    def _parse(cls, parser, tagged_sentence, sentence, issue):
        args, parser, aggregator = (
            parser.get('args', {}),
            parser['parser'],
            parser['aggregator'],
        )
        tree = parser.parse(tagged_sentence)
        interactions = list()
        for subtree in tree.subtrees():
            if subtree.label() == cls.tag:
                interactions.extend(
                    getattr(cls, aggregator)(subtree, sentence, issue, **args)
                )
        return interactions

    @classmethod
    def markedsubtree2instances(cls, subtree, sentence, issue, inverse=False):
        """Converts a subtree with a marker into a list of instances.

        A marker is a specific tag that splits the sentence in to to, e.g.,
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
            return [cls(b, a, sentence, issue) for b in bs]
        else:
            return [cls(a, b, sentence, issue) for b in bs]

    @classmethod
    def inversedsubtree2instances(cls, subtree, sentence, issue):
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
        return [cls(b, a, sentence, issue) for b in bs]

    def __str__(self):
        return ' '.join(
            [
                f'{self.__class__.__name__}:',
                self.entity_a,
                self.entity_b,
                f'on {self.date}:',
                f'"{self.sentence}"',
                f'(Issue {self.issue_id})',
            ]
        )

    def __repr__(self):
        return '-'.join(
            [self.entity_a, self.__class__.__name__, self.entity_b]
        )


class OnBehalf(Interaction):

    tag = 'OBH'
    tokens = [
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
    parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2instances',
        }
    ]

    def __init__(self, entity_a, entity_b, sentence, issue):
        super().__init__(entity_a, entity_b, sentence, issue)
        self.type = self.__class__.__name__


class Support(Interaction):

    tag = 'SUP'
    tokens = [
        'Supported by',
        'supported by',
        'supported by the',
    ]

    # Match "A supported by B[, C, and D]" and similar.
    chunk_rules = [ChunkRule(r'<ENT><SUP><ENT>+(<CC><ENT>)?', 'Support')]
    parsers = [
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'markedsubtree2instances',
            'args': {'inverse': True},
        }
    ]
    # Match "Supported by B[,C, and D], A".
    chunk_rules = [ChunkRule(r'^<SUP><ENT>+(<CC><ENT>)?<ENT>', 'Support')]
    parsers.append(
        {
            'parser': RegexpChunkParser(chunk_rules, chunk_label=tag),
            'aggregator': 'inversedsubtree2instances',
        }
    )

    def __init__(self, entity_a, entity_b, sentence, issue):
        super().__init__(entity_a, entity_b, sentence, issue)
        self.type = self.__class__.__name__
