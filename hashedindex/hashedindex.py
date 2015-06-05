from __future__ import division

import collections
import datetime
from math import log10

import numpy as np
import pandas as pd


DOCUMENT_DOES_NOT_EXIST = 'The specified document does not exist'
TERM_DOES_NOT_EXIST = 'The specified term does not exist'


class HashedIndex(object):
    """
    InvertedIndex structure in the form of a hash list implementation.
    """

    def __init__(self, initial_terms=None):
        """
        Construct a new HashedIndex. An optional list of initial terms
        may be passed which will be automatically added to the new HashedIndex.
        """
        self._documents = collections.Counter()
        self._terms = {}
        self._freeze = False
        if initial_terms is not None:
            for term in initial_terms:
                self._terms[term] = {}

    def __getitem__(self, term):
        return self._terms[term]

    def __contains__(self, term):
        return term in self._terms

    def __repr__(self):
        return '<HashedIndex: {} terms, {} documents>'.format(
            len(self._terms), len(self._documents)
        )

    def __eq__(self, other):
        return self._terms == other._terms and self._documents == other._documents

    def clear(self):
        """
        Resets the HashedIndex to a clean state without any terms or documents.
        """
        self._terms = {}
        self._documents = collections.Counter()

    def freeze(self):
        """
        Freezes the HashedIndex, preventing any new terms from being added
        when calling add_term_occurrence.
        """
        self._freeze = True

    def unfreeze(self):
        """
        Unfreezes (thaws) the HashedIndex, allowing new terms to be added
        when calling add_term_occurrence.
        """
        self._freeze = False

    def add_term_occurrence(self, term, document):
        """
        Adds an occurrence of the term in the specified document.
        """
        if document not in self._documents:
            self._documents[document] = 0

        if term not in self._terms:
            if self._freeze:
                return
            else:
                self._terms[term] = collections.Counter()

        if document not in self._terms[term]:
            self._terms[term][document] = 0

        self._documents[document] += 1
        self._terms[term][document] += 1

    def get_total_term_frequency(self, term):
        """
        Gets the frequency of the specified term in the entire corpus
        added to the HashedIndex.
        """
        if term not in self._terms:
            raise IndexError(TERM_DOES_NOT_EXIST)

        return sum(self._terms[term].values())

    def get_term_frequency(self, term, document):
        """
        Returns the frequency of the term specified in the document.
        """
        if document not in self._documents:
            raise IndexError(DOCUMENT_DOES_NOT_EXIST)

        if term not in self._terms:
            raise IndexError(TERM_DOES_NOT_EXIST)

        if document not in self._terms[term]:
            return 0

        return self._terms[term][document]

    def get_document_frequency(self, term):
        """
        Returns the number of documents the specified term appears in.
        """
        if term not in self._terms:
            raise IndexError(TERM_DOES_NOT_EXIST)
        else:
            return len(self._terms[term])

    def get_document_length(self, document):
        """
        Returns the number of terms found within the specified document.
        """
        if document in self._documents:
            return self._documents[document]
        else:
            raise IndexError(DOCUMENT_DOES_NOT_EXIST)

    def terms(self):
        return self._terms.keys()

    def documents(self):
        return list(self._documents)

    def items(self):
        return self._terms

    def get_tfidf(self, term, document):
        """
        Returns the Term-Frequency Inverse-Document-Frequency value for the given
        term in the specified document.
        """
        tf = self.get_term_frequency(term, document)

        # Speeds up performance by avoiding extra calculations
        if tf != 0.0:
            # Add 1 to document frequency to prevent divide by 0
            df = 1 + self.get_document_frequency(term)
            n = 1 + len(self._documents)

            return tf * log10(n / df)
        else:
            return 0.0

    def get_total_tfidf(self, term):
        result = 0
        for document in self._documents:
            result += self.get_tfidf(term, document)
        return result

    def generate_document_vector(self, doc, mode='tfidf'):
        """
        Returns a representation of the specified document as a feature vector
        weighted according the mode specified (by default tf-dif). The result
        will be returned in the form of a numpy ndarray.
        Available modes: tfidif, count, tf
        """
        result = np.zeros(len(self._terms))
        for i, term in enumerate(self._terms):
            if mode == 'tfidf':
                result[i] = self.get_tfidf(term, doc)
            elif mode == 'count':
                result[i] = self.get_term_frequency(term, doc)
            elif mode == 'tf':
                result[i] = self.get_term_frequency(term, doc) / self.get_document_length(doc)
            else:
                raise ValueError('Unexpected mode: %s', mode)

        return result

    def generate_feature_matrix(self, mode='tfidf'):
        """
        Returns a feature numpy matrix representing the terms and
        documents in this Inverted Index using the tf-idf weighting
        scheme by default. The term counts in each document can
        alternatively be used by specifying scheme='count'

        The size of the matrix is equal to m x n where m is
        the number of documents and n is the number of terms.
        """
        result = []

        for i, doc in enumerate(self._documents):
            result.append(self.generate_document_vector(doc, mode))

        return np.asmatrix(result)

    def generate_dataframe(self, mode='tfidf'):
        return pd.DataFrame(
            data=self.generate_feature_matrix(mode),
            columns=self.terms(),
            index=self.documents(),
        )

    def prune(self, min_value=None, max_value=None, use_percentile=False):
        n_documents = len(self._documents)

        for term in self.terms():
            freq = self.get_document_frequency(term)
            if use_percentile:
                freq /= n_documents

            if min_value is not None and freq < min_value:
                del self._terms[term]

            if max_value is not None and freq > max_value:
                del self._terms[term]


    def to_dict(self):
        return {
            'documents': self._documents,
            'terms': self._terms,
        }

    def from_dict(self, data):
        self._documents = data['documents']
        self._terms = data['terms']


def merge(index_list):
    result = HashedIndex()

    for index in index_list:
        first_index = result
        second_index = index

        assert isinstance(second_index, HashedIndex)

        for term in second_index.terms():
            if term in first_index._terms and term in second_index._terms:
                result._terms[term] = first_index._terms[term] + second_index._terms[term]
            elif term in second_index._terms:
                result._terms[term] = second_index._terms[term]
            else:
                raise ValueError("I dont know how the hell you managed to get here")

        result._documents = first_index._documents + second_index._documents

    return result
