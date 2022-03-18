from abc import ABC

from .utils import save_csv

INTERACTION_TYPES = set(['on-behalf', 'agreement', 'support', 'opposition'])


class Data(ABC):
    @classmethod
    def to_csv(cls, data, path):
        # Create dicts of datum.
        dicts = [
            {k: repr(getattr(datum, k)) for k in cls._keys} for datum in data
        ]
        # Add ID.
        dicts = [d | {'id': i + 1} for i, d in enumerate(dicts)]
        keys = ['id'] + cls._keys
        save_csv(dicts, path, keys=keys)


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
                self.entity.canonical_name,
                f'(as "{self.entity.name}")',
                f'on {self.date}:',
                f'"{self.sentence}"',
                f'(Issue {self.issue_id})',
            ]
        )

    def __repr__(self):
        return repr(self.entity)

    def __hash__(self):
        return hash(
            (
                self.entity.canonical_name,
                self.sentence,
                self.date,
                self.issue_id,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.entity.canonical_name == other.entity.canonical_name
            and self.sentence == other.sentence
            and self.date == other.date
            and self.issue_id == other.issue_id
        )


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
        self.entity_a = entity_a
        self.entity_b = entity_b
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
                repr(self.entity_a),
                repr(self.entity_b),
                f'on {self.date}:',
                f'"{self.sentence}"',
                f'(Issue {self.issue_id})',
            ]
        )

    def __repr__(self):
        if self.type == 'on-behalf':
            interacts = 'ON BEHALF OF'
        elif self.type == 'agreement':
            interacts = 'AGREES WITH'
        elif self.type == 'support':
            interacts = 'SUPPORTS'
        elif self.type == 'opposition':
            interacts = 'OPPOSES'
        return ' '.join([repr(self.entity_a), interacts, repr(self.entity_b)])
