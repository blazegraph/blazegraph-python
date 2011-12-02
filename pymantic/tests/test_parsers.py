from cStringIO import StringIO
from nose.tools import *
from nose.plugins.skip import Skip, SkipTest
from pymantic.parsers import *
from pymantic.primitives import *

def test_parse_ntriples_named_nodes():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> <http://example.com/objects/2> .
<http://example.com/objects/2> <http://example.com/predicates/2> <http://example.com/objects/1> .
"""
    g = Graph()
    ntriples_parser.parse(StringIO(test_ntriples), g)
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
    ntriples_parser.parse(StringIO(test_ntriples), g)
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
    ntriples_parser.parse(StringIO(test_ntriples), g)
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
    ntriples_parser.parse(StringIO(test_ntriples), g)
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
    ntriples_parser.parse(StringIO(test_ntriples), g)
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
    ntriples_parser.parse(StringIO(test_ntriples), g)
    assert len(g) == 2
    #assert Triple(NamedNode('http://example.com/objects/1'),
                  #NamedNode('http://example.com/predicates/1'),
                  #NamedNode('http://example.com/objects/2')) in g
    #assert Triple(NamedNode('http://example.com/objects/2'),
                  #NamedNode('http://example.com/predicates/2'),
                  #NamedNode('http://example.com/objects/1')) in g
                  
def test_parse_turtle_example_1():
    ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix ex: <http://example.org/stuff/1.0/> .

<http://www.w3.org/TR/rdf-syntax-grammar>
  dc:title "RDF/XML Syntax Specification (Revised)" ;
  ex:editor [
    ex:fullname "Dave Beckett";
    ex:homePage <http://purl.org/net/dajobe/>
  ] ."""
    g = Graph()
    turtle_parser.parse(data=ttl, sink=g)
    assert len(g) == 4

