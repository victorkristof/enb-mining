from nltk.chunk.regexp import ChunkRule, RegexpChunkParser

from .utils import combine, save_csv


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
        'for the',
        'for several',
        'for a number of members of the',
    ]

    chunk_rules = [
        ChunkRule(r'(<ENT><OBH><ENT>+(<CC><ENT>)?)+', 'On behalf'),
    ]

    def __init__(self, entity_a, entity_b, sentence, issue):
        super().__init__(entity_a, entity_b, sentence, issue)
        self.type = self.__class__.__name__

    @classmethod
    def identify(cls, tagged_sentence, sentence, issue):
        chunk_parser = RegexpChunkParser(cls.chunk_rules, chunk_label=cls.tag)
        tree = chunk_parser.parse(tagged_sentence)
        interactions = list()
        print(tree)
        for subtree in tree.subtrees():
            if subtree.label() == cls.tag:
                interactions.extend(
                    cls.subtree2instances(subtree, sentence, issue)
                )
        return interactions

    @staticmethod
    def subtree2instances(subtree, sentence, issue):
        side, entities_a, entities_b = 'left', list(), list()
        for token, tag in subtree:
            if side == 'left':
                if tag == 'ENT':
                    entities_a.append(token)
            if side == 'right':
                if tag == 'ENT':
                    entities_b.append(token)
            if tag == 'OBH':
                side = 'right'
        return [
            OnBehalf(a, b, sentence, issue)
            for a, b in combine(entities_a, entities_b)
        ]
