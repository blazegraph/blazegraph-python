#
from rdflib.plugin import register
from rdflib.serializer import Serializer
from rdflib.parser import Parser

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
