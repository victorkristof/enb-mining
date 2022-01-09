import time

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://enb.iisd.org/'
PAGE = 'page={number}'

NEGOTIATIONS = {'UNFCCC': 'un-framework-convention-climate-change-unfccc/'}


class Client:
    def __init__(self, negotiation='UNFCCC', debug=False):
        self.negotiation = NEGOTIATIONS[negotiation]
        self.debug = debug

    def get_issues_metadata(self, start_page, end_page):
        issues = list()
        for page_number in range(start_page - 1, end_page):  # Offset index.
            if self.debug:
                print(f'Scraping page {page_number+1}')
            issues.extend(self._scrape_issues_from_meetings(page_number))
            time.sleep(1)
        issues = self._assign_ids(issues)
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
        r = requests.get(url)
        r.raise_for_status()  # Raise an error if status code is 4XX or 5XX.
        return r.text

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
        if title == 'Report of main proceedings':
            return 'issue'
        elif title == 'Summary report':
            return 'summary'
        elif title == 'Curtain raiser':
            return 'first'
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
