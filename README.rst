========
Pymantic
========
---------------------------------------
Semantic Web and RDF library for Python
---------------------------------------


Quick Start
===========
:: 

    >>> import pymantic
    >>> resource = Resource.in_graph(graph, 'http://example.com/resource')


Requirements
============

Pymantic requires Python 2.5 or higher. rdflib is currently used to provide RDF
primitives, only rdflib 2.4.x versions are supported. httplib2 is used for HTTP 
requests and the SPARQL client. lxml is required by the SPARQL client as well.


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


