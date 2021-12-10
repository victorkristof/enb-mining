import re
from itertools import chain

from bs4 import BeautifulSoup

from .nlp import SentenceTokenizer, WordTokenizer
from .utils import save_csv


class Intervention:
    def __init__(self, entity, sentence, issue):
        self.entity = entity
        self.sentence = sentence
        self.date = issue['issue_date']
        self.issue_id = int(issue['id'])

    @staticmethod
    def to_csv(interventions, path):
        keys = ['issue_id', 'entity', 'date', 'sentence']
        # Create dicts of interventions.
        dicts = [{k: getattr(intv, k) for k in keys} for intv in interventions]
        # Add ID.
        dicts = [d | {'id': i + 1} for i, d in enumerate(dicts)]
        keys.insert(0, 'id')
        save_csv(dicts, path, keys=keys)

    def __str__(self):
        return ' '.join(
            [
                'Intervention by',
                self.entity,
                f'on {self.date}:',
                f'"{self.sentence}"',
                f'(Issue {self.issue_id})',
            ]
        )

    def __repr__(self):
        return self.entity


class Scraper:

    """A general scraper for interventions and interactions."""

    def __init__(self, html, issue, entities):
        """Initializes the scraper with some HTML, metadata about the ENB
        issue,  and a set of entities."""
        self.soup = BeautifulSoup(html, 'lxml')
        self.issue = issue
        self.entities = set(entities)
        self.word_tokenizer = WordTokenizer(entities)

    def extract_sentences(self):
        content = self.soup.find(
            'section', class_='o-content-from-editor--report'
        )
        paragraphs = content.find_all('p')
        tokenizer = SentenceTokenizer()
        sentences = list()
        for paragraph in paragraphs:
            text = paragraph.get_text()
            text = self._clean(text)
            sentences.extend(tokenizer.tokenize(text))

        return sentences

    def _clean(self, text):
        # Remove exclamation marks from names (for sentence tokenizer).
        text = re.sub(r'(Climate Justice Now)!', r'\1', text)
        text = re.sub(r'(CLIMATE JUSTICE NOW)!', r'\1', text)
        text = re.sub(r'(CJN)!', r'\1', text)
        text = re.sub(r'(ACT)!', r'\1', text)
        # Rename a.m./p.m. as am/pm.
        text = re.sub(r'a\.m\.', r'am', text)
        text = re.sub(r'p\.m\.', r'pm', text)
        # Normalize spaces.
        text = re.sub('\r', ' ', text)
        text = re.sub('\n', ' ', text)
        text = re.sub('\xa0+', ' ', text, flags=re.UNICODE)
        text = re.sub('\s\s+', ' ', text)
        return text


class InterventionScraper(Scraper):
    def __init__(self, html, issues, entities):
        super().__init__(html, issues, entities)

    def scrape(self):
        # Create a list of list of interventions.
        interventions = [
            self._extract_interventions(sentence)
            for sentence in self.extract_sentences()
        ]
        # Flatten this nested list.
        return list(chain.from_iterable(interventions))

    def _extract_interventions(self, sentence):
        """Extracts a list of interventions from a sentence."""
        tokens = set(self.word_tokenizer.tokenize(sentence))
        matches = tokens.intersection(self.entities)
        return [
            Intervention(entity, sentence, self.issue) for entity in matches
        ]


# %% DEBUG.
# import glob

# html_folder = 'data/html/*.html'
# html_files = glob.glob(html_folder)
# sentences = list()
# for i, html_file in enumerate(html_files):
#     # html_file = 'data/html/100.html'
#     with open(html_file) as f:
#         html = f.read()
#     scraper = InterventionScraper(html)
#     sentences.extend(scraper.extract_sentences())
#     if i % 10 == 0 or i == len(html_files) - 1:
#         print(f'{(i+1)/len(html_files)*100:.0f}%', end='\r')

# count = 0
# for i, s in enumerate(sentences):
#     if s[0].islower() and s[:4] != 'date' and s[:8] != 'location':
#         last_char = sentences[i - 1][-1]
#         if last_char != ';' and last_char != ':':
#             print(sentences[i - 1])
#             print(s)
#             print()
#             count += 1
# print(count)
