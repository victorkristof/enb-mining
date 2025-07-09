import csv
import os
import random
import time
from pathlib import Path

import fire
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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


def fetch_html_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get(url)
        import time
        time.sleep(2)
        return driver.page_source
    finally:
        driver.quit()


def main(issues_path, html_folder, debug=False):
    issues = load_csv(issues_path)

    for issue in issues:
        path = str(html_folder / Path(issue['id'] + '.html'))
        if os.path.exists(path):
            continue

        if debug:
            print(f'Downloading issue {issue["id"]}')

        time.sleep(random.uniform(0, 2))
        url = issue['url']
        html = fetch_html_with_selenium(url)
        save_html(html, path)


if __name__ == '__main__':
    fire.Fire(main)
