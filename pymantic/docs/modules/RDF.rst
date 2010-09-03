:mod:`pymantic.RDF` -- Modeling RDF as Python Objects
=====================================================

.. automodule:: pymantic.RDF

Functions
---------

.. autofunction:: en
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

    class MyResource(RDF.Resource):
        namespaces = {'dc': 'http://purl.org/dc/terms/',}
        title = RDF.ScalarPredicateProperty('dc:title', 
                                             docstring="""The title of my resource""")

.. autoclass:: PredicateProperty
    :members:

.. autoclass:: ScalarPredicateProperty
    :members:

.. autoclass:: ResourcePredicateProperty
    :members:

.. autoclass:: ScalarResourcePredicateProperty
    :members:

.. autoclass:: ResourceReversePredicateProperty
    :members:

.. autoclass:: SelfReferentialPredicateProperty
    :members:

.. autoclass:: ScalarSelfReferentialPredicateProperty
    :members:

.. autoclass:: InverseFunctionalLookupProperty
    :members:
