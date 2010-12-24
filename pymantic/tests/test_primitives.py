from nose.tools import *
from pymantic.primitives import *
import random

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

def test_match_sVV_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple("http://example.com", None, None))
    assert t in matches
    
def test_match_sVo_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple("http://example.com", None, "Never!"))
    assert t in matches
    
def test_match_spV_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple("http://example.com", "http://purl.org/dc/terms/issued", None))
    assert t in matches
    
def test_match_Vpo_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple(None, "http://purl.org/dc/terms/issued", "Never!"))
    assert t in matches
    
def test_match_VVo_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple(None, None, "Never!"))
    assert t in matches

def test_match_VpV_pattern():
    t = Triple("http://example.com", "http://purl.org/dc/terms/issued","Never!")
    g = TripleGraph()
    g.add(t)
    matches = g.match(Triple(None, "http://purl.org/dc/terms/issued", None))
    assert t in matches
    
def generate_triples(n=10):
    for i in range(1,n):
        yield Triple("http://example/" + str(random.randint(1,1000)),
                   "http://example/terms/" + str(random.randint(1,1000)),
                   random.randint(1,1000))

def test_1000_triples():
    g = TripleGraph()
    for t in generate_triples(1000):
        g.add(t)
    matches = g.match(Triple("http://example.com/42", None, None))
    matches = g.match(Triple(None, "http://example/terms/42", None))
    matches = g.match(Triple(None, None, 42))