# -*- encoding: utf8 -*-
from __future__ import unicode_literals, print_function, division

import re
import math
import unicodedata

from copy import copy
from string import ascii_letters, digits, punctuation

import six


# Stemmer interface which returns token unchanged
class NullStemmer(object):

    def stem(self, x):
        return x

    def __str__(self):
        return '<NullStemmer>'


_stopwords = frozenset()
_accepted = frozenset(ascii_letters + digits + punctuation) - frozenset('\'')

_punctuation = copy(punctuation)
_punctuation = _punctuation.replace('\\', '')
_punctuation = _punctuation.replace('/', '')
_punctuation = _punctuation.replace('-', '')

_re_punctuation = re.compile('[%s]' % re.escape(_punctuation))
_re_token = re.compile(r'[a-z0-9]+')

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
        return 0


def normalize_unicode(text):
    """
    Normalize any unicode characters to ascii equivalent
    https://docs.python.org/2/library/unicodedata.html#unicodedata.normalize
    """
    if isinstance(text, six.text_type):
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    else:
        return text


def get_ngrams(token_list, n=2):
    for i in range(len(token_list) - n + 1):
        yield token_list[i:i+n]


def word_tokenize(text, stopwords=_stopwords, ngrams=None, min_length=0, ignore_numeric=True):
    """
    Parses the given text and yields tokens which represent words within
    the given text. Tokens are assumed to be divided by any form of
    whitespace character.
    """
    if ngrams is None:
        ngrams = 1

    text = re.sub(re.compile('\'s'), '', text)  # Simple heuristic
    text = re.sub(_re_punctuation, '', text)

    matched_tokens = re.findall(_re_token, text.lower())
    for tokens in get_ngrams(matched_tokens, ngrams):
        for i in range(len(tokens)):
            tokens[i] = tokens[i].strip(punctuation)

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
