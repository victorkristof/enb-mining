import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = 'https://enb.iisd.org/'
PAGE = 'page={number}'

NEGOTIATIONS = {'UNFCCC': 'un-framework-convention-climate-change-unfccc/'}


class Client:
    def __init__(self, negotiation='UNFCCC', debug=False):
        self.negotiation = NEGOTIATIONS[negotiation]
        self.debug = debug

    def get_issues_metadata(self, start_page, end_page, missing_meetings=[]):
        issues = list()
        # Scrape issues from list of all meetings.
        for page_number in range(start_page - 1, end_page):  # Offset index.
            if self.debug:
                print(f'Scraping page {page_number+1}...')
            issues.extend(self._scrape_issues_from_meetings(page_number))
            time.sleep(1)
        # Scrape missing meetings.
        if self.debug and len(missing_meetings) > 0:
            print('Scraping missing meetings...')
        for meeting in missing_meetings:
            issues.extend(self._scrape_missing_meeting(meeting))
        # Assign IDs in chronological orders (doesn't work with missing
        # meetings)
        issues = self._assign_ids(issues)
        return issues

    def _scrape_missing_meeting(self, meeting):
        issues = list()
        issue_details = self._scrape_issues(meeting['url'])
        for issue in issue_details:
            issue |= {
                'meeting': meeting['meeting'],
                'meeting_date': meeting['meeting_date'],
            }
            issues.append(issue)
        return issues

    def _scrape_issues_from_meetings(self, page_number):
        url = self._get_negotiation_url(page_number)
        page = self._get_page(url)
        return self._scrape_issues_metadata(BeautifulSoup(page, 'lxml'))

    def _scrape_issues_metadata(self, soup):
        issues = list()
        rows = soup.find_all(class_='views-row')
        for row in rows:
            heading = row.find('a', class_='c-list-item__heading-link')
            meeting = heading.get_text()
            date = row.find('span', class_='c-list-item__meta-date')
            date = date.get_text().replace('–', '-')
            url = self._build_url(heading.get('href'))
            issue_details = self._scrape_issues(url)
            for issue in issue_details:
                issue |= {'meeting': meeting, 'meeting_date': date}
                issues.append(issue)
        return issues

    def _scrape_issues(self, url):
        soup = BeautifulSoup(self._get_page(url), 'lxml')
        location = self._get_location(soup)
        coverage = soup.find('div', id='tab-by-date')
        issues = list()
        for section in coverage.find_all('section'):
            issue_type = self._get_issue_type(section)
            # Skip issues that report highlights.
            if issue_type is None:
                continue
            issues.append(
                {
                    'url': self._get_issue_url(section),
                    'issue_date': self._get_issue_date(section),
                    'type': issue_type,
                    'location': location,
                }
            )
        return issues

    def _get_negotiation_url(self, page_number):
        args = '?' + PAGE.format(number=page_number)
        return BASE_URL + 'negotiations/' + self.negotiation + args

    def _build_url(self, href):
        if href[0] == '/':
            return BASE_URL + href[1:]
        return BASE_URL + href

    def _get_page(self, url):
        # Use Selenium to fetch the page as a real browser
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
            # Wait for the page to load. Increase the sleep if needed.
            import time
            time.sleep(2)
            page_source = driver.page_source
        finally:
            driver.quit()
        return page_source

    def _get_location(self, soup):
        datevenue = soup.find('p', class_='c-banner__date-and-venue')
        datevenue = datevenue.get_text().split('|')
        if len(datevenue) == 2:
            return datevenue[1].strip()
        return None

    def _get_issue_type(self, section):
        title = section.find(
            'span',
            class_='o-accordion-item__title o-accordion-item__title--no-date',
        ).get_text()
        if title == 'Report of main proceedings' or title == 'Daily report':
            return 'issue'
        elif title == 'Summary report':
            return 'summary'
        elif title == 'Curtain raiser':
            return 'curtain-raiser'
        return None

    def _get_issue_date(self, section):
        date = section.find(
            'span', class_='o-accordion__heading-text'
        ).get_text()
        if date != 'Pre event content':
            date = date.replace('–', '-')  # Normalize dash.
            return date
        return None

    def _get_issue_url(self, section):
        link = section.find('a', class_='o-accordion-item__heading-link')
        return self._build_url(link.get('href'))

    def _assign_ids(self, issues):
        return [iss | {'id': i + 1} for i, iss in enumerate(reversed(issues))]
