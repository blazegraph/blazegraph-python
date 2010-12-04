#
from rdflib.plugin import register
from rdflib.serializer import Serializer
from rdflib.parser import Parser
import re

# Fix rdflib's ntriples parser
from rdflib.plugins.parsers import ntriples
ntriples.litinfo = r'(?:@([a-z]+(?:-[a-zA-Z0-9]+)*)|\^\^' + ntriples.uriref + r')?'
ntriples.r_literal = re.compile(ntriples.literal + ntriples.litinfo)

register('nt', Serializer, 'pymantic.serializers', 'NTSerializer')
register('nq', Serializer, 'pymantic.serializers', 'NQSerializer')
register('nq', Parser, 'pymantic.parsers', 'NQParser')

content_type_to_rdflib_format = {
    'text/plain': 'nt',
    'text/x-nquads': 'nq',
    'application/rdf+xml': 'xml',
    'text/turtle': 'turtle',
}

rdflib_format_to_content_type = dict((value, key) for key, value in\
                                     content_type_to_rdflib_format.iteritems())
