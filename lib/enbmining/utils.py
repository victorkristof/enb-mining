import csv
from itertools import chain
from pathlib import Path


class Entity:
    def __init__(self, name, alias_of=None):
        self.name = name
        self.alias_of = alias_of

    def __repr__(self):
        return self.name

    def __str__(self):
        if self.alias_of is not None:
            return f'{self.name} [{self.alias_of}]'
        else:
            return self.name

    def __eq__(self, other):
        return self.name == other.name and self.alias_of == other.alias_of

    def __hash__(self):
        return hash((self.name, self.alias_of))

    @classmethod
    def load_entities(cls, path):
        def get_determinant(entity, determinant='the'):
            # The determinant is specified in parenthesis.
            determinant_key = f'({determinant})'
            if determinant_key in entity:
                entity = entity.replace(determinant_key, '').strip()
            else:
                determinant = None
            return entity, determinant

        def get_aliases(line):
            if ':' in line:
                entity, aliases = line.split(':')
                delim = ';' if ';' in aliases else ','
                aliases = [a.strip() for a in aliases.split(delim)]
                return entity, aliases
            else:
                return line, list()

        path = Path(path)
        with path.open() as f:
            lines = [e.strip() for e in f.readlines()]
        entities = set()
        for line in lines:
            entity, aliases = get_aliases(line)
            entity, determinant = get_determinant(entity)
            entities |= cls._combine(entity, aliases, determinant)
        return entities

    @staticmethod
    def _combine(entity, aliases, determinant):
        # Add the entity it self.
        result = set([Entity(entity)])
        # Add the entity with the determinant.
        if determinant is not None:
            det_entity = ' '.join([determinant, entity])
            result.add(Entity(det_entity, entity))
            result.add(Entity(det_entity.upper(), entity))
        # Add the entity in upper case if it's not already in upper case.
        if entity.upper() != entity:
            result.add(Entity(entity.upper(), entity))
        # Add all aliases, also in upper case, and with the determinant.
        for alias in aliases:
            result.add(Entity(alias, entity))
            result.add(Entity(alias.upper(), entity))
            if determinant is not None:
                det_alias = ' '.join([determinant, alias])
                result.add(Entity(det_alias, entity))
                result.add(Entity(det_alias.upper(), entity))
        return result


def save_csv(list_of_dict, output_path, sort_keys=False, keys=None):
    if keys is None:
        if sort_keys:
            keys = sorted(list_of_dict[0].keys())
        else:
            keys = list_of_dict[0].keys()
    output_path = Path(output_path)
    with output_path.open('w', newline='') as file:
        dict_writer = csv.DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dict)
    print(f'Saved CSV to {output_path}')


def load_csv(path):
    path = Path(path)
    with path.open() as f:
        return [
            {k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)
        ]


def load_html(html_folder, issue_id):
    path = html_folder / Path(issue_id).with_suffix('.html')
    with path.open() as f:
        return f.read()


def print_progress(index, array, every_n=None):
    if every_n is not None and (
        index % every_n == 0 or index == len(array) - 1
    ):
        print(f'{(index+1)/len(array)*100:.0f}%', end='\r')


def combine(array1, array2):
    """Generates all dyads from two arrays, without self-loops."""
    return [(a, b) for a in array1 for b in array2 if a != b]


def flatten(iterable):
    return list(chain.from_iterable(iterable))
