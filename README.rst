========
Pymantic
========
---------------------------------------
Semantic Web and RDF library for Python
---------------------------------------


Quick Start
===========
:: 

    >>> from pymantic.rdf import *
    >>> from pymantic.parsers import turtle_parser
    >>> from urllib2 import urlopen
    >>> Resource.prefixes['foaf'] = Prefix('http://xmlns.com/foaf/0.1/')
    >>> graph = turtle_parser.parse(urlopen('https://raw.github.com/norcalrdf/pymantic/master/examples/foaf-bond.ttl'))
    >>> bond_james = Resource(graph, 'http://example.org/stuff/Bond')
    >>> print "%s knows:" % (bond_james.get_scalar('foaf:name'),)
    >>> for person in bond_james['foaf:knows']:
            print person.get_scalar('foaf:name')



Requirements
============

Pymantic requires Python 2.6 or higher. Lepl is used for the Turtle and NTriples parser. httplib2 is used for HTTP 
requests and the SPARQL client. simplejson and lxml are required by the SPARQL client as well.


Install
=======

:: 

    $ python setup.py install

This will install Pymantic and all its dependencies.


Documentation
=============

Generating a local copy of the documentation requires Sphinx:

::

    $ easy_install Sphinx


