import re
import warnings

from rdflib.serializer import Serializer
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.parsers.ntriples import r_uriref

class NTSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format as per standard.
    
    Follows http://www.w3.org/TR/rdf-testcases/#ntriples
    
    Based on NTSerializer from rdflib.
    """
    
    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NTSerializer does not support base.")
        if encoding is not None:
            warnings.warn("NTSerializer does not use custom encoding.")
        encoding = self.encoding
        for triple in self.store:
            try:
                stream.write(_nt_row(triple).encode(encoding, "replace"))
            except NotURIError, e:
                warnings.warn('Ignoring triple, Not a URI: %s' % e.message)
        stream.write("\n")

def _nt_row(triple):
    return u"%s %s %s .\n" % (nt(triple[0]),
            nt(triple[1]),
            nt(triple[2]))

class NotURIError(Exception):
    pass

def nt(node):
    if isinstance(node, URIRef):
        uriref = '<' + nt_escape(unicode(node)) + '>'
        if not r_uriref.match(uriref):
            raise NotURIError(uriref)
        return uriref
    if isinstance(node, BNode):
        return '_:' + str(node)
    if isinstance(node, Literal):
        literal = '"' + nt_escape(unicode(node)) + '"'
        if node.language is not None:
            literal += '@' + node.language
        elif node.datatype is not None:
            literal += '^^' + nt(node.datatype)
        return literal

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
            output_string += char.enocde('utf-8')
        elif char >= u'\u007F' and char <= u'\uFFFF':
            output_string += '\\u%04X' % ord(char)
        elif char >= u'\U00010000' and char <= u'\U0010FFFF':
            output_string += '\\U%08X' % ord(char)
    return output_string

class NQSerializer(Serializer):
    """
    Serializes RDF graphs to NQuads format as per standard.
    
    Follows http://sw.deri.org/2008/07/n-quads/
    
    Based on NTSerializer from rdflib.
    """
    
    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NTSerializer does not support base.")
        if encoding is not None:
            warnings.warn("NTSerializer does not use custom encoding.")
        encoding = self.encoding
        for quad in self.store.quads((None, None, None)):
            try:
                stream.write(_nq_row(quad).encode(encoding, "replace"))
            except NotURIError, e:
                warnings.warn('Ignoring quad, Not a URI: %s' % e.message)
        stream.write("\n")

def _nq_row(triple):
    return u"%s %s %s %s .\n" % (nt(triple[0]),
            nt(triple[1]),
            nt(triple[2]),
            nt(triple[3].identifier))
