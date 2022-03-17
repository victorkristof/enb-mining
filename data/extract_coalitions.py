import csv
from pathlib import Path


def write(path, party, groups):
    with path.open('a+') as f:
        f.write(party + ': [')
        f.write(', '.join(groups))
        f.write(']\n')


coalition_path = Path('data/coalition-matrix.csv')
output_path = Path('data/coalitions.txt')
output_path.unlink(missing_ok=True)

with coalition_path.open(encoding='utf-8-sig') as f:
    for row in csv.DictReader(f, skipinitialspace=True):
        party = row.pop('country')
        groups = list()
        for key, val in row.items():
            if bool(val):
                groups.append(key)
        write(output_path, party, groups)
