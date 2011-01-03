from cStringIO import StringIO
from nose.tools import *
from pymantic.parsers import *
from pymantic.primitives import *

def test_parse_ntriples_named_nodes():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> <http://example.com/objects/2> .
<http://example.com/objects/2> <http://example.com/predicates/2> <http://example.com/objects/1> .
"""
    g = Graph()
    parse_ntriples(StringIO(test_ntriples), g)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  NamedNode('http://example.com/objects/2')) in g
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  NamedNode('http://example.com/objects/1')) in g

def test_parse_ntriples_bare_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo" .
<http://example.com/objects/2> <http://example.com/predicates/2> "Bar" .
"""
    g = Graph()
    parse_ntriples(StringIO(test_ntriples), g)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  Literal("Foo")) in g
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  Literal("Bar")) in g

def test_parse_ntriples_language_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo"@en-US .
<http://example.com/objects/2> <http://example.com/predicates/2> "Bar"@fr .
"""
    g = Graph()
    parse_ntriples(StringIO(test_ntriples), g)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  Literal("Foo", language='en-US')) in g
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  Literal("Bar", language='fr')) in g

def test_parse_ntriples_datatyped_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo"^^<http://www.w3.org/2001/XMLSchema#string> .
<http://example.com/objects/2> <http://example.com/predicates/2> "9.99"^^<http://www.w3.org/2001/XMLSchema#decimal> .
"""
    g = Graph()
    parse_ntriples(StringIO(test_ntriples), g)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  Literal("Foo", datatype=NamedNode('http://www.w3.org/2001/XMLSchema#string'))) in g
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  Literal("9.99", datatype=NamedNode('http://www.w3.org/2001/XMLSchema#decimal'))) in g

def test_parse_ntriples_mixed_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo"@en-US .
<http://example.com/objects/2> <http://example.com/predicates/2> "9.99"^^<http://www.w3.org/2001/XMLSchema#decimal> .
"""
    g = Graph()
    parse_ntriples(StringIO(test_ntriples), g)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  Literal("Foo", language='en-US')) in g
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  Literal("9.99", datatype=NamedNode('http://www.w3.org/2001/XMLSchema#decimal'))) in g

def test_parse_ntriples_bnodes():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> _:A1 .
_:A1 <http://example.com/predicates/2> <http://example.com/objects/1> .
"""
    g = Graph()
    parse_ntriples(StringIO(test_ntriples), g)
    assert len(g) == 2
    #assert Triple(NamedNode('http://example.com/objects/1'),
                  #NamedNode('http://example.com/predicates/1'),
                  #NamedNode('http://example.com/objects/2')) in g
    #assert Triple(NamedNode('http://example.com/objects/2'),
                  #NamedNode('http://example.com/predicates/2'),
                  #NamedNode('http://example.com/objects/1')) in g
