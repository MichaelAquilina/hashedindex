# -*- encoding: utf8 -*-
from __future__ import absolute_import, division, print_function

import collections
import json
import unittest

import hashedindex


def unordered_list_cmp(list1, list2):
    # Check lengths first for slight improvement in performance
    return len(list1) == len(list2) and sorted(list1) == sorted(list2)


class HashedIndexTest(unittest.TestCase):
    # Note that generate_document_vector and generate_feature_matrix tests
    # are considered interrelated and test cases are therefore not repeated
    # between them where possible.

    def setUp(self):
        self.index = hashedindex.HashedIndex()

        for i in range(3):
            self.index.add_term_occurrence('word', 'document1.txt')

        for i in range(5):
            self.index.add_term_occurrence('malta', 'document1.txt')

        for i in range(4):
            self.index.add_term_occurrence('phone', 'document2.txt')

        for i in range(2):
            self.index.add_term_occurrence('word', 'document2.txt')

    def test_get_documents(self):
        assert self.index.get_documents('word') == collections.Counter(
            {'document1.txt': 3, 'document2.txt': 2}
        )
        assert self.index.get_documents('malta') == collections.Counter({'document1.txt': 5})
        assert self.index.get_documents('phone') == collections.Counter({'document2.txt': 4})

        assert unordered_list_cmp(self.index.documents(), ['document1.txt', 'document2.txt'])

        self.index.add_term_occurrence('test', 'document3.txt')
        assert unordered_list_cmp(
            self.index.documents(), ['document1.txt', 'document2.txt', 'document3.txt']
        )

        assert 'doesnotexist.txt' not in self.index.documents()

    def test_hashedindex_constructor_with_terms(self):
        index2 = hashedindex.HashedIndex(self.index.terms())

        # Terms between the two indexes should be equal
        assert unordered_list_cmp(index2.terms(), self.index.terms())

        # No documents should be found
        assert index2.documents() == []

        # All terms should have no referenced documents
        for term in index2.terms():
            assert index2[term] == {}

        index2.add_term_occurrence('phone', 'mydoc.doc')
        assert index2.get_term_frequency('phone', 'mydoc.doc') == 1

    def test_case_sensitive_documents(self):
        self.index.add_term_occurrence('word', 'Document2.txt')

        assert self.index.get_term_frequency('word', 'document2.txt') == 2
        assert self.index.get_term_frequency('word', 'Document2.txt') == 1

        assert unordered_list_cmp(
            self.index.documents(), ['document1.txt', 'document2.txt', 'Document2.txt']
        )

    def test_getitem(self):
        assert unordered_list_cmp(self.index['word'].keys(), ['document1.txt', 'document2.txt'])
        assert unordered_list_cmp(self.index['malta'].keys(), ['document1.txt'])
        assert unordered_list_cmp(self.index['phone'].keys(), ['document2.txt'])

    def test_getitem_raises_keyerror(self):
        # Trying to get a term that does not exist should raise a key error
        self.assertRaises(KeyError, self.index.__getitem__, 'doesnotexist')

        # Case Insensitive check
        self.assertRaises(KeyError, self.index.__getitem__, 'wORd')

    def test_contains(self):
        assert 'word' in self.index
        assert 'malta' in self.index
        assert 'phone' in self.index

        # Case Insensitive Check
        assert 'WoRd' not in self.index

        # Non-Existent check
        assert 'doesnotexist' not in self.index

    def test_clear(self):
        self.index.clear()

        assert self.index.terms() == []
        assert self.index.documents() == []

    def test_freeze_unfreeze(self):
        self.index.freeze()
        self.index.add_term_occurrence('myword', 'document2.txt')

        # New words should be not added
        assert 'myword' not in self.index

        # Adding words that exist should work though
        assert self.index.get_term_frequency('word', 'document1.txt') == 3

        # Ensure documents are still added even if its term is not
        self.index.add_term_occurrence('idonotexist', 'document20.txt')
        assert 'document20.txt' in self.index.documents()

        self.index.add_term_occurrence('phone', 'document9.txt')
        self.index.add_term_occurrence('word', 'document1.txt')

        assert self.index.get_term_frequency('word', 'document1.txt') == 4
        assert self.index.get_term_frequency('phone', 'document9.txt') == 1

        # Terms should be add-able
        self.index.unfreeze()
        self.index.add_term_occurrence('myword', 'document2.txt')
        assert 'myword' in self.index

    def test_get_total_term_frequency(self):
        assert self.index.get_total_term_frequency('word') == 5
        assert self.index.get_total_term_frequency('malta') == 5
        assert self.index.get_total_term_frequency('phone') == 4

    def test_get_total_term_frequency_exceptions(self):
        self.assertRaises(IndexError, self.index.get_total_term_frequency, 'doesnotexist')

    def test_get_total_term_frequency_case(self):
        self.assertRaises(IndexError, self.index.get_total_term_frequency, 'WORD')
        self.assertRaises(IndexError, self.index.get_total_term_frequency, 'Malta')
        self.assertRaises(IndexError, self.index.get_total_term_frequency, 'phonE')

    def test_get_term_frequency(self):
        # Check Existing cases
        assert self.index.get_term_frequency('word', 'document1.txt') == 3
        assert self.index.get_term_frequency('malta', 'document1.txt') == 5
        assert self.index.get_term_frequency('phone', 'document2.txt') == 4
        assert self.index.get_term_frequency('word', 'document2.txt') == 2

        # Check non existing cases
        assert self.index.get_term_frequency('malta', 'document2.txt') == 0
        assert self.index.get_term_frequency('phone', 'document1.txt') == 0

    def test_get_term_frequency_exceptions(self):
        self.assertRaises(
            IndexError, self.index.get_term_frequency, 'doesnotexist', 'document1.txt'
        )
        self.assertRaises(IndexError, self.index.get_term_frequency, 'malta', 'deoesnotexist.txt')

    def test_get_document_frequency(self):
        assert self.index.get_document_frequency('word') == 2
        assert self.index.get_document_frequency('malta') == 1
        assert self.index.get_document_frequency('phone') == 1

    def test_get_document_frequency_exceptions(self):
        self.assertRaises(IndexError, self.index.get_document_frequency, 'doesnotexist')

    def test_get_document_length(self):
        assert self.index.get_document_length('document1.txt') == 8
        assert self.index.get_document_length('document2.txt') == 6

    def test_get_document_length_exceptions(self):
        self.assertRaises(IndexError, self.index.get_document_length, 'doesnotexist.txt')

    def test_get_terms(self):
        assert unordered_list_cmp(self.index.terms(), ['word', 'malta', 'phone'])

        self.index.add_term_occurrence('test', 'document3.txt')
        assert unordered_list_cmp(self.index.terms(), ['word', 'malta', 'phone', 'test'])

        assert 'doesnotexist' not in self.index.terms()

    def test_get_items(self):
        assert self.index.items() == {
            'word': {'document1.txt': 3, 'document2.txt': 2},
            'malta': {'document1.txt': 5},
            'phone': {'document2.txt': 4}
        }

    def test_get_tfidf_relation(self):
        # Test Inverse Document Frequency
        self.assertLess(
            self.index.get_tfidf('word', 'document1.txt'),
            self.index.get_tfidf('malta', 'document1.txt')
        )

    def test_get_tfidf_empty_document(self):
        assert self.index.get_tfidf('malta', 'document2.txt') == 0

    def test_get_tfidf_empty_term(self):
        assert self.index.get_tfidf('phone', 'document1.txt') == 0

    def test_generate_document_vector_default(self):
        self.assertListEqual(
            self.index.generate_document_vector('document1.txt'),
            self.index.generate_document_vector('document1.txt', mode='tfidf'),
        )

    def test_generate_document_vector_custom_function(self):
        def custom_weighting(index, term, document):
            return index.get_document_length(document)

        self.assertListEqual(
            self.index.generate_document_vector('document1.txt', mode=custom_weighting),
            [8, 8, 8],
        )

        def custom_weighting_2(index, term, document):
            return 1.0

        self.assertListEqual(
            self.index.generate_document_vector('document1.txt', mode=custom_weighting_2),
            [1.0, 1.0, 1.0],
        )

    def test_generate_feature_matrix_default(self):
        self.assertListEqual(
            self.index.generate_feature_matrix(),
            self.index.generate_feature_matrix(mode='tfidf'),
        )

    def test_generate_feature_matrix_tfidf(self):
        features = self.index.terms()
        instances = self.index.documents()

        matrix = self.index.generate_feature_matrix(mode='tfidf')

        self.assertEqual(
            matrix[instances.index('document1.txt')][features.index('malta')],
            self.index.get_tfidf('malta', 'document1.txt'),
        )

        self.assertEqual(
            matrix[instances.index('document2.txt')][features.index('word')],
            self.index.get_tfidf('word', 'document2.txt'),
        )

        self.assertEqual(
            matrix[instances.index('document2.txt')][features.index('phone')],
            self.index.get_tfidf('phone', 'document2.txt'),
        )

        self.assertEqual(
            matrix[instances.index('document1.txt')][features.index('word')],
            self.index.get_tfidf('word', 'document1.txt'),
        )

        # Zero Cases
        assert matrix[instances.index('document2.txt')][features.index('malta')] == 0
        assert matrix[instances.index('document1.txt')][features.index('phone')] == 0

    def test_generate_document_vector_count(self):
        features = self.index.terms()
        vector = self.index.generate_document_vector('document1.txt', mode='tf')

        # Correct vector shape
        assert len(vector) == len(features)

        assert vector[features.index('malta')] == 5.0
        assert vector[features.index('word')] == 3.0
        assert vector[features.index('phone')] == 0.0

    def test_generate_feature_matrix_tf(self):
        # Extract the feature and document indices
        features = self.index.terms()
        instances = self.index.documents()

        matrix = self.index.generate_feature_matrix(mode='tf')

        # Correct matrix dimensions
        assert len(matrix) == 2
        for row in matrix:
            assert len(row) == 3

        # Ensure this method of addressing data works
        assert matrix[instances.index('document1.txt')][features.index('malta')] == 5
        assert matrix[instances.index('document2.txt')][features.index('word')] == 2
        assert matrix[instances.index('document1.txt')][features.index('word')] == 3
        assert matrix[instances.index('document2.txt')][features.index('phone')] == 4

        # Zero cases
        assert matrix[instances.index('document2.txt')][features.index('malta')] == 0
        assert matrix[instances.index('document1.txt')][features.index('phone')] == 0

    def test_generate_feature_matrix_ntf(self):
        features = self.index.terms()
        instances = self.index.documents()

        matrix = self.index.generate_feature_matrix(mode='ntf')

        assert matrix[instances.index('document1.txt')][features.index('word')] == 3 / 8
        assert matrix[instances.index('document2.txt')][features.index('phone')] == 4 / 6
        assert matrix[instances.index('document1.txt')][features.index('malta')] == 5 / 8

        assert matrix[instances.index('document2.txt')][features.index('malta')] == 0
        assert matrix[instances.index('document2.txt')][features.index('word')] == 2 / 6

    def test_generate_feature_matrix_invalid(self):
        self.assertRaises(ValueError, self.index.generate_feature_matrix, mode='invalid')
        self.assertRaises(ValueError, self.index.generate_feature_matrix, mode=None)


class SerializationTest(unittest.TestCase):
    def setUp(self):
        self.index = hashedindex.HashedIndex()

        for i in range(3):
            self.index.add_term_occurrence('word', 'document1.txt')

        for i in range(5):
            self.index.add_term_occurrence('malta', 'document1.txt')

        for i in range(4):
            self.index.add_term_occurrence('phone', 'document2.txt')

        for i in range(2):
            self.index.add_term_occurrence('word', 'document2.txt')

    def test_to_dict(self):
        assert self.index.to_dict() == {
            'documents': {'document1.txt': 8, 'document2.txt': 6},
            'terms': {
                'word': {'document1.txt': 3, 'document2.txt': 2},
                'malta': {'document1.txt': 5},
                'phone': {'document2.txt': 4},
            }
        }

    def test_from_dict(self):
        index2 = hashedindex.HashedIndex()
        index2.from_dict({
            'documents': {'a': 2, 'b': 3},
            # Does not test for validity
            'terms': {
                'foo': {'a': 20, 'b': 40},
                'bar': {'a': 65, 'b': 2},
            }
        })

        assert unordered_list_cmp(index2.terms(), ['foo', 'bar'])
        assert unordered_list_cmp(index2.documents(), ['a', 'b'])
        assert index2.get_documents('foo') == collections.Counter({'a': 20, 'b': 40})
        assert index2.get_documents('bar') == collections.Counter({'a': 65, 'b': 2})

    def test_integrity(self):
        index2 = hashedindex.HashedIndex()
        index2.from_dict(self.index.to_dict())

        assert index2 == self.index

    def test_json_seriazable(self):
        assert json.dumps(self.index.to_dict())


class PruneIndexTest(unittest.TestCase):
    def setUp(self):
        self.index = hashedindex.HashedIndex()

        for i in range(100):
            self.index.add_term_occurrence('word', 'document{}.txt'.format(i))

        for i in range(20):
            self.index.add_term_occurrence('text', 'document{}.txt'.format(i))

        self.index.add_term_occurrence('lonely', 'document2.txt')

    def test_min_prune(self):
        self.index.prune(min_value=2)
        assert unordered_list_cmp(self.index.terms(), ['word', 'text'])

        self.index.prune(min_value=25)
        assert unordered_list_cmp(self.index.terms(), ['word'])

    def test_max_prune(self):
        self.index.prune(max_value=20)
        assert unordered_list_cmp(self.index.terms(), ['text', 'lonely'])

    def test_min_prune_percentile(self):
        self.index.prune(min_value=0.25, use_percentile=True)
        assert unordered_list_cmp(self.index.terms(), ['word'])

    def test_max_prune_percentile(self):
        self.index.prune(max_value=0.20, use_percentile=True)
        assert unordered_list_cmp(self.index.terms(), ['text', 'lonely'])


class MergeIndexTest(unittest.TestCase):
    def setUp(self):
        self.first_index = hashedindex.HashedIndex()
        self.first_index.add_term_occurrence('foo', 'document2.txt')
        self.first_index.add_term_occurrence('foo', 'document1.txt')

        self.second_index = hashedindex.HashedIndex()
        self.second_index.add_term_occurrence('foo', 'document1.txt')
        self.second_index.add_term_occurrence('bar', 'document9.txt')

    def test_merge_index_empty(self):
        assert hashedindex.merge([]) == hashedindex.HashedIndex()

    def test_merge_index_single(self):
        assert hashedindex.merge([self.first_index]) == self.first_index

    def test_merge_index(self):
        merged_index = hashedindex.merge([
            self.first_index,
            self.second_index,
        ])

        assert unordered_list_cmp(
            merged_index.terms(),
            ['foo', 'bar']
        )
        assert unordered_list_cmp(
            merged_index.documents(),
            ['document1.txt', 'document2.txt', 'document9.txt']
        )

        assert merged_index._terms['foo'] == {'document1.txt': 2, 'document2.txt': 1}
        assert merged_index._terms['bar'] == {'document9.txt': 1}

        assert merged_index._documents['document1.txt'] == 2
        assert merged_index._documents['document2.txt'] == 1
        assert merged_index._documents['document9.txt'] == 1
