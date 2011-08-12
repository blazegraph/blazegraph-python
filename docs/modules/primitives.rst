:mod:`pymantic.primitives`
--------------------------

This module provides a Python implementation of the 
`RDF Interfaces <http://www.w3.org/TR/rdf-interfaces/>`_ defined by the W3C. 
Also extends that API in places to allow for Datasets and Quads. The goal is to 
provide a simple API for working directly with Triples, and RDF Terms. 

.. automodule:: pymantic.primitives
    
    Data Structures
    ===============
    
    .. warning:: Currently Pyamntic does *NOT* restrict data structures to the RDF data model. 
        For example Literals are allowed in the subject and predicate position, seralizing
        these is imposible

    .. autoclass:: Triple

    .. autoclass:: Graph
        :members:
        
    Non-RDF Interfaces Classes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    .. autoclass:: Quad
    
    .. autoclass:: Dataset
        :members:

    RDF Terms
    =========
    
    .. autoclass:: Literal
    
    .. autoclass:: NamedNode
    
    .. autoclass:: BlankNode
        

    RDF Enviroment Interfaces
    =========================
    
    .. autoclass:: RDFEnvironment
        :show-inheritance:
        :members:
        :undoc-members:
    
    .. autoclass:: PrefixMap
        :members:
        
    .. autoclass:: TermMap
        :members:
        
    .. autoclass:: Profile
        :members:
        
    Helper Functions
    ================
    
    .. autofunction:: is_language
    
    .. autofunction:: lang_match
    
    .. autofunction:: parse_curie
    
    .. autofunction:: parse_curies
    
    .. autofunction:: to_curie
        
