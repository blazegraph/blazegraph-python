"""Utility functions used throughout pymantic."""

__all__ = ['en', 'de', 'one_or_none', 'normalize_iri', 'quote_normalized_iri',]

import re
from urllib import quote

def en(value):
    """Returns an RDF literal from the en language for the given value."""
    from pymantic.primitives import Literal
    return Literal(value, language='en')

def de(value):
    """Returns an RDF literal from the de language for the given value."""
    from pymantic.primitives import Literal
    return Literal(value, language='de')

def one_or_none(values):
    """Fetch the first value from values, or None if values is empty. Raises
    ValueError if values has more than one thing in it."""
    if not values:
        return None
    if len(values) > 1:
        raise ValueError('Got more than one value.')
    return values[0]

percent_encoding_re = re.compile(r'(?:%[a-fA-F0-9][a-fA-F0-9])+')

reserved_in_iri = ["%", ":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'",\
                   "(", ")", "*", "+", ",", ";", "="]

def percent_decode(regmatch):
    encoded = ''
    for group in regmatch.group(0)[1:].split('%'):
        encoded += chr(int(group, 16))
    uni = encoded.decode('utf-8')
    for res in reserved_in_iri:
        uni = uni.replace(res, '%%%02X' % ord(res))
    return uni

def normalize_iri(iri):
    """Normalize an IRI using the Case Normalization (5.3.2.1) and
    Percent-Encoding Normalization (5.3.2.3) from RFC 3987. The IRI should be a
    unicode object."""
    return percent_encoding_re.sub(percent_decode, iri)

def percent_encode(char):
    return ''.join('%%%02X' % ord(char) for char in char.encode('utf-8'))

def quote_normalized_iri(normalized_iri):
    """Percent-encode a normalized IRI; IE, all reserved characters are presumed
    to be themselves and not percent encoded. All other unsafe characters are
    percent-encoded."""
    normalized_uri = ''.join(percent_encode(char) if ord(char) > 127 else char for\
                             char in normalized_iri)
    return quote(normalized_uri, safe=''.join(reserved_in_iri))
