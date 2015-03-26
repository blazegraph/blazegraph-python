import os.path
import unittest
from pymantic.parsers import turtle_parser, ntriples_parser
import pymantic.rdf as rdf

turtle_tests_url = 'http://dvcs.w3.org/hg/rdf/raw-file/default/rdf-turtle/tests/'

prefixes = {
    'mf': 'http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#',
    'qt': 'http://www.w3.org/2001/sw/DataAccess/tests/test-query#',
}

@rdf.register_class('mf:Manifest')
class Manifest(rdf.Resource):
    prefixes = prefixes

    scalars = frozenset(('rdfs:comment','mf:entries'))

class ManifestEntry(rdf.Resource):
    prefixes = prefixes

    scalars = frozenset(('mf:name', 'rdfs:comment', 'mf:action', 'mf:result'))

class Action(rdf.Resource):
    prefixes = prefixes

    scalars = frozenset(('qt:data',))

class MetaRDFTest(type):
    def __new__(mcs, name, bases, dict):
        manifest_name = dict['manifest']
        with open(manifest_name, 'r') as f:
            manifest_turtle = f.read()
        manifest_graph = turtle_parser.parse(manifest_turtle, base=dict['base'])
        manifest = Manifest(manifest_graph, dict['base'])
        entries = manifest['mf:entries'].as_(rdf.List)
        for entry in entries:
            entry = entry.as_(ManifestEntry)
            test_name = entry['mf:name'].value.replace('-', '_')
            if not test_name.startswith('test_'):
                test_name = 'test_' + test_name
            dict[test_name] = lambda self, entry=entry: self.execute(entry)
            # Doesn't look right in tracebacks, but looks fine in nose output.
            dict[test_name].func_name = test_name
        return type.__new__(mcs, name, bases, dict)

class TurtleTests(unittest.TestCase):
    __metaclass__ = MetaRDFTest

    base = os.path.join(os.path.dirname(__file__), 'turtle_tests/')

    manifest = os.path.join(base, 'manifest.ttl')

    def execute(self, entry):
        with open(unicode(entry['mf:action'].as_(Action)['qt:data']), 'r') as f:
            in_data = f.read()
        with open(unicode(entry['mf:result'])) as f:
            compare_data = f.read()
        test_graph = turtle_parser.parse(in_data)
        compare_graph = ntriples_parser.parse_string(compare_data)

class BadTurtleTests(unittest.TestCase):
    __metaclass__ = MetaRDFTest

    base = os.path.join(os.path.dirname(__file__), 'turtle_tests/')

    manifest = os.path.join(base, 'manifest-bad.ttl')

    def execute(self, entry):
        with open(unicode(entry['mf:action'].as_(Action)['qt:data']), 'r') as f:
            in_data = f.read()
            print in_data
        try:
            test_graph = turtle_parser.parse(in_data)
        except:
            pass
        else:
            self.fail('should not have parsed')
