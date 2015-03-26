from unittest import TestCase

from cStringIO import StringIO
from nose.tools import *
from pymantic.parsers import *
from pymantic.primitives import *
from pymantic.serializers import *

def test_parse_ntriples_named_nodes():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> <http://example.com/objects/2> .
<http://example.com/objects/2> <http://example.com/predicates/2> <http://example.com/objects/1> .
"""
    g = Graph()
    ntriples_parser.parse(StringIO(test_ntriples), g)
    f = StringIO()
    serialize_ntriples(g, f)
    f.seek(0)
    g2 = Graph()
    ntriples_parser.parse(f, g2)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  NamedNode('http://example.com/objects/2')) in g2
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  NamedNode('http://example.com/objects/1')) in g2

class TestTurtleRepresentation(TestCase):
    def setUp(self):
        from pymantic.serializers import turtle_repr
        self.turtle_repr = turtle_repr
        import pymantic.primitives
        self.primitives = pymantic.primitives
        self.profile = self.primitives.Profile()
    
    def test_integer(self):
        lit = self.primitives.Literal(value='42', datatype=self.profile.resolve('xsd:integer'))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '42')
    
    def test_decimal(self):
        lit = self.primitives.Literal(value='4.2', datatype=self.profile.resolve('xsd:decimal'))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '4.2')
    
    def test_double(self):
        lit = self.primitives.Literal(value='4.2e1', datatype=self.profile.resolve('xsd:double'))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '4.2e1')
    
    def test_boolean(self):
        lit = self.primitives.Literal(value='true', datatype=self.profile.resolve('xsd:boolean'))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, 'true')
    
    def test_bare_string(self):
        lit = self.primitives.Literal(value='Foo', datatype=self.profile.resolve('xsd:string'))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '"Foo"')
    
    def test_language_string(self):
        lit = self.primitives.Literal(value='Foo', language="en")
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '"Foo"@en')
    
    def test_random_datatype_bare_url(self):
        lit = self.primitives.Literal(value='Foo', datatype=self.primitives.NamedNode("http://example.com/garply"))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '"Foo"^<http://example.com/garply>')
    
    def test_random_datatype_prefixed(self):
        self.profile.setPrefix('ex', self.primitives.NamedNode('http://example.com/'))
        lit = self.primitives.Literal(value='Foo', datatype=self.primitives.NamedNode("http://example.com/garply"))
        name = self.turtle_repr(node = lit, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '"Foo"^ex:garply')
    
    def test_named_node_bare(self):
        node = self.primitives.NamedNode('http://example.com/foo')
        name = self.turtle_repr(node = node, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, '<http://example.com/foo>')
    
    def test_named_node_prefixed(self):
        self.profile.setPrefix('ex', self.primitives.NamedNode('http://example.com/'))
        node = self.primitives.NamedNode('http://example.com/foo')
        name = self.turtle_repr(node = node, profile = self.profile, name_map = None, bnode_name_maker = None)
        self.assertEqual(name, 'ex:foo')

class TestTurtleSerializer(TestCase):
    def setUp(self):
        from pymantic.parsers import turtle_parser
        from pymantic.serializers import serialize_turtle
        self.turtle_parser = turtle_parser
        self.serialize_turtle = serialize_turtle
        import pymantic.primitives
        self.primitives = pymantic.primitives
        self.profile = self.primitives.Profile()
    
    def testSimpleSerialization(self):
        from cStringIO import StringIO
        basic_turtle = """@prefix dc: <http://purl.org/dc/terms/> .
        @prefix example: <http://example.com/> .

        example:foo dc:title "Foo" .
        example:bar dc:title "Bar" .
        example:baz dc:subject example:foo ."""

        graph = self.turtle_parser.parse(basic_turtle)
        f = StringIO()
        self.profile.setPrefix('ex', self.primitives.NamedNode('http://example.com/'))
        self.profile.setPrefix('dc', self.primitives.NamedNode('http://purl.org/dc/terms/'))
        self.serialize_turtle(graph = graph, f = f, profile = self.profile)
        f.seek(0)
        graph2 = self.turtle_parser.parse(f.read())
        f.seek(0)
        self.assertEqual(f.read().strip(), """@prefix ex: <http://example.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dc: <http://purl.org/dc/terms/> .
ex:bar dc:title "Bar" ;
       .

ex:baz dc:subject ex:foo ;
       .

ex:foo dc:title "Foo" ;
       .""")
    
    def testMultiplePredicates(self):
        from cStringIO import StringIO
        basic_turtle = """@prefix dc: <http://purl.org/dc/terms/> .
        @prefix example: <http://example.com/> .

        example:foo dc:title "Foo" ;
                    dc:author "Bar" ;
                    dc:subject example:yesfootoo .
        
        example:garply dc:title "Garply" ;
                    dc:author "Baz" ;
                    dc:subject example:thegarply ."""

        graph = self.turtle_parser.parse(basic_turtle)
        f = StringIO()
        self.profile.setPrefix('ex', self.primitives.NamedNode('http://example.com/'))
        self.profile.setPrefix('dc', self.primitives.NamedNode('http://purl.org/dc/terms/'))
        self.serialize_turtle(graph = graph, f = f, profile = self.profile)
        f.seek(0)
        graph2 = self.turtle_parser.parse(f.read())
        f.seek(0)
        self.assertEqual(f.read().strip(), """@prefix ex: <http://example.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dc: <http://purl.org/dc/terms/> .
ex:foo dc:author "Bar" ;
       dc:subject ex:yesfootoo ;
       dc:title "Foo" ;
       .

ex:garply dc:author "Baz" ;
          dc:subject ex:thegarply ;
          dc:title "Garply" ;
          .""")

    def testListSerialization(self):
        from cStringIO import StringIO
        basic_turtle = """@prefix dc: <http://purl.org/dc/terms/> .
        @prefix example: <http://example.com/> .

        example:foo dc:author ("Foo" "Bar" "Baz") ."""

        graph = self.turtle_parser.parse(basic_turtle)
        f = StringIO()
        self.profile.setPrefix('ex', self.primitives.NamedNode('http://example.com/'))
        self.profile.setPrefix('dc', self.primitives.NamedNode('http://purl.org/dc/terms/'))
        self.serialize_turtle(graph = graph, f = f, profile = self.profile)
        f.seek(0)
        print f.read()
        f.seek(0)
        graph2 = self.turtle_parser.parse(f.read())
        f.seek(0)
        self.assertEqual(f.read().strip(), """@prefix ex: <http://example.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dc: <http://purl.org/dc/terms/> .
ex:foo dc:author ("Foo" "Bar" "Baz") ;
       .""")
    
