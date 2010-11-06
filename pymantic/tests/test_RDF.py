import unittest

import rdflib

import pymantic.RDF
import pymantic.util

class TestRDF(unittest.TestCase):
    def testCurieURI(self):
        """Test CURIE parsing of explicit URIs."""
        test_ns = {'http': rdflib.Namespace('WRONG!'),
                   'urn': rdflib.Namespace('WRONG!'),}
        self.assertEqual(pymantic.RDF.parse_curie('http://oreilly.com', test_ns),
                         rdflib.URIRef('http://oreilly.com'))
        self.assertEqual(pymantic.RDF.parse_curie('urn:isbn:1234567890123', test_ns),
                         rdflib.URIRef('urn:isbn:1234567890123'))
    
    def testCurieDefaultNamespace(self):
        """Test CURIE parsing of CURIEs in the default namespace."""
        test_ns = {'': rdflib.Namespace('foo/'),
                   'wrong': rdflib.Namespace('WRONG!')}
        self.assertEqual(pymantic.RDF.parse_curie('bar', test_ns),
                         rdflib.URIRef('foo/bar'))
        self.assertEqual(pymantic.RDF.parse_curie('[bar]', test_ns),
                         rdflib.URIRef('foo/bar'))
        self.assertEqual(pymantic.RDF.parse_curie('baz', test_ns),
                         rdflib.URIRef('foo/baz'))
        self.assertEqual(pymantic.RDF.parse_curie('[aap]', test_ns),
                         rdflib.URIRef('foo/aap'))
    
    def testCurieNamespaces(self):
        """Test CURIE parsing of CURIEs in non-default namespaces."""
        test_ns = {'': rdflib.Namespace('WRONG!'),
                   'foo': rdflib.Namespace('foobly/'),
                   'bar': rdflib.Namespace('bardle/'),
                   'http': rdflib.Namespace('reallybadidea/'),}
        self.assertEqual(pymantic.RDF.parse_curie('foo:aap', test_ns),
                         rdflib.URIRef('foobly/aap'))
        self.assertEqual(pymantic.RDF.parse_curie('[bar:aap]', test_ns),
                         rdflib.URIRef('bardle/aap'))
        self.assertEqual(pymantic.RDF.parse_curie('[foo:baz]', test_ns),
                         rdflib.URIRef('foobly/baz'))
        self.assertEqual(pymantic.RDF.parse_curie('bar:baz', test_ns),
                         rdflib.URIRef('bardle/baz'))
        self.assertEqual(pymantic.RDF.parse_curie('[http://oreilly.com]', test_ns),
                         rdflib.URIRef('reallybadidea///oreilly.com'))
    
    def testCurieNoSuffix(self):
        """Test CURIE parsing of CURIEs with no suffix."""
        pass
    
    def testUnparseableCuries(self):
        """Test some CURIEs that shouldn't parse."""
        test_ns = {'foo': rdflib.Namespace('WRONG!'),}
        self.assertRaises(ValueError, pymantic.RDF.parse_curie, '[bar]', test_ns)
        self.assertRaises(ValueError, pymantic.RDF.parse_curie, 'bar', test_ns)
        self.assertRaises(ValueError, pymantic.RDF.parse_curie, 'bar:baz', test_ns)
        self.assertRaises(ValueError, pymantic.RDF.parse_curie, '[bar:baz]', test_ns)
    
    def testMetaResourceNothingUseful(self):
        """Test applying a MetaResource to a class without anything it uses."""
        class Foo(object):
            __metaclass__ = pymantic.RDF.MetaResource
    
    def testMetaResourceNamespaces(self):
        """Test the handling of namespaces by MetaResource."""
        class Foo(object):
            __metaclass__ = pymantic.RDF.MetaResource
            namespaces = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        
        self.assertEqual(Foo.namespaces, {'foo': rdflib.Namespace('bar'),
                                          'baz': rdflib.Namespace('garply'),
                                          'meme': rdflib.Namespace('lolcatz!'),})
    
    def testMetaResourceNamespaceInheritance(self):
        """Test the composition of namespace dictionaries by MetaResource."""
        class Foo(object):
            __metaclass__ = pymantic.RDF.MetaResource
            namespaces = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        class Bar(Foo):
            namespaces = {'allyourbase': 'arebelongtous!', 'bunny': 'pancake',}
        self.assertEqual(Foo.namespaces, {'foo': rdflib.Namespace('bar'),
                                          'baz': rdflib.Namespace('garply'),
                                          'meme': rdflib.Namespace('lolcatz!'),})
        self.assertEqual(Bar.namespaces, {'foo': rdflib.Namespace('bar'),
                                          'baz': rdflib.Namespace('garply'),
                                          'meme': rdflib.Namespace('lolcatz!'),
                                          'allyourbase': rdflib.Namespace('arebelongtous!'),
                                          'bunny': rdflib.Namespace('pancake'),})
    
    def testMetaResourceNamespaceInheritanceReplacement(self):
        """Test the composition of namespace dictionaries by MetaResource where
        some namespaces on the parent get replaced."""
        class Foo(object):
            __metaclass__ = pymantic.RDF.MetaResource
            namespaces = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        class Bar(Foo):
            namespaces = {'allyourbase': 'arebelongtous!', 'bunny': 'pancake',
                          'foo': 'notbar', 'baz': 'notgarply',}
        self.assertEqual(Foo.namespaces, {'foo': rdflib.Namespace('bar'),
                                          'baz': rdflib.Namespace('garply'),
                                          'meme': rdflib.Namespace('lolcatz!'),})
        self.assertEqual(Bar.namespaces, {'foo': rdflib.Namespace('notbar'),
                                          'baz': rdflib.Namespace('notgarply'),
                                          'meme': rdflib.Namespace('lolcatz!'),
                                          'allyourbase': rdflib.Namespace('arebelongtous!'),
                                          'bunny': rdflib.Namespace('pancake'),})

    def testResourceEquality(self):
        graph = rdflib.ConjunctiveGraph()
        otherGraph = rdflib.ConjunctiveGraph()
        testResource = pymantic.RDF.Resource.for_uri(graph, 'foo')
        self.assertEqual(testResource, pymantic.RDF.Resource.for_uri(
            graph, 'foo'))
        self.assertEqual(testResource, rdflib.URIRef('foo'))
        self.assertEqual(testResource, 'foo')
        self.assertNotEqual(testResource, pymantic.RDF.Resource.for_uri(
            graph, 'bar'))
        self.assertEqual(testResource, pymantic.RDF.Resource.for_uri(
            otherGraph, 'foo'))
        self.assertNotEqual(testResource, rdflib.URIRef('bar'))
        self.assertNotEqual(testResource, 'bar')
        self.assertNotEqual(testResource, 42)
