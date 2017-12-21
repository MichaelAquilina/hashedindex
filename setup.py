#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
]

test_requirements = [
    'wheel>=0.23.0',
    'pytest>=2.7.1',
    'tox>=2.0.1',
]

setup(
    name='hashedindex',
    version='0.4.1',
    description="InvertedIndex implementation using hash lists (dictionaries)",
    long_description=readme + '\n\n' + history,
    author="Michael Aquilina",
    author_email='michaelaquilina@gmail.com',
    url='https://github.com/MichaelAquilina/hashedindex',
    packages=[
        'hashedindex',
    ],
    package_dir={'hashedindex':
                 'hashedindex'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='hashedindex',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
