import nltk

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

    """A tokenizer that accounts for multi-word entities (countries, agencies, party
    groupings, etc., such as 'United Kingdom')."""

    def __init__(self, entities):
        """Initializes a tokenizer from a set of entities."""
        mwes = filter(
            lambda mw: len(mw) > 1, [entity.split() for entity in entities]
        )
        self.tokenizer = nltk.tokenize.MWETokenizer(list(mwes), separator=' ')

    def tokenize(self, text):
        return self.tokenizer.tokenize(nltk.word_tokenize(text))
