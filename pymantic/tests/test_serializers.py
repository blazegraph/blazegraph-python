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
    parse_ntriples(StringIO(test_ntriples), g)
    f = StringIO()
    serialize_ntriples(g, f)
    f.seek(0)
    g2 = Graph()
    parse_ntriples(f, g2)
    assert len(g) == 2
    assert Triple(NamedNode('http://example.com/objects/1'),
                  NamedNode('http://example.com/predicates/1'),
                  NamedNode('http://example.com/objects/2')) in g2
    assert Triple(NamedNode('http://example.com/objects/2'),
                  NamedNode('http://example.com/predicates/2'),
                  NamedNode('http://example.com/objects/1')) in g2