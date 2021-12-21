from abc import ABC

from .utils import save_csv

INTERACTION_TYPES = set(['on-behalf', 'agreement', 'support', 'opposition'])


class Data(ABC):
    @classmethod
    def to_csv(cls, interventions, path):
        # Create dicts of interventions.
        dicts = [
            {k: getattr(intv, k) for k in cls._keys} for intv in interventions
        ]
        # Add ID.
        dicts = [d | {'id': i + 1} for i, d in enumerate(dicts)]
        cls._keys.insert(0, 'id')
        save_csv(dicts, path, keys=cls._keys)


class Intervention(Data):

    _keys = ['issue_id', 'entity', 'date', 'sentence']

    def __init__(self, entity, sentence, issue):
        self.entity = entity
        self.sentence = sentence
        self.date = issue['issue_date']
        self.issue_id = int(issue['id'])

    def __str__(self):
        return ' '.join(
            [
                'Intervention by',
                self.entity,
                f'on {self.date}:',
                f'"{self.sentence}"',
                f'(Issue {self.issue_id})',
            ]
        )

    def __repr__(self):
        return self.entity


class Interaction(Data):

    _keys = [
        'issue_id',
        'entity_a',
        'entity_b',
        'type',
        'date',
        'sentence',
    ]

    def __init__(self, entity_a, entity_b, sentence, issue, interaction_type):
        self.entity_a = entity_a.upper()
        self.entity_b = entity_b.upper()
        self.sentence = sentence
        self.date = issue['issue_date']
        self.issue_id = int(issue['id'])
        if interaction_type not in INTERACTION_TYPES:
            raise ValueError(f'Invalid type "{interaction_type}"')
        self.type = interaction_type

    def __str__(self):
        return ' '.join(
            [
                f'{self.type.title()}:',
                self.entity_a,
                self.entity_b,
                f'on {self.date}:',
                f'"{self.sentence}"',
                f'(Issue {self.issue_id})',
            ]
        )

    def __repr__(self):
        return ' '.join([self.entity_a, self.type, self.entity_b])
