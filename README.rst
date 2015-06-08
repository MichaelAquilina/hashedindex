===============================
hashedindex
===============================

.. image:: https://img.shields.io/travis/MichaelAquilina/hashedindex.svg
        :target: https://travis-ci.org/MichaelAquilina/hashedindex

.. image:: https://img.shields.io/pypi/v/hashedindex.svg
        :target: https://pypi.python.org/pypi/hashedindex


Fast and simple InvertedIndex implementation using hash lists (python dictionaries).

* Free software: BSD license
* Documentation: https://hashedindex.readthedocs.org.

Features
--------

hashedindex provides a simple to use inverted index structure that is flexible enough to work with all kinds of use cases.

Basic Usage:

.. code-block:: python

    import hashedindex
    index = hashedindex.HashedIndex()
        
    index.add_term_occurrence('hello', 'document1.txt')
    index.add_term_occurrence('world', 'document1.txt')
        
    index.get_documents('hello')
     
    Counter({'document1.txt': 1})
        
    index.items()
    {'hello': Counter({'document1.txt': 1}),
    'world': Counter({'document1.txt': 1})}

    example = 'The Quick Brown Fox Jumps Over The Lazy Dog'

    for term in example.split():
        index.add_term_occurrence(term, 'document2.txt')

The hashedindex is not limited to strings, any hashable object can be indexed.

.. code-block:: python

   index.add_term_occurrence('foo', 10)
   index.add_term_occurrence(('fire', 'fox'), 90.2)

   index.items()
   {'foo': Counter({10: 1}), ('fire', 'fox'): Counter({90.2: 1})}

All methods within the code have high test coverage so you can be sure everything works as expected. Found a bug? Nice, a bug found is a bug fixed. Open an Issue or better yet, open a pull request.
