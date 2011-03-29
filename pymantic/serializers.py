import re
import warnings

def nt_escape(node_string):
    """Properly escape strings for n-triples and n-quads serialization."""
    output_string = ''
    for char in node_string:
        if char == u'\u0009':
            output_string += '\\t'
        elif char == u'\u000A':
            output_string += '\\n'
        elif char == u'\u000D':
            output_string += '\\r'
        elif char == u'\u0022':
            output_string += '\\"'
        elif char == u'\u005C':
            output_string += '\\\\'
        elif char >= u'\u0020' and char <= u'\u0021' or\
             char >= u'\u0023' and char <= u'\u005B' or\
             char >= u'\u005D' and char <= u'\u007E':
            output_string += char.encode('utf-8')
        elif char >= u'\u007F' and char <= u'\uFFFF':
            output_string += '\\u%04X' % ord(char)
        elif char >= u'\U00010000' and char <= u'\U0010FFFF':
            output_string += '\\U%08X' % ord(char)
    return output_string

def serialize_ntriples(graph, f):
    for triple in graph:
        f.write(str(triple))

def serialize_nquads(dataset, f):
    for quad in dataset:
        f.write(str(quad))
