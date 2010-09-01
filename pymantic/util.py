"""Utility functions used throughout pymantic."""

import rdflib

def en(value):
    """Returns an RDF literal from the en-US language for the given value."""
    return rdflib.Literal(value, lang='en')

def one_or_none(values):
    """Fetch the first value from values, or None if values is empty. Raises
    ValueError if values has more than one thing in it."""
    if not values:
        return None
    if len(values) > 1:
        raise ValueError('Got more than one value.')
    return values[0]
