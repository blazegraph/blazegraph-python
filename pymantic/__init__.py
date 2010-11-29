#
from rdflib.plugin import register
from rdflib.serializer import Serializer
from rdflib.parser import Parser

register('nt', Serializer, 'pymantic.serializers', 'NTSerializer')
register('nq', Serializer, 'pymantic.serializers', 'NQSerializer')
register('nq', Parser, 'pymantic.parsers', 'NQParser')