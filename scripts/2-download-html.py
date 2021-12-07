import csv
import os
import random
import time
from pathlib import Path

import fire
import requests


def log(issue, response, html_folder):
    with open(str(html_folder / Path('log.txt')), 'a+') as f:
        print(f'Status {response.status_code} for issue {issue["id"]}', file=f)


def load_csv(input_path):
    with open(input_path) as f:
        return [
            {k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)
        ]


def save_html(content, path):
    with open(path, 'w') as f:
        f.write(content)


def main(input_path, html_folder, debug=False):
    issues = load_csv(input_path)

    for issue in issues:
        path = str(html_folder / Path(issue['id'] + '.html'))
        if os.path.exists(path):
            continue

        if debug:
            print(f'Downloading issue {issue["id"]}')

        time.sleep(random.uniform(0, 2))
        url = issue['url']
        r = requests.get(url)
        if r.status_code >= 400:
            if debug:
                log(issue, r, html_folder)
            continue
        save_html(r.text, path)


if __name__ == '__main__':
    fire.Fire(main)
