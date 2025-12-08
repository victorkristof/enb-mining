import csv
from itertools import chain
from pathlib import Path


def save_csv(list_of_dict, output_path, sort_keys=False, keys=None):
    if keys is None:
        if sort_keys:
            keys = sorted(list_of_dict[0].keys())
        else:
            keys = list_of_dict[0].keys()
    output_path = Path(output_path)
    with output_path.open('w', newline='',encoding="utf8") as file:
        dict_writer = csv.DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dict)
    print(f'Saved CSV to {output_path}')


def load_csv(path):
    path = Path(path)
    with path.open(encoding="utf8") as f:
        return [
            {k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)
        ]


def load_html(html_folder, issue_id):
    html_folder = Path(html_folder)
    path = html_folder / Path(str(issue_id)).with_suffix('.html')
    with path.open(encoding="utf8") as f:
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
