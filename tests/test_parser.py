import unittest

from hashedindex import textparser


class TfidfTestCase(unittest.TestCase):

    def test_zero_term_frequency(self):
        assert textparser.tfidf(tf=0, df=10, corpus_size=1) == 0

    def test_zero_document_frequency(self):
        assert textparser.tfidf(tf=10, df=0, corpus_size=1) == 0


class ValidateStemmerTestCase(unittest.TestCase):

    class EmptyStemmer(object):

        def stem(self, x):
            return ''

    def test_null_stemmer(self):
        stemmer = textparser.NullStemmer()
        textparser.validate_stemmer(stemmer)

    def test_empty_stemmer(self):
        stemmer = self.EmptyStemmer()
        textparser.validate_stemmer(stemmer)

    def test_stemmer_constant(self):
        kwargs = {'stemmer': 'string'}
        exception = textparser.InvalidStemmerException
        self.assertRaises(exception, textparser.validate_stemmer, **kwargs)

    def test_stemmer_function(self):
        kwargs = {'stemmer': lambda: None}
        exception = textparser.InvalidStemmerException
        self.assertRaises(exception, textparser.validate_stemmer, **kwargs)

    def test_stemmer_missing_stem_attribute(self):
        kwargs = {'stemmer': object()}
        exception = textparser.InvalidStemmerException
        self.assertRaises(exception, textparser.validate_stemmer, **kwargs)

    def test_stemmer_stem_not_callable(self):
        stemmer = type('', (object,), {'stem': None})()
        kwargs = {'stemmer': stemmer}
        exception = textparser.InvalidStemmerException
        self.assertRaises(exception, textparser.validate_stemmer, **kwargs)


class IsNumericTestCase(unittest.TestCase):

    def test_integer(self):
        assert textparser.isnumeric('23')
        assert textparser.isnumeric('8431')

    def test_float(self):
        assert textparser.isnumeric('23.480')
        assert textparser.isnumeric('9.6502')

    def test_scientific_notation(self):
        assert textparser.isnumeric('1e-10')
        assert textparser.isnumeric('2e+54')

    def test_no_numeric(self):
        assert not textparser.isnumeric('foo')
        assert not textparser.isnumeric('10 foo')


class GetNGramsTestCase(unittest.TestCase):

    def test_bigram_token_list(self):
        assert list(textparser.get_ngrams(
            token_list=['one', 'two', 'three', 'four'],
        )) == [['one', 'two'], ['two', 'three'], ['three', 'four']]

    def test_trigram_token_list(self):
        assert list(textparser.get_ngrams(
            token_list=['one', 'two', 'three', 'four'],
            n=3,
        )) == [
            ['one', 'two', 'three'],
            ['two', 'three', 'four'],
        ]


class WordTokenizeTestCase(unittest.TestCase):

    class NaivePluralStemmer(object):

        def stem(self, x):
            return x.rstrip('s')

    def test_sentence(self):
        assert list(textparser.word_tokenize(
            text='Life is about making an impact, not making an income.',
        )) == [
            ('life', ), ('is', ), ('about', ),
            ('making', ), ('an', ), ('impact', ),
            ('not', ), ('making', ), ('an', ),
            ('income', )
        ]

    def test_strips_punctuation(self):
        assert list(textparser.word_tokenize(
            text='first. second',
        )) == [('first', ), ('second', )]

    def test_inner_punctuation(self):
        assert list(textparser.word_tokenize(
            text='decision is a and/or b',
        )) == [('decision',), ('is',), ('a',), ('and/or',), ('b',)]

    def test_ignores_stopwords(self):
        assert list(textparser.word_tokenize(
            text='The first rule of python is',
            stopwords=set(['the', 'of', 'is']),
            min_length=1,
        )) == [('first', ), ('rule', ), ('python', )]

    def test_min_length(self):
        assert list(textparser.word_tokenize(
            text='one for the money two for the go',
            min_length=4,
        )) == [('money', )]

    def test_ignores_numeric(self):
        assert list(textparser.word_tokenize(
            text='one two 3 four',
        )) == [('one', ), ('two', ), ('four', )]

    def test_retains_casing(self):
        assert list(textparser.word_tokenize(
            text='Three letter acronym (TLA)',
            retain_casing=True
        )) == [('Three', ), ('letter', ), ('acronym', ), ('TLA',)]

    def test_retains_punctuation(self):
        assert list(textparser.word_tokenize(
            text='who, where? (question!)',
            retain_punctuation=True
        )) == [('who', ), (',', ), ('where',), ('?', ), ('(',), ('question',), ('!',), (')',)]

    def test_retains_punctuation_within_tokens(self):
        assert list(textparser.word_tokenize(
            text='is the oven pre-heated?',
            retain_punctuation=True
        )) == [('is', ), ('the', ), ('oven',), ('pre-heated', ), ('?',)]

    def test_retain_unicode_within_tokens(self):
        assert list(textparser.word_tokenize('québec')) == [('québec',)]

    def test_ngrams(self):
        assert list(textparser.word_tokenize(
            text='foo bar bomb blar',
            ngrams=2,
        )) == [('foo', 'bar'), ('bar', 'bomb'), ('bomb', 'blar')]

    def test_ngram_unsatisfiable(self):
        assert list(textparser.word_tokenize(
            text='foo bar',
            ngrams=3,
        )) == []

    def test_stemming(self):
        assert list(textparser.word_tokenize(
            text='one examples',
            stemmer=self.NaivePluralStemmer()
        )) == [('one',), ('example',)]

    def test_tokenize_whitespace(self):
        assert list(textparser.word_tokenize(
            text='around   the world',
            tokenize_whitespace=True
        )) == [('around',), ('   ',), ('the',), (' ',), ('world', )]

    def test_tokenize_punctuation_and_whitespace(self):
        assert list(textparser.word_tokenize(
            text='who, where, what, when, why?',
            retain_punctuation=True,
            tokenize_whitespace=True
        )) == [
            ('who',), (',',), (' ',),
            ('where',), (',',), (' ',),
            ('what',), (',',), (' ',),
            ('when',), (',',), (' ',),
            ('why',), ('?',),
        ]


class TestNullStemmer(unittest.TestCase):
    def test_repr(self):
        stemmer = textparser.NullStemmer()
        assert str(stemmer) == repr(stemmer) == '<NullStemmer>'

    def test_stem(self0):
        stemmer = textparser.NullStemmer()
        assert stemmer.stem('hello  ') == 'hello  '


class IsUrlTestCase(unittest.TestCase):

    def test_http_url(self):
        assert textparser.is_url('http://www.google.com')

    def test_https_url(self):
        assert textparser.is_url('https://www.google.com')

    def test_url_with_path(self):
        assert textparser.is_url('https://www.facebook.com/some/path/here')

    def test_url_with_query_string(self):
        assert textparser.is_url('https://www.yplanapp.com?foo=1&bar=2')

    def test_not_a_url(self):
        assert not textparser.is_url('foo')
        assert not textparser.is_url('bar')
        assert not textparser.is_url('waterboat')
