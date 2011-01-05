from nose.tools import *
from pymantic.util import *

def test_normalize_iri_no_escapes():
    normalized = normalize_iri('http://example.com/foo/bar?garply=aap&maz=bies')
    assert normalized == u'http://example.com/foo/bar?garply=aap&maz=bies'

def test_normalize_iri_escaped_slash():
    normalized = normalize_iri('http://example.com/foo%2Fbar?garply=aap&maz=bies')
    print normalized
    assert normalized == u'http://example.com/foo%2Fbar?garply=aap&maz=bies'
    
def test_normalize_iri_escaped_ampersand():
    normalized = normalize_iri('http://example.com/foo/bar?garply=aap%26yak&maz=bies')
    assert normalized == u'http://example.com/foo/bar?garply=aap%26yak&maz=bies'
    
def test_normalize_iri_escaped_international():
    normalized = normalize_iri('http://example.com/foo/bar?garply=aap&maz=bi%C3%89s')
    print repr(normalized)
    assert normalized == u'http://example.com/foo/bar?garply=aap&maz=bi\u00C9s'
