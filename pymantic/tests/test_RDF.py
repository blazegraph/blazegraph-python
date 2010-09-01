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

    def testLanguageScalarProperties(self):
        """Language filtering in ScalarProperties works"""
        class Foo(pymantic.RDF.Resource):
            namespaces = {'test': 'http://example.com/test',}
            english_name = pymantic.RDF.ScalarPredicateProperty('test:name',language="en")
        testns = rdflib.Namespace('http://example.com/test')
        graph = rdflib.ConjunctiveGraph()
        graph.add((rdflib.URIRef('foo'), testns['name'], rdflib.Literal("english",lang="en")))
        graph.add((rdflib.URIRef('foo'), testns['name'], rdflib.Literal("german",lang="de")))
        foo = Foo.for_uri(graph,'foo')
        self.assertEquals(foo.english_name, pymantic.util.en("english"))
        
    def testClassification(self):
        """Test the classification feature."""
        graph = rdflib.ConjunctiveGraph()
        rdfns = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        testns = rdflib.Namespace('test!')
        graph.set((rdflib.URIRef('foo'), rdfns['type'], testns['lolcats']))
        graph.set((rdflib.URIRef('foo'), testns['test'], "Brains."))
        graph.set((rdflib.URIRef('bar'), rdfns['type'], testns['lolcats']))
        graph.set((rdflib.URIRef('bar'), testns['test'], "Brains!"))
        graph.set((rdflib.URIRef('baz'), rdfns['type'], testns['orlyowl']))
        graph.set((rdflib.URIRef('baz'), testns['test'], "Brains!!!"))
        class Test(pymantic.RDF.Resource):
            namespaces = {'test': 'test!',}
            classification_value = 'test:lolcats'
            test = pymantic.RDF.ScalarPredicateProperty('test:test')
        t_foo = Test.for_uri(graph, 'foo')
        self.assertEqual(t_foo.test, 'Brains.')
        t_bar = Test.for_uri(graph, 'bar')
        self.assertEqual(t_bar.test, 'Brains!')
        self.assert_(Test.for_uri(graph, 'baz') is None)
        self.assertRaises(pymantic.RDF.ClassificationMismatchError,
                          Test, graph, rdflib.URIRef('baz'))
        l = list(Test.in_graph(graph))
        self.assertEqual(len(l), 2)
        self.assert_(t_foo in l)
        self.assert_(t_bar in l)

    def testClassificationPredicate(self):
        """Test the classification feature with different predicates."""
        graph = rdflib.ConjunctiveGraph()
        testns = rdflib.Namespace('test!')
        graph.set((rdflib.URIRef('foo'), testns['type'], testns['lolcats']))
        graph.set((rdflib.URIRef('foo'), testns['test'], "Brains."))
        graph.set((rdflib.URIRef('bar'), testns['type'], testns['lolcats']))
        graph.set((rdflib.URIRef('bar'), testns['test'], "Brains!"))
        graph.set((rdflib.URIRef('baz'), testns['type'], testns['orlyowl']))
        graph.set((rdflib.URIRef('baz'), testns['test'], "Brains!!!"))
        class Test(pymantic.RDF.Resource):
            namespaces = {'test': 'test!',}
            classification_predicate = 'test:type'
            classification_value = 'test:lolcats'
            test = pymantic.RDF.ScalarPredicateProperty('test:test')
        t_foo = Test.for_uri(graph, 'foo')
        self.assertEqual(t_foo.test, 'Brains.')
        t_bar = Test.for_uri(graph, 'bar')
        self.assertEqual(t_bar.test, 'Brains!')
        self.assert_(Test.for_uri(graph, 'baz') is None)
        self.assertRaises(pymantic.RDF.ClassificationMismatchError,
                          Test, graph, rdflib.URIRef('baz'))
        l = list(Test.in_graph(graph))
        self.assertEqual(len(l), 2)
        self.assert_(t_foo in l)
        self.assert_(t_bar in l)
    
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
    
    def testAutomaticResourceRetreival(self):
        class FakeProductType(pymantic.RDF.Resource):
                namespaces = {'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                              'dcam': 'http://purl.org/dc/dcam/',}
    
                classification_predicate = 'dcam:memberOf'
    
                classification_value = 'http://purl.oreilly.com/product-types/'
                
                label = pymantic.RDF.ScalarPredicateProperty('rdfs:label')
        
        graph = rdflib.ConjunctiveGraph()
        graph.retrieve_http = True
        testResource = FakeProductType.for_uri(graph, 'http://purl.oreilly.com/product-types/BOOK')
        self.assertEqual(testResource.label,
                         rdflib.Literal('Print', lang='en-US'))
        self.assert_(rdflib.URIRef('http://purl.oreilly.com/product-types/BOOK') in graph.retrieved_uris)
