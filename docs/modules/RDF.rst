:mod:`pymantic.RDF` -- Modeling RDF as Python Objects
=====================================================

.. automodule:: pymantic.rdf

Functions
---------

.. autofunction:: parse_curie
.. autofunction:: to_curie

Classes
-------
.. autoclass:: Resource
    :members:

Descriptors
-----------

These are used on Resource or ther objects to create python attributes bound to
RDF predicates. The `preicate` argument should be a curie, the prefix used must
be bound to a namespace in the class' namespace attribute.

Example usage::

    class MyResource(rdf.Resource):
        namespaces = {'dc': 'http://purl.org/dc/terms/',}
        
        
