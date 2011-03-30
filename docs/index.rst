.. _index:

********
Pymantic
********

Pymantic is a pythonic and easy-to-use library for working with `Resource Description Framework (RDF) <http://www.w3.org/RDF/>`_ data.

Examples
========


Reading RDF data in N-Triples
-----------------------------
.. doctest::

    from pymantic.parsers import *
    
    with open("triples.nt") as f:
        graph = parse_ntriples(f)


.. _getting_involved:

Getting Involved
================


GitHub project page
-------------------

Fork it, add features, wallow in the code, find out what is being worked on

`github.com/norcalrdf/pymantic <https://github.com/norcalrdf/pymantic>`_.

Feedback (Bugs)
---------------

Submit bugs in our `issue tracker <https://github.com/norcalrdf/pymantic/issues>`_.

Discuss
-------

* `pymantic users mailing list <http://groups.google.com/group/pymantic-users>`_.
* `pymantic development mailing list <http://groups.google.com/group/pymantic-developers>`_.
