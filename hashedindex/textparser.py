import re
import math
import unicodedata

from copy import copy
from string import ascii_letters, digits, punctuation


# Stemmer interface which returns token unchanged
class NullStemmer:

    def stem(self, x):
        return x

    def __repr__(self):
        return '<NullStemmer>'


class InvalidStemmerException(Exception):
    pass


_stopwords = frozenset()
_accepted = frozenset(ascii_letters + digits + punctuation) - frozenset('\'')

_punctuation = copy(punctuation)
_punctuation = _punctuation.replace('\\', '')
_punctuation = _punctuation.replace('/', '')
_punctuation = _punctuation.replace('-', '')
_punctuation_class = '[%s]' % re.escape(_punctuation)

_re_punctuation = re.compile(_punctuation_class)
_re_token = re.compile(r'[A-z0-9]+|%s' % _punctuation_class)

_url_pattern = (
    r'(https?:\/\/)?(([\da-z-]+)\.){1,2}.([a-z\.]{2,6})(/[\/\w \.-]*)*\/?(\?(\w+=\w+&?)+)?'
)
_re_full_url = re.compile(r'^%s$' % _url_pattern)
_re_url = re.compile(_url_pattern)


# Determining the best way to calculate tfidf is proving difficult,
# might need more advanced techniques
def tfidf(tf, df, corpus_size):
    if df and tf:
        return (1 + math.log(tf)) * math.log(corpus_size / df)
    else:
        return 0.0


def normalize_unicode(text):
    """
    Normalize any unicode characters to ascii equivalent
    https://docs.python.org/2/library/unicodedata.html#unicodedata.normalize
    """
    if isinstance(text, str):
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf8')
    else:
        return text


def get_ngrams(token_list, n=2):
    for i in range(len(token_list) - n + 1):
        yield token_list[i:i+n]


def validate_stemmer(stemmer):
    if not hasattr(stemmer, 'stem'):
        raise InvalidStemmerException('Stemmer is missing a "stem" function')
    if not callable(stemmer.stem):
        raise InvalidStemmerException('Stemmer has a "stem" attribute but it is not a function')


def word_tokenize(text, stopwords=_stopwords, ngrams=None, min_length=0, ignore_numeric=True,
                  stemmer=None, retain_casing=False, retain_punctuation=False):
    """
    Parses the given text and yields tokens which represent words within
    the given text. Tokens are assumed to be divided by any form of
    whitespace character.  A stemmer may optionally be provided, which will
    apply a transformation to each token.

    The tokenizer ignores numeric tokens by default; the ignore_numeric
    parameter can be set to False to include them in the output stream.

    Generated tokens are lowercased by default; the retain_casing flag can
    be set to True to retain upper/lower casing from the original text.

    Unless retain_punctuation is set to True, punctuation characters will be
    dropped from the output stream.
    """
    if ngrams is None:
        ngrams = 1
    if stemmer is None:
        stemmer = NullStemmer()

    validate_stemmer(stemmer)

    text = re.sub(re.compile('\'s'), '', text)  # Simple heuristic
    text = text if retain_punctuation else re.sub(_re_punctuation, '', text)
    text = text if retain_casing else text.lower()

    matched_tokens = re.findall(_re_token, text)
    for tokens in get_ngrams(matched_tokens, ngrams):
        for i in range(len(tokens)):
            if not retain_punctuation:
                tokens[i] = tokens[i].strip(punctuation)
            tokens[i] = stemmer.stem(tokens[i])

            if len(tokens[i]) < min_length or tokens[i] in stopwords:
                break
            if ignore_numeric and isnumeric(tokens[i]):
                break
        else:
            yield tuple(tokens)


def isnumeric(text):
    """
    Returns a True if the text is purely numeric and False otherwise.
    """
    try:
        float(text)
    except ValueError:
        return False
    else:
        return True


def is_url(text):
    """
    Returns a True if the text is a url and False otherwise.
    """
    return bool(_re_full_url.match(text))
