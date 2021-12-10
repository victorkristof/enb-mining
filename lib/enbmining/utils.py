import csv
from pathlib import Path


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


def print_progress(index, array, every_n=None):
    if every_n is not None and (
        index % every_n == 0 or index == len(array) - 1
    ):
        print(f'{(index+1)/len(array)*100:.0f}%', end='\r')
