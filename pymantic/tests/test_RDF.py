import unittest

import rdflib

import pymantic.RDF
import pymantic.util

class TestRDF(unittest.TestCase):
    def tearDown(self):
        pymantic.RDF.MetaResource._classes = {}
    
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
        testResource = pymantic.RDF.Resource(graph, 'foo')
        self.assertEqual(testResource, pymantic.RDF.Resource(
            graph, 'foo'))
        self.assertEqual(testResource, rdflib.URIRef('foo'))
        self.assertEqual(testResource, 'foo')
        self.assertNotEqual(testResource, pymantic.RDF.Resource(
            graph, 'bar'))
        self.assertEqual(testResource, pymantic.RDF.Resource(
            otherGraph, 'foo'))
        self.assertNotEqual(testResource, rdflib.URIRef('bar'))
        self.assertNotEqual(testResource, 'bar')
        self.assertNotEqual(testResource, 42)
    
    def testClassification(self):
        """Test classification of a resource."""
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject = rdflib.URIRef('http://example.com/athing')
        graph = rdflib.ConjunctiveGraph()
        graph.add((test_subject, Offering.resolve('rdf:type'),
                   Offering.resolve('gr:Offering')))
        offering = pymantic.RDF.Resource.classify(graph, test_subject)
        self.assert_(isinstance(offering, Offering))
    
    def testMulticlassClassification(self):
        """Test classification of a resource that matches multiple registered
        classes."""
        @pymantic.RDF.register_class('foaf:Organization')
        class Organization(pymantic.RDF.Resource):
            namespaces = {
                'foaf': 'http://xmlns.com/foaf/0.1/',
            }
        
        @pymantic.RDF.register_class('foaf:Group')
        class Group(pymantic.RDF.Resource):
            namespaces = {
                'foaf': 'http://xmlns.com/foaf/0.1/',
            }
        
        test_subject1 = rdflib.URIRef('http://example.com/aorganization')
        test_subject2 = rdflib.URIRef('http://example.com/agroup')
        test_subject3 = rdflib.URIRef('http://example.com/aorgandgroup')
        graph = rdflib.ConjunctiveGraph()
        graph.add((test_subject1, Organization.resolve('rdf:type'),
                   Organization.resolve('foaf:Organization')))
        graph.add((test_subject2, Group.resolve('rdf:type'),
                   Group.resolve('foaf:Group')))
        graph.add((test_subject3, Organization.resolve('rdf:type'),
                   Organization.resolve('foaf:Organization')))
        graph.add((test_subject3, Organization.resolve('rdf:type'),
                   Organization.resolve('foaf:Group')))
        organization = pymantic.RDF.Resource.classify(graph, test_subject1)
        group = pymantic.RDF.Resource.classify(graph, test_subject2)
        both = pymantic.RDF.Resource.classify(graph, test_subject3)
        self.assert_(isinstance(organization, Organization))
        self.assertFalse(isinstance(organization, Group))
        self.assertFalse(isinstance(group, Organization))
        self.assert_(isinstance(group, Group))
        self.assert_(isinstance(both, Organization))
        self.assert_(isinstance(both, Group))
