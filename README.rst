========
Pymantic
========
---------------------------------------
Semantic Web and RDF library for Python
---------------------------------------


Quick Start
===========

.. code-block :: python
    
    >>> import pymantic
    >>> resource = Resource.in_graph(graph, 'http://example.com/resource')


Requirements
============

Pymantic requires Python 2.5 or higher. rdflib is currently used to provide RDF primitives, only rdflib 2.4.x versions are supported.


Install
=======

.. code-block :: bash

    $ python setup.py install

This will install Pymantic and all its dependencies.


Documentation
=============

Generating a local copy of the documentation requires Sphinx:

.. code-block :: bash
    $ easy_install Sphinx


