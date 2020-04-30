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

# Permit certain characters within punctuation
_punctuation_exceptions = '\\/-'
_punctuation = copy(punctuation)
_punctuation.strip(_punctuation_exceptions)

_token_class = '[A-z0-9%s]' % re.escape(_punctuation_exceptions)

_re_punctuation = re.compile('[%s]' % _punctuation)
_re_token = re.compile(r'%s+|\s+' % (_token_class))

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


def match_tokens(text, tokenize_whitespace):
    for token in re.findall(_re_token, text):
        if token.strip() or tokenize_whitespace:
            yield token


def get_ngrams(token_list, n=2):
    tokens = iter(token_list)
    try:
        ngram = [next(tokens) for _ in range(0, n)]
        yield ngram
    except StopIteration:
        return

    for token in tokens:
        ngram = ngram[1:]
        ngram.append(token)
        yield ngram


def validate_stemmer(stemmer):
    if not hasattr(stemmer, 'stem'):
        raise InvalidStemmerException('Stemmer is missing a "stem" function')
    if not callable(stemmer.stem):
        raise InvalidStemmerException('Stemmer has a "stem" attribute but it is not a function')


def word_tokenize(text, stopwords=_stopwords, ngrams=None, min_length=0, ignore_numeric=True,
                  stemmer=None, retain_casing=False, tokenize_whitespace=False):
    """
    Parses the given text and yields tokens which represent words within
    the given text. Tokens are assumed to be divided by any form of
    whitespace character.  A stemmer may optionally be provided, which will
    apply a transformation to each token.

    The tokenizer ignores numeric tokens by default; the ignore_numeric
    parameter can be set to False to include them in the output stream.

    Generated tokens are lowercased by default; the retain_casing flag can
    be set to True to retain upper/lower casing from the original text.

    Whitespace tokens are omitted by default; the tokenize_whitespace flag can
    be set to True to include whitespace tokens in the output stream.
    """
    if ngrams is None:
        ngrams = 1
    if stemmer is None:
        stemmer = NullStemmer()

    validate_stemmer(stemmer)

    text = re.sub(re.compile('\'s'), '', text)  # Simple heuristic
    text = re.sub(_re_punctuation, '', text)
    text = text if retain_casing else text.lower()

    matched_tokens = match_tokens(text, tokenize_whitespace)
    for ngram in get_ngrams(matched_tokens, ngrams):
        output_tokens = tuple()
        for token in ngram:
            token = stemmer.stem(token)
            if len(token) < min_length or token in stopwords:
                break
            if ignore_numeric and isnumeric(token):
                break
            output_tokens += (token,)
        else:
            yield output_tokens


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
