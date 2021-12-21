from .utils import save_csv

INTERACTION_TYPES = set(['on-behalf', 'agreement', 'support', 'opposition'])


class Interaction:
    def __init__(self, entity_a, entity_b, sentence, issue, interaction_type):
        self.entity_a = entity_a.upper()
        self.entity_b = entity_b.upper()
        self.sentence = sentence
        self.date = issue['issue_date']
        self.issue_id = int(issue['id'])
        if interaction_type not in INTERACTION_TYPES:
            raise ValueError(f'Invalid type "{interaction_type}"')
        self.type = interaction_type

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
