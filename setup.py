from setuptools import setup, find_packages
import sys, os

version = '0.1'

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
      packages=find_packages(exclude=[]),
      include_package_data=True,
      zip_safe=True,
      test_suite='nose.collector',
      install_requires=[
          "rdflib>=3.0.0",
          'httplib2',
          'lxml',
          'mock_http',
          'pytz',
          'simplejson',
          'lepl'
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts = [
          'pymantic/scripts/named_graph_to_nquads',
      ]
      )
