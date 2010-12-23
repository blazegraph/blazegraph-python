"""Utility functions used throughout pymantic."""

import rdflib

def en(value):
    """Returns an RDF literal from the en language for the given value."""
    return rdflib.Literal(value, lang='en')

def de(value):
    """Returns an RDF literal from the de language for the given value."""
    return rdflib.Literal(value, lang='de')


def one_or_none(values):
    """Fetch the first value from values, or None if values is empty. Raises
    ValueError if values has more than one thing in it."""
    if not values:
        return None
    if len(values) > 1:
        raise ValueError('Got more than one value.')
    return values[0]
