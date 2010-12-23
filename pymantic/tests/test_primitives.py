from nose.tools import *
from pymantic.primitives import *

def test_simple_add():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    assert t in g
    
def test_simple_remove():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    g.remove(t)
    assert t not in g

def test_match_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple("http://example.com", None, None))
    assert t in matches