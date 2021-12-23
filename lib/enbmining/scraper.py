import re

from bs4 import BeautifulSoup

from .data import Intervention
from .interaction_parsers import (AgreementParser, OnBehalfParser,
                                  OppositionParser, SupportParser)
from .nlp import POSTagger, SentenceTokenizer, WordTokenizer
from .utils import flatten

PARSERS = [
    OnBehalfParser,
    SupportParser,
    OppositionParser,
    AgreementParser,
]


class Scraper:

    """A general scraper for interventions and interactions."""

    def __init__(self, html, issue, entities):
        """Initializes the scraper with some HTML, metadata about the ENB
        issue,  and a set of entities."""
        self.soup = BeautifulSoup(html, 'lxml')
        self.issue = issue
        self.entities = set(entities)

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

    def scrape(self):
        # Scraped interventions/interactions (list of list).
        scraped = [
            self._scrape_from_sentence(sentence)
            for sentence in self.extract_sentences()
        ]
        # Flatten this nested list.
        return flatten(scraped)

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
        text = re.sub(r'\r', ' ', text)
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'\xa0+', ' ', text, flags=re.UNICODE)
        text = re.sub(r'\s\s+', ' ', text)
        return text


class InterventionScraper(Scraper):
    def __init__(self, html, issue, entities):
        super().__init__(html, issue, entities)
        self.word_tokenizer = WordTokenizer(entities)

    def _scrape_from_sentence(self, sentence):
        """Extracts a list of interventions from a sentence."""
        tokens = set(self.word_tokenizer.tokenize(sentence))
        matches = tokens.intersection(self.entities)
        return [
            Intervention(entity, sentence, self.issue) for entity in matches
        ]


class InteractionScraper(Scraper):
    def __init__(self, html, issue, entities):
        super().__init__(html, issue, entities)
        self.pos_tagger = POSTagger(entities)

    def _scrape_from_sentence(self, sentence):
        """Extracts a list of interactions from a sentence."""
        tagged = self.pos_tagger.tag(sentence)
        interactions = list()
        for parser in PARSERS:
            parser = parser(sentence, self.issue)
            interactions.extend(parser.parse(tagged))
        return interactions
