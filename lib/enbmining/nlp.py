import string
from itertools import chain

import nltk

from .interactions import OnBehalf

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

INTERACTIONS = [
    OnBehalf,
    # ('spoke', 'with'),
    # ('spoke', 'with', 'the'),
    # ('concerns', 'of'),
    # ('concerns', 'of', 'the'),
    # ('supported', 'by'),
    # ('supported', 'by', 'the'),
    # ('opposed', 'by'),
    # ('opposed', 'by', 'the'),
    # ('proposed', 'by'),
    # ('proposed', 'by', 'the'),
]


class SentenceTokenizer:
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

    """A tokenizer that accounts for multi-word entities (countries, agencies,
    party groupings, etc., such as 'United Kingdom')."""

    def __init__(self, entities):
        """Initializes a tokenizer from a set of entities."""
        mwes = filter(
            lambda mw: len(mw) > 1, [entity.split() for entity in entities]
        )
        self.tokenizer = nltk.tokenize.MWETokenizer(list(mwes), separator=' ')

    def tokenize(self, text):
        tokens = self.tokenizer.tokenize(nltk.word_tokenize(text))
        # Remove punctuation from sentences.
        return list(filter(lambda tk: tk not in string.punctuation, tokens))


class InteractionTokenizer:

    """A tokenizer that combines entities and words related to interactions."""

    def __init__(self, entities):
        tokens = [
            tk for interaction in INTERACTIONS for tk in interaction.tokens
        ]
        entities = list(chain(entities, tokens))
        self.tokenizer = WordTokenizer(entities)

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)


class POSTagger:
    def __init__(self, entities):
        self.tokenizer = InteractionTokenizer(entities)
        self._tag_model = self._init_model(entities)

    @staticmethod
    def _init_model(entities):
        model = dict()
        for entity in entities:
            model[entity] = 'ENT'
        for interaction in INTERACTIONS:
            for token in interaction.tokens:
                model[token] = interaction.tag
        return model

    def _retag_with_model(self, tagged):
        new_tagged = list()
        for tok, tag in tagged:
            new_tag = self._tag_model.get(tok)
            if new_tag is None:
                new_tagged.append((tok, tag))
            else:
                new_tagged.append((tok, new_tag))
        return new_tagged

    def tag(self, sentence):
        tagged = nltk.pos_tag(self.tokenizer.tokenize(sentence))
        return self._retag_with_model(tagged)
