#
from rdflib.plugin import register
from rdflib.serializer import Serializer

register('nt', Serializer, 'pymantic.serializers', 'NTSerializer')
register('nq', Serializer, 'pymantic.serializers', 'NQSerializer')