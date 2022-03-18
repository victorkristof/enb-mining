import re

from bs4 import BeautifulSoup, Tag

from .nlp import POSTagger, SentenceTokenizer
from .parsers import (AgreementParser, InterventionParser, OnBehalfParser,
                      OppositionParser, SupportParser)
from .utils import flatten

INTERACTION_PARSERS = [
    OnBehalfParser,
    SupportParser,
    OppositionParser,
    AgreementParser,
]


class Scraper:

    """A general scraper for interventions and interactions."""

    def __init__(self, html, issue, parties, groupings):
        """Initializes the scraper with some HTML, metadata about the ENB
        issue, and a set of Entities."""
        self.soup = BeautifulSoup(html, 'lxml')
        self.issue = issue
        self.parties = parties
        self.groupings = groupings
        self.pos_tagger = POSTagger(
            [party.name for party in parties],
            [group.name for group in groupings],
        )

    def scrape(self):
        # Scraped interventions/interactions (list of list).
        scraped = [
            self._scrape_from_sentence(sentence)
            for sentence in self.extract_sentences()
        ]
        # Flatten this nested list.
        return flatten(scraped)

    def extract_sentences(self):
        content = self.soup.find(
            'section', class_='o-content-from-editor--report'
        )
        paragraphs = self._get_paragraphs(content)
        tokenizer = SentenceTokenizer()
        sentences = list()
        for paragraph in paragraphs:
            text = paragraph.get_text()
            text = self._normalize(text)
            sentences.extend(tokenizer.tokenize(text))

        return sentences

    @staticmethod
    def _get_paragraphs(content):
        """Filters only the paragraphs that are relevant.

        In particular, it removes analysis and opinion sections."""

        def is_opinion_paragraph(node):
            text = node.get_text()
            opinions = [
                'BRIEF ANALYSIS OF',
                'THINGS TO LOOK FOR',
                'IN THE CORRIDORS',
                'This issue of the Earth Negotiations Bulletin',
            ]
            return any([opinion in text for opinion in opinions])

        paragraphs = list()
        for node in content.children:
            if type(node) == Tag:
                # We stop as soon as we see an opinion paragraph.
                if is_opinion_paragraph(node):
                    return paragraphs
                # Keep only <p> tags.
                elif node.name == 'p':
                    paragraphs.append(node)
        return paragraphs

    def _normalize(self, text):
        """Normalizes a sentence before it gets tokenized.

        This improves the format of the sentence, so it can be saved as is."""
        # Rename a.m./p.m. as am/pm.
        text = re.sub(r'a\.m\.', r'am', text)
        text = re.sub(r'p\.m\.', r'pm', text)
        # Add spacing for "andParty" -> "and Party".
        text = re.sub(r'(and)([A-Z])', r'\1 \2', text)
        text = re.sub(r'77and', r'77 and', text)
        # Add spacing before parenthesis.
        text = 'France(on behalf)'
        text = re.sub(r'(\w)\(', r'\1 (', text)
        # Normalize spaces.
        text = re.sub(r'\r', ' ', text)
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'\xa0+', ' ', text, flags=re.UNICODE)
        text = re.sub(r'\s\s+', ' ', text)
        return text

    def _preprocess(self, text):
        """Prepocesses a sentence before it gets tagged.

        This changes the sentence, so it should not be saved in this format."""
        # Remove exclamation marks from names (for sentence tokenizer).
        text = re.sub(r'(Climate Justice Now)!', r'\1', text)
        text = re.sub(r'(CLIMATE JUSTICE NOW)!', r'\1', text)
        text = re.sub(r'(CJN)!', r'\1', text)
        text = re.sub(r'(ACT)!', r'\1', text)
        # Normalize US$ to prevent parsing interventions for US.
        text = re.sub(r'US\$', '$', text)
        # Normalize QELROS so that it's not matched as a city.
        text = re.sub(r'QELRO[Ss]', 'qelros', text)
        return text


class InterventionScraper(Scraper):
    def __init__(self, html, issue, parties, groupings):
        super().__init__(html, issue, parties, groupings)

    def _scrape_from_sentence(self, sentence):
        """Extracts a list of interventions from a sentence."""
        parser = InterventionParser(
            sentence, self.issue, self.parties, self.groupings
        )
        tagged = self.pos_tagger.tag(self._preprocess(sentence))
        return parser.parse(tagged)


class InteractionScraper(Scraper):
    def __init__(self, html, issue, parties, groupings):
        super().__init__(html, issue, parties, groupings)

    def _scrape_from_sentence(self, sentence):
        """Extracts a list of interactions from a sentence."""
        tagged = self.pos_tagger.tag(self._preprocess(sentence))
        interactions = list()
        for Parser in INTERACTION_PARSERS:
            parser = Parser(sentence, self.issue, self.parties, self.groupings)
            interactions.extend(parser.parse(tagged))
        return interactions
