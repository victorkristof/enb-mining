from itertools import chain

import nltk

from .parsers import (AgreementParser, OnBehalfParser, OppositionParser,
                      SupportParser)

ABBREV = set(
    [
        'i.e',
        'e.g',
        'etc',
        'p.m',
        'a.m',
        'kt',  # Kilo-ton
        'cm',
        'unfccc',
        'inf.3',
        'e.v',
        'dept',
        'tel',
    ]
)

PARSERS = [
    OnBehalfParser,
    SupportParser,
    OppositionParser,
    AgreementParser,
]


class SentenceTokenizer:

    """A tokenizer for sentences in a paragraph."""

    def __init__(self):
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentence_tokenizer._params.abbrev_types.update(ABBREV)
        self.tokenizer = sentence_tokenizer

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)

    def debug(self, text):
        for d in self.tokenizer.debug_decisions(text):
            print(nltk.tokenize.punkt.format_debug_decision(d))


class WordTokenizer:

    """A word tokenizer that accounts for multi-word entities (countries,
    agencies, party groupings, etc., such as 'United Kingdom')."""

    def __init__(self, entities):
        """Initializes a tokenizer from a set of entities."""
        # Tokenize multi-word entities to identify them as such (this makes it
        # handle special characters in entity names).
        mwes = list(
            filter(
                lambda mw: len(mw) > 1,
                [nltk.word_tokenize(entity) for entity in entities],
            )
        )
        # Aggregate them using underscore.
        self.tokenizer = nltk.tokenize.MWETokenizer(mwes, separator='_')

    def tokenize(self, text):
        return self.tokenizer.tokenize(nltk.word_tokenize(text))


class InteractionTokenizer:

    """A tokenizer that combines entities and markers of interactions."""

    def __init__(self, entities):
        markers = [mk for parser in PARSERS for mk in parser.markers]
        self.tokenizer = WordTokenizer(list(chain(entities, markers)))

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)


class POSTagger:
    def __init__(self, entities):
        self.tokenizer = InteractionTokenizer(entities)
        self._tag_model = self._init_model(entities)

    @staticmethod
    def _init_model(entities):
        def encode_token(token):
            return '_'.join(nltk.word_tokenize(token))

        # Create tagging model compatible with the multi-word expression
        # tokenizer in WordTokenizer.
        model = {encode_token(entity): 'ENT' for entity in entities}
        model |= {
            encode_token(marker): parser.tag
            for parser in PARSERS
            for marker in parser.markers
        }
        return model

    def _retag_with_model(self, tagged):
        # Assign new tags when they exist, otherwise default to current tag.
        return [(tok, self._tag_model.get(tok, tag)) for tok, tag in tagged]

    def tag(self, sentence):
        tagged = nltk.pos_tag(self.tokenizer.tokenize(sentence))
        return self._retag_with_model(tagged)
