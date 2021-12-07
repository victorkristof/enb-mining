import csv

import fire
from enbmining import Client


def save(issues, output_path):
    keys = sorted(issues[0].keys())
    with open(output_path, 'w', newline='') as file:
        dict_writer = csv.DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(issues)
    print(f'Saved {output_path}')


def main(output_path, debug=False):
    client = Client(negotiation='UNFCCC', debug=debug)
    issues = client.get_issues_metadata(start_page=1, end_page=9)
    save(issues, output_path)


if __name__ == '__main__':
    fire.Fire(main)
