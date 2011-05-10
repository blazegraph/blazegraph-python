import sys, os

try:
    import Cython
except ImportError:
    pass

from setuptools import setup

from pymantic import version

import setupinfo

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
          'lepl'
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts = [
          'pymantic/scripts/named_graph_to_nquads',
      ],
      ext_modules = setupinfo.ext_modules(),
      **setupinfo.extra_setup_args()
)
