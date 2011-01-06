from nose.tools import *
from pymantic.util import *

def test_normalize_iri_no_escapes():
    uri = 'http://example.com/foo/bar?garply=aap&maz=bies'
    normalized = normalize_iri(uri)
    assert normalized == u'http://example.com/foo/bar?garply=aap&maz=bies'
    assert normalized == normalize_iri(normalized)
    assert quote_normalized_iri(normalized) == uri

def test_normalize_iri_escaped_slash():
    uri = 'http://example.com/foo%2Fbar?garply=aap&maz=bies'
    normalized = normalize_iri(uri)
    print normalized
    assert normalized == u'http://example.com/foo%2Fbar?garply=aap&maz=bies'
    assert normalized == normalize_iri(normalized)
    assert quote_normalized_iri(normalized) == uri
    
def test_normalize_iri_escaped_ampersand():
    uri = 'http://example.com/foo/bar?garply=aap%26yak&maz=bies'
    normalized = normalize_iri(uri)
    assert normalized == u'http://example.com/foo/bar?garply=aap%26yak&maz=bies'
    assert normalized == normalize_iri(normalized)
    assert quote_normalized_iri(normalized) == uri
    
def test_normalize_iri_escaped_international():
    uri = 'http://example.com/foo/bar?garply=aap&maz=bi%C3%89s'
    normalized = normalize_iri(uri)
    print repr(normalized)
    assert normalized == u'http://example.com/foo/bar?garply=aap&maz=bi\u00C9s'
    assert normalized == normalize_iri(normalized)
    assert quote_normalized_iri(normalized) == uri
