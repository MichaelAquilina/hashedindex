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

test_requirements = [
    'wheel',
    'pytest',
]

setup(
    name='hashedindex',
    version='0.6.0',
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
    license="BSD",
    zip_safe=False,
    keywords='hashedindex',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests',
    setup_requires=['pytest-runner'],
    tests_require=test_requirements
)
