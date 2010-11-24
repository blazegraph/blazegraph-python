import datetime
import unittest

import rdflib.graph
import rdflib.term
import rdflib.namespace

import pymantic.RDF
import pymantic.util

from rdflib.namespace import XSD

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
    
    def testGetSetDelPredicateDatatype(self):
        """Test getting, setting and deleting a multi-value predicate with an explicit datatype."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/')
        r = pymantic.RDF.Resource(graph, test_subject1)
        now = datetime.datetime.now()
        then = datetime.datetime.now() - datetime.timedelta(days=1)
        number = 42
        r['rdfs:example', XSD['integer']] = set((number,))
        r['rdfs:example', XSD['dateTime']] = set((now, then,))
        example_values = set(r['rdfs:example', XSD['dateTime']])
        print example_values
        self.assert_(rdflib.term.Literal(now) in example_values)
        self.assert_(rdflib.term.Literal(then) in example_values)
        self.assert_(rdflib.term.Literal(number) not in example_values)
        self.assertEqual(len(example_values), 2)
        example_values = set(r['rdfs:example', XSD['integer']])
        self.assert_(rdflib.term.Literal(now) not in example_values)
        self.assert_(rdflib.term.Literal(then) not in example_values)
        self.assert_(rdflib.term.Literal(number) in example_values)
        self.assertEqual(len(example_values), 1)
        del r['rdfs:example', XSD['dateTime']]
        example_values = set(r['rdfs:example', XSD['dateTime']])
        self.assertEqual(len(example_values), 0)
        example_values = set(r['rdfs:example', XSD['integer']])
        self.assert_(rdflib.term.Literal(now) not in example_values)
        self.assert_(rdflib.term.Literal(then) not in example_values)
        self.assert_(rdflib.term.Literal(number) in example_values)
        self.assertEqual(len(example_values), 1)
    
    def testGetSetDelScalarPredicateDatatype(self):
        """Test getting, setting, and deleting a scalar predicate with an explicit datatype."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/')
        r = pymantic.RDF.Resource(graph, test_subject1)
        now = datetime.datetime.now()
        number = 42
        r['rdfs:label', XSD['integer']] = number
        self.assertEqual(r['rdfs:label', XSD['integer']],
                         rdflib.term.Literal(number, datatype=XSD['integer']))
        self.assertEqual(r['rdfs:label', XSD['dateTime']], None)
        self.assertEqual(r['rdfs:label'],
                         rdflib.term.Literal(number, datatype=XSD['integer']))
        r['rdfs:label', XSD['dateTime']] = now
        self.assertEqual(r['rdfs:label', XSD['dateTime']],
                         rdflib.term.Literal(now))
        self.assertEqual(r['rdfs:label', XSD['integer']], None)
        self.assertEqual(r['rdfs:label'], rdflib.term.Literal(now))
        del r['rdfs:label', XSD['integer']]
        self.assertEqual(r['rdfs:label', XSD['dateTime']], rdflib.term.Literal(now))
        self.assertEqual(r['rdfs:label', XSD['integer']], None)
        self.assertEqual(r['rdfs:label'], rdflib.term.Literal(now))
        del r['rdfs:label', XSD['dateTime']]
        self.assertEqual(r['rdfs:label'], None)
        r['rdfs:label', XSD['integer']] = number
        self.assertEqual(r['rdfs:label', XSD['integer']],
                         rdflib.term.Literal(number, datatype=XSD['integer']))
        self.assertEqual(r['rdfs:label', XSD['dateTime']], None)
        self.assertEqual(r['rdfs:label'],
                         rdflib.term.Literal(number, datatype=XSD['integer']))
        del r['rdfs:label']
        self.assertEqual(r['rdfs:label'], None)
    
    def testGetSetDelPredicateType(self):
        """Test getting, setting and deleting a multi-value predicate with an explicit expected RDF Class."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/offering')
        test_subject2 = rdflib.term.URIRef('http://example.com/aposi1')
        test_subject3 = rdflib.term.URIRef('http://example.com/aposi2')
        test_subject4 = rdflib.term.URIRef('http://example.com/possip1')
        
        NAMESPACES = {
            'gr': 'http://purl.org/goodrelations/',
        }
        
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = NAMESPACES
        
        @pymantic.RDF.register_class('gr:ActualProductOrServiceInstance')
        class ActualProduct(pymantic.RDF.Resource):
            namespaces = NAMESPACES
            
        @pymantic.RDF.register_class('gr:ProductOrServicesSomeInstancesPlaceholder')
        class PlaceholderProduct(pymantic.RDF.Resource):
            namespaces = NAMESPACES
        
        offering = Offering.new(graph, test_subject1)
        aposi1 = ActualProduct.new(graph, test_subject2)
        aposi2 = ActualProduct.new(graph, test_subject3)
        possip1 = PlaceholderProduct.new(graph, test_subject4)
        offering['gr:includes', ActualProduct] = set((aposi1, aposi2,))
        offering['gr:includes', PlaceholderProduct] = set((possip1,))
        example_values = set(offering['gr:includes', ActualProduct])
        self.assert_(aposi1 in example_values)
        self.assert_(aposi2 in example_values)
        self.assert_(possip1 not in example_values)
        self.assertEqual(len(example_values), 2)
        example_values = set(offering['gr:includes', PlaceholderProduct])
        self.assert_(aposi1 not in example_values)
        self.assert_(aposi2 not in example_values)
        self.assert_(possip1 in example_values)
        self.assertEqual(len(example_values), 1)
        del offering['gr:includes', ActualProduct]
        example_values = set(offering['gr:includes', ActualProduct])
        self.assertEqual(len(example_values), 0)
        example_values = set(offering['gr:includes', PlaceholderProduct])
        self.assert_(aposi1 not in example_values)
        self.assert_(aposi2 not in example_values)
        self.assert_(possip1 in example_values)
        self.assertEqual(len(example_values), 1)
    
    def testGetSetDelScalarPredicateType(self):
        """Test getting, setting, and deleting a scalar predicate with an explicit language."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/offering')
        test_subject2 = rdflib.term.URIRef('http://example.com/aposi')
        test_subject4 = rdflib.term.URIRef('http://example.com/possip')
        
        NAMESPACES = {
            'gr': 'http://purl.org/goodrelations/',
        }
        
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = NAMESPACES
            
            scalars = frozenset(('gr:includes',))
        
        @pymantic.RDF.register_class('gr:ActualProductOrServiceInstance')
        class ActualProduct(pymantic.RDF.Resource):
            namespaces = NAMESPACES
            
        @pymantic.RDF.register_class('gr:ProductOrServicesSomeInstancesPlaceholder')
        class PlaceholderProduct(pymantic.RDF.Resource):
            namespaces = NAMESPACES
        
        offering = Offering.new(graph, test_subject1)
        aposi1 = ActualProduct.new(graph, test_subject2)
        possip1 = PlaceholderProduct.new(graph, test_subject4)
        offering['gr:includes', ActualProduct] = aposi1
        self.assertEqual(aposi1, offering['gr:includes', ActualProduct])
        self.assertEqual(None, offering['gr:includes', PlaceholderProduct])
        self.assertEqual(aposi1, offering['gr:includes'])
        offering['gr:includes', PlaceholderProduct] = possip1
        self.assertEqual(None, offering['gr:includes', ActualProduct])
        self.assertEqual(possip1, offering['gr:includes', PlaceholderProduct])
        self.assertEqual(possip1, offering['gr:includes'])
        del offering['gr:includes', ActualProduct]
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        self.assertEqual(possip1, offering['gr:includes', PlaceholderProduct])
        del offering['gr:includes', PlaceholderProduct]
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        self.assertEqual(offering['gr:includes', PlaceholderProduct], None)
        offering['gr:includes', ActualProduct] = aposi1
        self.assertEqual(aposi1, offering['gr:includes', ActualProduct])
        self.assertEqual(None, offering['gr:includes', PlaceholderProduct])
        self.assertEqual(aposi1, offering['gr:includes'])
        del offering['gr:includes']
        self.assertEqual(None, offering['gr:includes', ActualProduct])
        self.assertEqual(None, offering['gr:includes', PlaceholderProduct])
        self.assertEqual(None, offering['gr:includes'])

    def testSetMixedScalarPredicate(self):
        """Test getting and setting a scalar predicate with mixed typing."""
        graph = rdflib.graph.Graph()
        test_subject1 = rdflib.term.URIRef('http://example.com/offering')
        test_subject2 = rdflib.term.URIRef('http://example.com/aposi')
        
        NAMESPACES = {
            'gr': 'http://purl.org/goodrelations/',
        }
        
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = NAMESPACES
            
            scalars = frozenset(('gr:includes',))
        
        @pymantic.RDF.register_class('gr:ActualProductOrServiceInstance')
        class ActualProduct(pymantic.RDF.Resource):
            namespaces = NAMESPACES
        
        offering = Offering.new(graph, test_subject1)
        aposi1 = ActualProduct.new(graph, test_subject2)
        test_en = rdflib.Literal('foo', lang='en')
        test_fr = rdflib.Literal('le foo', lang='fr')
        test_dt = rdflib.Literal(42)
        
        offering['gr:includes'] = aposi1
        self.assertEqual(offering['gr:includes'], aposi1)
        offering['gr:includes'] = test_dt
        self.assertEqual(offering['gr:includes'], test_dt)
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        offering['gr:includes'] = test_en
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        self.assertEqual(offering['gr:includes', XSD['integer']], None)
        self.assertEqual(offering['gr:includes'], test_en)
        self.assertEqual(offering['gr:includes', 'en'], test_en)
        self.assertEqual(offering['gr:includes', 'fr'], None)
        offering['gr:includes'] = test_fr
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        self.assertEqual(offering['gr:includes', XSD['integer']], None)
        self.assertEqual(offering['gr:includes'], test_en)
        self.assertEqual(offering['gr:includes', 'en'], test_en)
        self.assertEqual(offering['gr:includes', 'fr'], test_fr)
        offering['gr:includes'] = aposi1
        self.assertEqual(offering['gr:includes'], aposi1)
        self.assertEqual(offering['gr:includes', XSD['integer']], None)
        self.assertEqual(offering['gr:includes', 'en'], None)
        self.assertEqual(offering['gr:includes', 'fr'], None)
    
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
        
    def testGetAllResourcesInGraph(self):
        """Test iterating over all of the resources in a graph with a
        particular RDF type."""
        
        @pymantic.RDF.register_class('gr:Offering')
        class Offering(pymantic.RDF.Resource):
            namespaces = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        graph = rdflib.ConjunctiveGraph()
        test_subject_base = rdflib.term.URIRef('http://example.com/')
        for i in range(10):
            graph.add((rdflib.term.URIRef(test_subject_base + str(i)),
                       Offering.resolve('rdf:type'),
                       Offering.resolve('gr:Offering')))
        offerings = Offering.in_graph(graph)
        self.assertEqual(len(offerings), 10)
        for i in range(10):
            this_subject = rdflib.term.URIRef(test_subject_base + str(i))
            offering = Offering(graph, this_subject)
            self.assert_(offering in offerings)
            
    def testBack(self):
        """Test following a predicate backwards."""
        
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
        
        graph = rdflib.ConjunctiveGraph()
        offering1 = Offering.new(graph, 'http://example.com/offering1')
        offering2 = Offering.new(graph, 'http://example.com/offering2')
        offering3 = Offering.new(graph, 'http://example.com/offering3')
        price1 = PriceSpecification.new(graph, 'http://example.com/price1')
        price2 = PriceSpecification.new(graph, 'http://example.com/price2')
        price3 = PriceSpecification.new(graph, 'http://example.com/price3')
        offering1['gr:hasPriceSpecification'] = set((price1, price2, price3,))
        offering2['gr:hasPriceSpecification'] = set((price2, price3,))
        self.assertEqual(set(price1.back('gr:hasPriceSpecification')),
                         set((offering1,)))
        self.assertEqual(set(price2.back('gr:hasPriceSpecification')),
                         set((offering1,offering2,)))
        self.assertEqual(set(price3.back('gr:hasPriceSpecification')),
                         set((offering1,offering2,)))
