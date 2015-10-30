import sys, os

from setuptools import setup

from pymantic import version

setup(name='pymantic',
      version=version,
      description="Semantic Web and RDF library for Python",
      long_description="""""",
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Text Processing :: Markup',
                   ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='RDF N3 Turtle Semantics Web3.0',
      author='Gavin Carothers, Nick Pilon',
      author_email='gavin@carothers.name, npilon@gmail.com',
      url='http://github.com/oreillymedia/pymantic',
      license='BSD',
      packages=['pymantic'],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
          'httplib2',
          'lxml',
          'mock_http',
          'pytz',
          'simplejson',
          'lepl',
          'rdflib'
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts = [
          'pymantic/scripts/named_graph_to_nquads',
          'pymantic/scripts/bnf2html',
      ],
)
