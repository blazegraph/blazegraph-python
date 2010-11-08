import unittest

import rdflib.graph
import rdflib.term
import rdflib.namespace

import pymantic.RDF
import pymantic.util

class TestRDF(unittest.TestCase):
    def tearDown(self):
        pymantic.RDF.MetaResource._classes = {}
    
    def testCurieURI(self):
        """Test CURIE parsing of explicit URIs."""
        test_ns = {'http': rdflib.namespace.Namespace('WRONG!'),
                   'urn': rdflib.namespace.Namespace('WRONG!'),}
        self.assertEqual(pymantic.RDF.parse_curie('http://oreilly.com', test_ns),
                         rdflib.term.URIRef('http://oreilly.com'))
        self.assertEqual(pymantic.RDF.parse_curie('urn:isbn:1234567890123', test_ns),
                         rdflib.term.URIRef('urn:isbn:1234567890123'))
    
    def testCurieDefaultNamespace(self):
        """Test CURIE parsing of CURIEs in the default namespace."""
        test_ns = {'': rdflib.namespace.Namespace('foo/'),
                   'wrong': rdflib.namespace.Namespace('WRONG!')}
        self.assertEqual(pymantic.RDF.parse_curie('bar', test_ns),
                         rdflib.term.URIRef('foo/bar'))
        self.assertEqual(pymantic.RDF.parse_curie('[bar]', test_ns),
                         rdflib.term.URIRef('foo/bar'))
        self.assertEqual(pymantic.RDF.parse_curie('baz', test_ns),
                         rdflib.term.URIRef('foo/baz'))
        self.assertEqual(pymantic.RDF.parse_curie('[aap]', test_ns),
                         rdflib.term.URIRef('foo/aap'))
    
    def testCurieNamespaces(self):
        """Test CURIE parsing of CURIEs in non-default namespaces."""
        test_ns = {'': rdflib.namespace.Namespace('WRONG!'),
                   'foo': rdflib.namespace.Namespace('foobly/'),
                   'bar': rdflib.namespace.Namespace('bardle/'),
                   'http': rdflib.namespace.Namespace('reallybadidea/'),}
        self.assertEqual(pymantic.RDF.parse_curie('foo:aap', test_ns),
                         rdflib.term.URIRef('foobly/aap'))
        self.assertEqual(pymantic.RDF.parse_curie('[bar:aap]', test_ns),
                         rdflib.term.URIRef('bardle/aap'))
        self.assertEqual(pymantic.RDF.parse_curie('[foo:baz]', test_ns),
                         rdflib.term.URIRef('foobly/baz'))
        self.assertEqual(pymantic.RDF.parse_curie('bar:baz', test_ns),
                         rdflib.term.URIRef('bardle/baz'))
        self.assertEqual(pymantic.RDF.parse_curie('[http://oreilly.com]', test_ns),
                         rdflib.term.URIRef('reallybadidea///oreilly.com'))
    
    def testCurieNoSuffix(self):
        """Test CURIE parsing of CURIEs with no suffix."""
        pass
    
    def testUnparseableCuries(self):
        """Test some CURIEs that shouldn't parse."""
        test_ns = {'foo': rdflib.namespace.Namespace('WRONG!'),}
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
        
        self.assertEqual(Foo.namespaces, {'foo': rdflib.namespace.Namespace('bar'),
                                          'baz': rdflib.namespace.Namespace('garply'),
                                          'meme': rdflib.namespace.Namespace('lolcatz!'),})
    
    def testMetaResourceNamespaceInheritance(self):
        """Test the composition of namespace dictionaries by MetaResource."""
        class Foo(object):
            __metaclass__ = pymantic.RDF.MetaResource
            namespaces = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        class Bar(Foo):
            namespaces = {'allyourbase': 'arebelongtous!', 'bunny': 'pancake',}
        self.assertEqual(Foo.namespaces, {'foo': rdflib.namespace.Namespace('bar'),
                                          'baz': rdflib.namespace.Namespace('garply'),
                                          'meme': rdflib.namespace.Namespace('lolcatz!'),})
        self.assertEqual(Bar.namespaces, {'foo': rdflib.namespace.Namespace('bar'),
                                          'baz': rdflib.namespace.Namespace('garply'),
                                          'meme': rdflib.namespace.Namespace('lolcatz!'),
                                          'allyourbase': rdflib.namespace.Namespace('arebelongtous!'),
                                          'bunny': rdflib.namespace.Namespace('pancake'),})
    
    def testMetaResourceNamespaceInheritanceReplacement(self):
        """Test the composition of namespace dictionaries by MetaResource where
        some namespaces on the parent get replaced."""
        class Foo(object):
            __metaclass__ = pymantic.RDF.MetaResource
            namespaces = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        class Bar(Foo):
            namespaces = {'allyourbase': 'arebelongtous!', 'bunny': 'pancake',
                          'foo': 'notbar', 'baz': 'notgarply',}
        self.assertEqual(Foo.namespaces, {'foo': rdflib.namespace.Namespace('bar'),
                                          'baz': rdflib.namespace.Namespace('garply'),
                                          'meme': rdflib.namespace.Namespace('lolcatz!'),})
        self.assertEqual(Bar.namespaces, {'foo': rdflib.namespace.Namespace('notbar'),
                                          'baz': rdflib.namespace.Namespace('notgarply'),
                                          'meme': rdflib.namespace.Namespace('lolcatz!'),
                                          'allyourbase': rdflib.namespace.Namespace('arebelongtous!'),
                                          'bunny': rdflib.namespace.Namespace('pancake'),})

    def testResourceEquality(self):
        graph = rdflib.graph.Graph()
        otherGraph = rdflib.graph.Graph()
        testResource = pymantic.RDF.Resource(graph, 'foo')
        self.assertEqual(testResource, pymantic.RDF.Resource(
            graph, 'foo'))
        self.assertEqual(testResource, rdflib.term.URIRef('foo'))
        self.assertEqual(testResource, 'foo')
        self.assertNotEqual(testResource, pymantic.RDF.Resource(
            graph, 'bar'))
        self.assertEqual(testResource, pymantic.RDF.Resource(
            otherGraph, 'foo'))
        self.assertNotEqual(testResource, rdflib.term.URIRef('bar'))
        self.assertNotEqual(testResource, 'bar')
        self.assertNotEqual(testResource, 42)
    
    def testClassification(self):
        """Test classification of a resource."""
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject = rdflib.term.URIRef('http://example.com/athing')
        graph = rdflib.graph.Graph()
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
        
        test_subject1 = rdflib.term.URIRef('http://example.com/aorganization')
        test_subject2 = rdflib.term.URIRef('http://example.com/agroup')
        test_subject3 = rdflib.term.URIRef('http://example.com/aorgandgroup')
        graph = rdflib.graph.Graph()
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

    def testStr(self):
        """Test str-y serialization of Resources."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/aorganization')
        test_label = rdflib.term.Literal('Test Label', lang='en')
        graph.add((test_subject1, pymantic.RDF.Resource.resolve('rdfs:label'),
                   test_label))
        r = pymantic.RDF.Resource(graph, test_subject1)
        self.assertEqual(r['rdfs:label'], test_label)
        self.assertEqual(str(r), str(test_label))
    
    def testGetSetDelPredicate(self):
        """Test getting, setting, and deleting a multi-value predicate."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/')
        r = pymantic.RDF.Resource(graph, test_subject1)
        r['rdfs:example'] = set(('foo', 'bar'))
        example_values = set(r['rdfs:example'])
        self.assert_(rdflib.term.Literal('foo', lang='en') in example_values)
        self.assert_(rdflib.term.Literal('bar', lang='en') in example_values)
        self.assertEqual(len(example_values), 2)
        del r['rdfs:example']
        example_values = set(r['rdfs:example'])
        self.assertEqual(len(example_values), 0)
    
    def testGetSetDelScalarPredicate(self):
        """Test getting, setting, and deleting a scalar predicate."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/')
        r = pymantic.RDF.Resource(graph, test_subject1)
        r['rdfs:label'] = 'foo'
        self.assertEqual(r['rdfs:label'], rdflib.term.Literal('foo', lang='en'))
        del r['rdfs:label']
        self.assertEqual(r['rdfs:label'], None)
    
    def testGetSetDelPredicateLanguage(self):
        """Test getting, setting and deleting a multi-value predicate with an explicit language."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/')
        r = pymantic.RDF.Resource(graph, test_subject1)
        r['rdfs:example', 'en'] = set(('baz',))
        r['rdfs:example', 'fr'] = set(('foo', 'bar'))
        example_values = set(r['rdfs:example', 'fr'])
        self.assert_(rdflib.term.Literal('foo', lang='fr') in example_values)
        self.assert_(rdflib.term.Literal('bar', lang='fr') in example_values)
        self.assert_(rdflib.term.Literal('baz', lang='en') not in example_values)
        self.assertEqual(len(example_values), 2)
        example_values = set(r['rdfs:example', 'en'])
        self.assert_(rdflib.term.Literal('foo', lang='fr') not in example_values)
        self.assert_(rdflib.term.Literal('bar', lang='fr') not in example_values)
        self.assert_(rdflib.term.Literal('baz', lang='en') in example_values)
        self.assertEqual(len(example_values), 1)
        del r['rdfs:example', 'fr']
        example_values = set(r['rdfs:example', 'fr'])
        self.assertEqual(len(example_values), 0)
        example_values = set(r['rdfs:example', 'en'])
        self.assert_(rdflib.term.Literal('foo', lang='fr') not in example_values)
        self.assert_(rdflib.term.Literal('bar', lang='fr') not in example_values)
        self.assert_(rdflib.term.Literal('baz', lang='en') in example_values)
        self.assertEqual(len(example_values), 1)
    
    def testGetSetDelScalarPredicateLanguage(self):
        """Test getting, setting, and deleting a scalar predicate with an explicit language."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/')
        r = pymantic.RDF.Resource(graph, test_subject1)
        r['rdfs:label'] = 'foo'
        r['rdfs:label', 'fr'] = 'bar'
        self.assertEqual(r['rdfs:label'], rdflib.term.Literal('foo', lang='en'))
        self.assertEqual(r['rdfs:label', 'en'], rdflib.term.Literal('foo', lang='en'))
        self.assertEqual(r['rdfs:label', 'fr'], rdflib.term.Literal('bar', lang='fr'))
        del r['rdfs:label']
        self.assertEqual(r['rdfs:label'], None)
        self.assertEqual(r['rdfs:label', 'en'], None)
        self.assertEqual(r['rdfs:label', 'fr'], rdflib.term.Literal('bar', lang='fr'))        
    
    def testResourcePredicate(self):
        """Test instantiating a class when accessing a predicate."""
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        @pymantic.RDF.register_class('gr:PriceSpecification')
        class PriceSpecification(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject1 = rdflib.term.URIRef('http://example.com/offering')
        test_subject2 = rdflib.term.URIRef('http://example.com/price')
        graph = rdflib.graph.Graph()
        graph.add((test_subject1, Offering.resolve('rdf:type'),
                   Offering.resolve('gr:Offering')))
        graph.add((test_subject1, Offering.resolve('gr:hasPriceSpecification'),
                   test_subject2))
        graph.add((test_subject2, PriceSpecification.resolve('rdf:type'),
                   PriceSpecification.resolve('gr:PriceSpecification')))
        offering = Offering(graph, test_subject1)
        price_specification = PriceSpecification(graph, test_subject2)
        prices = set(offering['gr:hasPriceSpecification'])
        self.assertEqual(len(prices), 1)
        self.assert_(price_specification in prices)
    
    def testResourcePredicateAssignment(self):
        """Test assigning an instance of a resource to a predicate."""
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        @pymantic.RDF.register_class('gr:PriceSpecification')
        class PriceSpecification(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject1 = rdflib.term.URIRef('http://example.com/offering')
        test_subject2 = rdflib.term.URIRef('http://example.com/price')
        graph = rdflib.graph.Graph()
        graph.add((test_subject1, Offering.resolve('rdf:type'),
                   Offering.resolve('gr:Offering')))
        graph.add((test_subject2, PriceSpecification.resolve('rdf:type'),
                   PriceSpecification.resolve('gr:PriceSpecification')))
        offering = Offering(graph, test_subject1)
        price_specification = PriceSpecification(graph, test_subject2)
        before_prices = set(offering['gr:hasPriceSpecification'])
        self.assertEqual(len(before_prices), 0)
        offering['gr:hasPriceSpecification'] = price_specification
        after_prices = set(offering['gr:hasPriceSpecification'])
        self.assertEqual(len(after_prices), 1)
        self.assert_(price_specification in after_prices)
    
    def testNewResource(self):
        """Test creating a new resource."""
        graph = rdflib.graph.Graph()
        
        @pymantic.RDF.register_class('foaf:Person')
        class Person(pymantic.RDF.Resource):
            namespaces = {
                'foaf': 'http://xmlns.com/foaf/0.1/',
            }
        
        test_subject = rdflib.term.URIRef('http://example.com/')
        p = Person.new(graph, test_subject)
