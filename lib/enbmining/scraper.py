import re

from bs4 import BeautifulSoup, Tag

from .nlp import POSTagger, SentenceTokenizer
from .parsers import (
    AgreementParser,
    InterventionParser,
    OnBehalfParser,
    OppositionParser,
    SupportParser,
    WhileOppositionParser,
)
from .utils import flatten

INTERACTION_PARSERS = [
    OnBehalfParser,
    SupportParser,
    OppositionParser,
    WhileOppositionParser,
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
        headsentences = self.extract_sentences()
        scraped = [
            self._scrape_from_sentence(sentence, heading)
            for heading, sentences in headsentences.items()
            for sentence in sentences
        ]
        # Flatten this nested list.
        return flatten(scraped)

    # The following function extracts a dictionary of headings-subheadings and sentences,
    # while keeping the current heading and/or subheading until a new one is found.
    def extract_sentences(self):
        content = self.soup.find('section', class_='o-content-from-editor--report')
        paragraphs = self._get_paragraphs(content)
        tokenizer = SentenceTokenizer()
        headsentences = dict()
        current_heading2 = None  # Variable to keep track of the current heading level 2
        current_heading3 = None  # Variable to keep track of the current heading level 3
        current_heading4 = None  # Variable to keep track of the current heading level 4
        current_strong_em = None  # Variable to keep track of the current strong_em
        current_strong = None  # Variable to keep track of the current strong
        current_heading5 = None  # Variable to keep track of the additional headings
        current_subheading = None  # Variable to keep track of the current subheading

        for i, paragraph in enumerate(paragraphs):
            if not isinstance(paragraph, Tag):
                continue  # Skip if the paragraph is not a Tag object
            text = paragraph.get_text()
            text = self._normalize(text)

            # Check for <h2> tags at the correct level
            if paragraph.name in ['h2']:
                current_heading2 = paragraph.get_text().strip().rstrip(':').strip()
                current_heading3 = None   # Reset current_heading3 when a new heading is found
                current_heading4 = None  # Reset current_heading4 when a new heading is found
                current_strong_em = None  # Reset strong_em when a new heading is found
                current_strong = None  # Reset strong when a new heading is found
                current_heading5 = None  # Reset current_heading5 when a new heading is found
                current_subheading = None  # Reset subheading when a new heading is found
                
                # Remove the heading from the text ONLY if it is at the beginning or followed by a colon
                if re.match(rf'^{re.escape(current_heading2)}(:|\s|$)', text):
                    text = text[len(current_heading2):].strip()
            else:
                heading = paragraph.find(['h2'])  # Find heading tagged as <h2> within the paragraph
                if heading:
                    current_heading2 = heading.get_text().strip().rstrip(':').strip()
                    current_heading3 = None   # Reset current_heading3 when a new heading is found
                    current_heading4 = None  # Reset current_heading4 when a new heading is found
                    current_strong_em = None  # Reset strong_em when a new heading is found
                    current_strong = None  # Reset strong when a new heading is found
                    current_heading5 = None  # Reset current_heading4 when a new heading is found
                    current_subheading = None  # Reset subheading when a new heading is found

                    # Remove the heading from the text ONLY if it is at the beginning or followed by a colon
                    if re.match(rf'^{re.escape(current_heading2)}(:|\s|$)', text):
                        text = text[len(current_heading2):].strip()

            # Check for <h3> tags at the correct level
            if paragraph.name in ['h3']:
                current_heading3 = paragraph.get_text().strip().rstrip(':').strip()
                current_heading4 = None  # Reset current_heading4 when a new heading is found
                current_strong_em = None  # Reset strong_em when a new heading is found
                current_strong = None  # Reset strong when a new heading is found
                current_heading5 = None  # Reset current_heading5 when a new heading is found
                current_subheading = None  # Reset subheading when a new heading is found
                
                # Remove the heading from the text ONLY if it is at the beginning or followed by a colon
                if re.match(rf'^{re.escape(current_heading3)}(:|\s|$)', text):
                    text = text[len(current_heading3):].strip()
            else:
                heading = paragraph.find(['h3'])  # Find heading tagged as <h3> within the paragraph
                if heading:
                    current_heading3 = heading.get_text().strip().rstrip(':').strip()
                    current_heading4 = None  # Reset current_heading4 when a new heading is found
                    current_strong_em = None  # Reset strong_em when a new heading is found
                    current_strong = None  # Reset strong when a new heading is found
                    current_heading5 = None  # Reset current_heading5 when a new heading is found
                    current_subheading = None  # Reset subheading when a new heading is found

                    # Remove the heading from the text ONLY if it is at the beginning or followed by a colon
                    if re.match(rf'^{re.escape(current_heading3)}(:|\s|$)', text):
                        text = text[len(current_heading3):].strip()

            # Check for <h4> tags at the correct level
            if paragraph.name in ['h4']:
                current_heading4 = paragraph.get_text().strip().rstrip(':').strip()
                current_strong_em = None  # Reset strong_em when a new heading is found
                current_strong = None  # Reset strong when a new heading is found
                current_heading5 = None  # Reset current_heading5 when a new heading is found
                current_subheading = None  # Reset subheading when a new heading is found
                
                # Remove the heading from the text ONLY if it is at the beginning or followed by a colon
                if re.match(rf'^{re.escape(current_heading4)}(:|\s|$)', text):
                    text = text[len(current_heading4):].strip()
            else:
                heading = paragraph.find(['h4'])  # Find heading tagged as <h4> within the paragraph
                if heading:
                    current_heading4 = heading.get_text().strip().rstrip(':').strip()
                    current_strong_em = None  # Reset strong_em when a new heading is found
                    current_strong = None  # Reset strong when a new heading is found
                    current_heading5 = None  # Reset current_heading5 when a new heading is found
                    current_subheading = None  # Reset subheading when a new heading is found

                    # Remove the heading from the text ONLY if it is at the beginning or followed by a colon
                    if re.match(rf'^{re.escape(current_heading4)}(:|\s|$)', text):
                        text = text[len(current_heading4):].strip()
                    
            strong_em = next((tag for tag in paragraph.find_all(lambda tag: tag.name == 'strong' and tag.find('em'))), None)  # Find <strong> tag containing <em> tag
            if strong_em:
                current_strong_em = strong_em.get_text().strip().rstrip(':').strip()
                current_strong = None  # Reset strong when a new strong_em is found
                current_heading5 = None  # Reset current_heading5 when a new heading is found
                current_subheading = None  # Reset subheading when a new strong_em is found
                
                # Remove the strong_em from the text ONLY if it is at the beginning, followed by a colon, or follows a heading
                if re.match(rf'^{re.escape(current_strong_em)}(:|\s|$)', text):
                    text = text[len(current_strong_em):].strip()
            
            strong = next((tag for tag in paragraph.find_all(lambda tag: tag.name == 'strong' and not tag.find('em'))), None)  # Find <strong> tag not containing <em> tag
            if strong:
                current_strong = strong.get_text().strip().rstrip(':').strip()
                current_heading5 = None  # Reset current_heading5 when a new heading is found
                current_subheading = None  # Reset subheading when a new strong is found
                
                # Remove the strong from the text ONLY if it is at the beginning, followed by a colon, or follows a heading
                if re.match(rf'^{re.escape(current_strong)}(:|\s|$)', text):
                    text = text[len(current_strong):].strip()

            additional_heading = self._additional_heading(paragraph)
            if additional_heading:
                current_heading5 = paragraph.get_text().strip().rstrip(':').strip()
                current_subheading = None  # Reset subheading when a new strong is found

                # Remove the current_heading5 from the text ONLY if it is at the beginning, followed by a colon, or follows a heading
                if re.match(rf'^{re.escape(current_heading5)}(:|\s|$)', text):
                    text = text[len(current_heading5):].strip()
             
            # Check for subheading at the beginning of the paragraph, finishing with a colon but before any full sentence and before any comma
            subheading_match = re.match(r'^[^.,]*?:', text)
            if subheading_match:
                current_subheading = subheading_match.group(0).strip().rstrip(':').strip()  # Extract the subheading and remove any leading or trailing space and trailing colon
                # Do not remove the subheading from the text, because sometimes relevant parts of sentences are captured in the subheading (e.g.: 'The EU said, inter alia: ')
            
            # Concatenate heading, strong_em, strong, and subheading into heading_full with slashes as separators
            unique_components = list(dict.fromkeys(filter(None, [
                current_heading2,
                current_heading3,
                current_heading4,
                current_strong_em,
                current_heading5,
                current_strong,
                current_subheading
            ])))
            heading_full = ' / '.join(unique_components)
            
            if heading_full:
                heading_full = f'Paragraph {i+1}: {heading_full}'  # Prepend the paragraph index to the heading
            else:
                heading_full = f'Paragraph {i+1}'  # Use the paragraph index as the default heading

            # Remove any leading spaces and colons from the text
            text = re.sub(r'^\s*:?', '', text).strip()

            # Tokenize the cleaned text into sentences
            sentences = tokenizer.tokenize(text)
            headsentences[heading_full] = sentences  # Match the heading to the sentences

        return headsentences

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
                'OTHER PRESS BRIEFINGS',
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
        # Add spacing between specific party names and "by" or "and" or a given verb.
        text = re.sub(r'([A-Z][A-Z])(and)', r'\1 \2', text)
        text = re.sub(r'(by)([A-Z])', r'\1 \2', text)
        text = re.sub(r'(AUSTRALIA)(endorsed)', r'\1 \2', text)
        text = re.sub(r'(AUSTRALIA)(said)', r'\1 \2', text)
        text = re.sub(r'(Australia)(said)', r'\1 \2', text)
        text = re.sub(r'(EU)(highlighted)', r'\1 \2', text)
        # Add spacing before parenthesis.
        text = re.sub(r'(\w)\(', r'\1 (', text)
        # Add spacing before dot.
        text = re.sub(r'\.([A-Z])', r'. \1', text)
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
