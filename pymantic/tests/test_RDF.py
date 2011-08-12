import datetime
import unittest

import pymantic.rdf
import pymantic.util
from pymantic.primitives import *

XSD = Prefix('http://www.w3.org/2001/XMLSchema#')

RDF = Prefix("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

class TestRDF(unittest.TestCase):
    def tearDown(self):
        pymantic.rdf.MetaResource._classes = {}
    
    def testCurieURI(self):
        """Test CURIE parsing of explicit URIs."""
        test_ns = {'http': Prefix('WRONG!'),
                   'urn': Prefix('WRONG!'),}
        self.assertEqual(pymantic.rdf.parse_curie('http://oreilly.com', test_ns),
                         NamedNode('http://oreilly.com'))
        self.assertEqual(pymantic.rdf.parse_curie('urn:isbn:1234567890123', test_ns),
                         NamedNode('urn:isbn:1234567890123'))
    
    def testCurieDefaultPrefix(self):
        """Test CURIE parsing of CURIEs in the default Prefix."""
        test_ns = {'': Prefix('foo/'),
                   'wrong': Prefix('WRONG!')}
        self.assertEqual(pymantic.rdf.parse_curie('bar', test_ns),
                         NamedNode('foo/bar'))
        self.assertEqual(pymantic.rdf.parse_curie('[bar]', test_ns),
                         NamedNode('foo/bar'))
        self.assertEqual(pymantic.rdf.parse_curie('baz', test_ns),
                         NamedNode('foo/baz'))
        self.assertEqual(pymantic.rdf.parse_curie('[aap]', test_ns),
                         NamedNode('foo/aap'))
    
    def testCurieprefixes(self):
        """Test CURIE parsing of CURIEs in non-default prefixes."""
        test_ns = {'': Prefix('WRONG!'),
                   'foo': Prefix('foobly/'),
                   'bar': Prefix('bardle/'),
                   'http': Prefix('reallybadidea/'),}
        self.assertEqual(pymantic.rdf.parse_curie('foo:aap', test_ns),
                         NamedNode('foobly/aap'))
        self.assertEqual(pymantic.rdf.parse_curie('[bar:aap]', test_ns),
                         NamedNode('bardle/aap'))
        self.assertEqual(pymantic.rdf.parse_curie('[foo:baz]', test_ns),
                         NamedNode('foobly/baz'))
        self.assertEqual(pymantic.rdf.parse_curie('bar:baz', test_ns),
                         NamedNode('bardle/baz'))
        self.assertEqual(pymantic.rdf.parse_curie('[http://oreilly.com]', test_ns),
                         NamedNode('reallybadidea///oreilly.com'))
    
    def testCurieNoSuffix(self):
        """Test CURIE parsing of CURIEs with no suffix."""
        pass
    
    def testUnparseableCuries(self):
        """Test some CURIEs that shouldn't parse."""
        test_ns = {'foo': Prefix('WRONG!'),}
        self.assertRaises(ValueError, pymantic.rdf.parse_curie, '[bar]', test_ns)
        self.assertRaises(ValueError, pymantic.rdf.parse_curie, 'bar', test_ns)
        self.assertRaises(ValueError, pymantic.rdf.parse_curie, 'bar:baz', test_ns)
        self.assertRaises(ValueError, pymantic.rdf.parse_curie, '[bar:baz]', test_ns)
    
    def testMetaResourceNothingUseful(self):
        """Test applying a MetaResource to a class without anything it uses."""
        class Foo(object):
            __metaclass__ = pymantic.rdf.MetaResource
    
    def testMetaResourceprefixes(self):
        """Test the handling of prefixes by MetaResource."""
        class Foo(object):
            __metaclass__ = pymantic.rdf.MetaResource
            prefixes = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        
        self.assertEqual(Foo.prefixes, {'foo': Prefix('bar'),
                                          'baz': Prefix('garply'),
                                          'meme': Prefix('lolcatz!'),})
    
    def testMetaResourcePrefixInheritance(self):
        """Test the composition of Prefix dictionaries by MetaResource."""
        class Foo(object):
            __metaclass__ = pymantic.rdf.MetaResource
            prefixes = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        class Bar(Foo):
            prefixes = {'allyourbase': 'arebelongtous!', 'bunny': 'pancake',}
        self.assertEqual(Foo.prefixes, {'foo': Prefix('bar'),
                                          'baz': Prefix('garply'),
                                          'meme': Prefix('lolcatz!'),})
        self.assertEqual(Bar.prefixes, {'foo': Prefix('bar'),
                                          'baz': Prefix('garply'),
                                          'meme': Prefix('lolcatz!'),
                                          'allyourbase': Prefix('arebelongtous!'),
                                          'bunny': Prefix('pancake'),})
    
    def testMetaResourcePrefixInheritanceReplacement(self):
        """Test the composition of Prefix dictionaries by MetaResource where
        some prefixes on the parent get replaced."""
        class Foo(object):
            __metaclass__ = pymantic.rdf.MetaResource
            prefixes = {'foo': 'bar', 'baz': 'garply', 'meme': 'lolcatz!',}
        class Bar(Foo):
            prefixes = {'allyourbase': 'arebelongtous!', 'bunny': 'pancake',
                          'foo': 'notbar', 'baz': 'notgarply',}
        self.assertEqual(Foo.prefixes, {'foo': Prefix('bar'),
                                          'baz': Prefix('garply'),
                                          'meme': Prefix('lolcatz!'),})
        self.assertEqual(Bar.prefixes, {'foo': Prefix('notbar'),
                                          'baz': Prefix('notgarply'),
                                          'meme': Prefix('lolcatz!'),
                                          'allyourbase': Prefix('arebelongtous!'),
                                          'bunny': Prefix('pancake'),})

    def testResourceEquality(self):
        graph = Graph()
        otherGraph = Graph()
        testResource = pymantic.rdf.Resource(graph, 'foo')
        self.assertEqual(testResource, pymantic.rdf.Resource(
            graph, 'foo'))
        self.assertEqual(testResource, NamedNode('foo'))
        self.assertEqual(testResource, 'foo')
        self.assertNotEqual(testResource, pymantic.rdf.Resource(
            graph, 'bar'))
        self.assertEqual(testResource, pymantic.rdf.Resource(
            otherGraph, 'foo'))
        self.assertNotEqual(testResource, NamedNode('bar'))
        self.assertNotEqual(testResource, 'bar')
        self.assertNotEqual(testResource, 42)
    
    def testClassification(self):
        """Test classification of a resource."""
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject = NamedNode('http://example.com/athing')
        graph = Graph()
        graph.add(Triple(test_subject, Offering.resolve('rdf:type'),
                         Offering.resolve('gr:Offering')))
        offering = pymantic.rdf.Resource.classify(graph, test_subject)
        self.assert_(isinstance(offering, Offering))
    
    def testMulticlassClassification(self):
        """Test classification of a resource that matches multiple registered
        classes."""
        @pymantic.rdf.register_class('foaf:Organization')
        class Organization(pymantic.rdf.Resource):
            prefixes = {
                'foaf': 'http://xmlns.com/foaf/0.1/',
            }
        
        @pymantic.rdf.register_class('foaf:Group')
        class Group(pymantic.rdf.Resource):
            prefixes = {
                'foaf': 'http://xmlns.com/foaf/0.1/',
            }
        
        test_subject1 = NamedNode('http://example.com/aorganization')
        test_subject2 = NamedNode('http://example.com/agroup')
        test_subject3 = NamedNode('http://example.com/aorgandgroup')
        graph = Graph()
        graph.add(Triple(test_subject1, Organization.resolve('rdf:type'),
                         Organization.resolve('foaf:Organization')))
        graph.add(Triple(test_subject2, Group.resolve('rdf:type'),
                         Group.resolve('foaf:Group')))
        graph.add(Triple(test_subject3, Organization.resolve('rdf:type'),
                         Organization.resolve('foaf:Organization')))
        graph.add(Triple(test_subject3, Organization.resolve('rdf:type'),
                         Organization.resolve('foaf:Group')))
        organization = pymantic.rdf.Resource.classify(graph, test_subject1)
        group = pymantic.rdf.Resource.classify(graph, test_subject2)
        both = pymantic.rdf.Resource.classify(graph, test_subject3)
        self.assert_(isinstance(organization, Organization))
        self.assertFalse(isinstance(organization, Group))
        self.assertFalse(isinstance(group, Organization))
        self.assert_(isinstance(group, Group))
        self.assert_(isinstance(both, Organization))
        self.assert_(isinstance(both, Group))

    def testStr(self):
        """Test str-y serialization of Resources."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/aorganization')
        test_label = Literal('Test Label', language='en')
        graph.add(Triple(test_subject1,
                         pymantic.rdf.Resource.resolve('rdfs:label'),
                         test_label))
        r = pymantic.rdf.Resource(graph, test_subject1)
        self.assertEqual(r['rdfs:label'], test_label)
        self.assertEqual(str(r), test_label.value)
    
    def testGetSetDelPredicate(self):
        """Test getting, setting, and deleting a multi-value predicate."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        r['rdfs:example'] = set(('foo', 'bar'))
        example_values = set(r['rdfs:example'])
        print example_values
        self.assert_(Literal('foo') in example_values)
        self.assert_(Literal('bar') in example_values)
        self.assertEqual(len(example_values), 2)
        del r['rdfs:example']
        example_values = set(r['rdfs:example'])
        self.assertEqual(len(example_values), 0)
    
    def testGetSetDelScalarPredicate(self):
        """Test getting, setting, and deleting a scalar predicate."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        r['rdfs:label'] = 'foo'
        self.assertEqual(r['rdfs:label'], Literal('foo', language='en'))
        del r['rdfs:label']
        self.assertEqual(r['rdfs:label'], None)
    
    def testGetSetDelPredicateLanguage(self):
        """Test getting, setting and deleting a multi-value predicate with an explicit language."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        r['rdfs:example', 'en'] = set(('baz',))
        r['rdfs:example', 'fr'] = set(('foo', 'bar'))
        example_values = set(r['rdfs:example', 'fr'])
        self.assert_(Literal('foo', language='fr') in example_values)
        self.assert_(Literal('bar', language='fr') in example_values)
        self.assert_(Literal('baz', language='en') not in example_values)
        self.assertEqual(len(example_values), 2)
        example_values = set(r['rdfs:example', 'en'])
        self.assert_(Literal('foo', language='fr') not in example_values)
        self.assert_(Literal('bar', language='fr') not in example_values)
        self.assert_(Literal('baz', language='en') in example_values)
        self.assertEqual(len(example_values), 1)
        del r['rdfs:example', 'fr']
        example_values = set(r['rdfs:example', 'fr'])
        self.assertEqual(len(example_values), 0)
        example_values = set(r['rdfs:example', 'en'])
        self.assert_(Literal('foo', language='fr') not in example_values)
        self.assert_(Literal('bar', language='fr') not in example_values)
        self.assert_(Literal('baz', language='en') in example_values)
        self.assertEqual(len(example_values), 1)
    
    def testGetSetDelScalarPredicateLanguage(self):
        """Test getting, setting, and deleting a scalar predicate with an explicit language."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        r['rdfs:label'] = 'foo'
        r['rdfs:label', 'fr'] = 'bar'
        self.assertEqual(r['rdfs:label'], Literal('foo', language='en'))
        self.assertEqual(r['rdfs:label', 'en'], Literal('foo', language='en'))
        self.assertEqual(r['rdfs:label', 'fr'], Literal('bar', language='fr'))
        del r['rdfs:label']
        self.assertEqual(r['rdfs:label'], None)
        self.assertEqual(r['rdfs:label', 'en'], None)
        self.assertEqual(r['rdfs:label', 'fr'], Literal('bar', language='fr'))
    
    def testGetSetDelPredicateDatatype(self):
        """Test getting, setting and deleting a multi-value predicate with an explicit datatype."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        now = datetime.datetime.now()
        then = datetime.datetime.now() - datetime.timedelta(days=1)
        number = 42
        r['rdfs:example', XSD('integer')] = set((number,))
        r['rdfs:example', XSD('dateTime')] = set((now, then,))
        example_values = set(r['rdfs:example', XSD('dateTime')])
        print example_values
        self.assert_(Literal(now) in example_values)
        self.assert_(Literal(then) in example_values)
        self.assert_(Literal(number) not in example_values)
        self.assertEqual(len(example_values), 2)
        example_values = set(r['rdfs:example', XSD('integer')])
        self.assert_(Literal(now) not in example_values)
        self.assert_(Literal(then) not in example_values)
        self.assert_(Literal(number) in example_values)
        self.assertEqual(len(example_values), 1)
        del r['rdfs:example', XSD('dateTime')]
        example_values = set(r['rdfs:example', XSD('dateTime')])
        self.assertEqual(len(example_values), 0)
        example_values = set(r['rdfs:example', XSD('integer')])
        self.assert_(Literal(now) not in example_values)
        self.assert_(Literal(then) not in example_values)
        self.assert_(Literal(number) in example_values)
        self.assertEqual(len(example_values), 1)
    
    def testGetSetDelScalarPredicateDatatype(self):
        """Test getting, setting, and deleting a scalar predicate with an explicit datatype."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        now = datetime.datetime.now()
        number = 42
        r['rdfs:label', XSD('integer')] = number
        self.assertEqual(r['rdfs:label', XSD('integer')],
                         Literal(number, datatype=XSD('integer')))
        self.assertEqual(r['rdfs:label', XSD('dateTime')], None)
        self.assertEqual(r['rdfs:label'],
                         Literal(number, datatype=XSD('integer')))
        r['rdfs:label', XSD('dateTime')] = now
        self.assertEqual(r['rdfs:label', XSD('dateTime')], Literal(now))
        self.assertEqual(r['rdfs:label', XSD('integer')], None)
        self.assertEqual(r['rdfs:label'], Literal(now))
        del r['rdfs:label', XSD('integer')]
        self.assertEqual(r['rdfs:label', XSD('dateTime')], Literal(now))
        self.assertEqual(r['rdfs:label', XSD('integer')], None)
        self.assertEqual(r['rdfs:label'], Literal(now))
        del r['rdfs:label', XSD('dateTime')]
        self.assertEqual(r['rdfs:label'], None)
        r['rdfs:label', XSD('integer')] = number
        self.assertEqual(r['rdfs:label', XSD('integer')],
                         Literal(number, datatype=XSD('integer')))
        self.assertEqual(r['rdfs:label', XSD('dateTime')], None)
        self.assertEqual(r['rdfs:label'], Literal(number, datatype=XSD('integer')))
        del r['rdfs:label']
        self.assertEqual(r['rdfs:label'], None)
    
    def testGetSetDelPredicateType(self):
        """Test getting, setting and deleting a multi-value predicate with an explicit expected RDF Class."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/offering')
        test_subject2 = NamedNode('http://example.com/aposi1')
        test_subject3 = NamedNode('http://example.com/aposi2')
        test_subject4 = NamedNode('http://example.com/possip1')
        
        shared_prefixes = {
            'gr': 'http://purl.org/goodrelations/',
        }
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = shared_prefixes
        
        @pymantic.rdf.register_class('gr:ActualProductOrServiceInstance')
        class ActualProduct(pymantic.rdf.Resource):
            prefixes = shared_prefixes
            
        @pymantic.rdf.register_class('gr:ProductOrServicesSomeInstancesPlaceholder')
        class PlaceholderProduct(pymantic.rdf.Resource):
            prefixes = shared_prefixes
        
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
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/offering')
        test_subject2 = NamedNode('http://example.com/aposi')
        test_subject4 = NamedNode('http://example.com/possip')
        
        shared_prefixes = {
            'gr': 'http://purl.org/goodrelations/',
        }
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = shared_prefixes
            
            scalars = frozenset(('gr:includes',))
        
        @pymantic.rdf.register_class('gr:ActualProductOrServiceInstance')
        class ActualProduct(pymantic.rdf.Resource):
            prefixes = shared_prefixes
            
        @pymantic.rdf.register_class('gr:ProductOrServicesSomeInstancesPlaceholder')
        class PlaceholderProduct(pymantic.rdf.Resource):
            prefixes = shared_prefixes
        
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
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/offering')
        test_subject2 = NamedNode('http://example.com/aposi')
        
        shared_prefixes = {
            'gr': 'http://purl.org/goodrelations/',
        }
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = shared_prefixes
            
            scalars = frozenset(('gr:includes',))
        
        @pymantic.rdf.register_class('gr:ActualProductOrServiceInstance')
        class ActualProduct(pymantic.rdf.Resource):
            prefixes = shared_prefixes
        
        offering = Offering.new(graph, test_subject1)
        aposi1 = ActualProduct.new(graph, test_subject2)
        test_en = Literal('foo', language='en')
        test_fr = Literal('le foo', language='fr')
        test_dt = Literal('42', datatype = XSD('integer'))
        
        offering['gr:includes'] = aposi1
        self.assertEqual(offering['gr:includes'], aposi1)
        offering['gr:includes'] = test_dt
        self.assertEqual(offering['gr:includes'], test_dt)
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        offering['gr:includes'] = test_en
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        self.assertEqual(offering['gr:includes', XSD('integer')], None)
        self.assertEqual(offering['gr:includes'], test_en)
        self.assertEqual(offering['gr:includes', 'en'], test_en)
        self.assertEqual(offering['gr:includes', 'fr'], None)
        offering['gr:includes'] = test_fr
        self.assertEqual(offering['gr:includes', ActualProduct], None)
        self.assertEqual(offering['gr:includes', XSD('integer')], None)
        self.assertEqual(offering['gr:includes'], test_en)
        self.assertEqual(offering['gr:includes', 'en'], test_en)
        self.assertEqual(offering['gr:includes', 'fr'], test_fr)
        offering['gr:includes'] = aposi1
        self.assertEqual(offering['gr:includes'], aposi1)
        self.assertEqual(offering['gr:includes', XSD('integer')], None)
        self.assertEqual(offering['gr:includes', 'en'], None)
        self.assertEqual(offering['gr:includes', 'fr'], None)
    
    def testResourcePredicate(self):
        """Test instantiating a class when accessing a predicate."""
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        @pymantic.rdf.register_class('gr:PriceSpecification')
        class PriceSpecification(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject1 = NamedNode('http://example.com/offering')
        test_subject2 = NamedNode('http://example.com/price')
        graph = Graph()
        graph.add(Triple(test_subject1, Offering.resolve('rdf:type'),
                         Offering.resolve('gr:Offering')))
        graph.add(Triple(test_subject1, Offering.resolve('gr:hasPriceSpecification'),
                         test_subject2))
        graph.add(Triple(test_subject2, PriceSpecification.resolve('rdf:type'),
                         PriceSpecification.resolve('gr:PriceSpecification')))
        offering = Offering(graph, test_subject1)
        price_specification = PriceSpecification(graph, test_subject2)
        prices = set(offering['gr:hasPriceSpecification'])
        self.assertEqual(len(prices), 1)
        self.assert_(price_specification in prices)
    
    def testResourcePredicateAssignment(self):
        """Test assigning an instance of a resource to a predicate."""
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        @pymantic.rdf.register_class('gr:PriceSpecification')
        class PriceSpecification(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        test_subject1 = NamedNode('http://example.com/offering')
        test_subject2 = NamedNode('http://example.com/price')
        graph = Graph()
        graph.add(Triple(test_subject1, Offering.resolve('rdf:type'),
                         Offering.resolve('gr:Offering')))
        graph.add(Triple(test_subject2, PriceSpecification.resolve('rdf:type'),
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
        graph = Graph()
        
        @pymantic.rdf.register_class('foaf:Person')
        class Person(pymantic.rdf.Resource):
            prefixes = {
                'foaf': 'http://xmlns.com/foaf/0.1/',
            }
        
        test_subject = NamedNode('http://example.com/')
        p = Person.new(graph, test_subject)
        
    def testGetAllResourcesInGraph(self):
        """Test iterating over all of the resources in a graph with a
        particular RDF type."""
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        graph = Graph()
        test_subject_base = NamedNode('http://example.com/')
        for i in range(10):
            graph.add(Triple(NamedNode(test_subject_base + str(i)),
                             Offering.resolve('rdf:type'),
                             Offering.resolve('gr:Offering')))
        offerings = Offering.in_graph(graph)
        self.assertEqual(len(offerings), 10)
        for i in range(10):
            this_subject = NamedNode(test_subject_base + str(i))
            offering = Offering(graph, this_subject)
            self.assert_(offering in offerings)
    
    def testContained(self):
        """Test in against a multi-value predicate."""
        graph = Graph()
        test_subject1 = NamedNode('http://example.com/')
        r = pymantic.rdf.Resource(graph, test_subject1)
        r['rdfs:example'] = set(('foo', 'bar'))
        self.assert_('rdfs:example' in r)
        self.assertFalse(('rdfs:example', 'en') in r)
        self.assertFalse(('rdfs:example', 'fr') in r)
        self.assertFalse('rdfs:examplefoo' in r)
        del r['rdfs:example']
        self.assertFalse('rdfs:example' in r)
        self.assertFalse(('rdfs:example', 'en') in r)
        self.assertFalse(('rdfs:example', 'fr') in r)
        self.assertFalse('rdfs:examplefoo' in r)
        r['rdfs:example', 'fr'] = 'le foo'
            
    def testBack(self):
        """Test following a predicate backwards."""
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
            
        @pymantic.rdf.register_class('gr:PriceSpecification')
        class PriceSpecification(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        graph = Graph()
        offering1 = Offering.new(graph, 'http://example.com/offering1')
        offering2 = Offering.new(graph, 'http://example.com/offering2')
        offering3 = Offering.new(graph, 'http://example.com/offering3')
        price1 = PriceSpecification.new(graph, 'http://example.com/price1')
        price2 = PriceSpecification.new(graph, 'http://example.com/price2')
        price3 = PriceSpecification.new(graph, 'http://example.com/price3')
        offering1['gr:hasPriceSpecification'] = set((price1, price2, price3,))
        offering2['gr:hasPriceSpecification'] = set((price2, price3,))
        self.assertEqual(set(price1.object_of(predicate='gr:hasPriceSpecification')),
                         set((offering1,)))
        self.assertEqual(set(price2.object_of(predicate='gr:hasPriceSpecification')),
                         set((offering1,offering2,)))
        self.assertEqual(set(price3.object_of(predicate='gr:hasPriceSpecification')),
                         set((offering1,offering2,)))
    
    def testGetAllValues(self):
        """Test getting all values for a predicate."""
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        en = Literal('foo', language='en')
        fr = Literal('bar', language='fr')
        es = Literal('baz', language='es')
        xsdstring = Literal('aap')
        xsddecimal = Literal('9.95', datatype=XSD('decimal'))
        graph = Graph()
        offering = Offering.new(graph, 'http://example.com/offering')
        
        offering['gr:description'] = set((en, fr, es,))
        self.assertEqual(frozenset(offering['gr:description']), frozenset((en,fr,es,)))
        self.assertEqual(frozenset(offering['gr:description', 'en']), frozenset((en,)))
        self.assertEqual(frozenset(offering['gr:description', 'fr']), frozenset((fr,)))
        self.assertEqual(frozenset(offering['gr:description', 'es']), frozenset((es,)))
        self.assertEqual(frozenset(offering['gr:description', None]),
                         frozenset((en, fr, es,)))
        
        offering['gr:description'] = set((xsdstring, xsddecimal,))
        self.assertEqual(frozenset(offering['gr:description', '']),
                         frozenset((xsdstring,)))
        self.assertEqual(frozenset(offering['gr:description', XSD('string')]),
                         frozenset((xsdstring,)))
        self.assertEqual(frozenset(offering['gr:description', XSD('decimal')]),
                         frozenset((xsddecimal,)))
        self.assertEqual(frozenset(offering['gr:description', None]),
                         frozenset((xsdstring, xsddecimal,)))
        
        offering['gr:description'] = set((en, fr, es, xsdstring, xsddecimal,))
        self.assertEqual(frozenset(offering['gr:description']), frozenset((en, fr, es, xsdstring, xsddecimal,)))
        self.assertEqual(frozenset(offering['gr:description', 'en']), frozenset((en,)))
        self.assertEqual(frozenset(offering['gr:description', 'fr']), frozenset((fr,)))
        self.assertEqual(frozenset(offering['gr:description', 'es']), frozenset((es,)))
        self.assertEqual(frozenset(offering['gr:description', '']),
                         frozenset((xsdstring,)))
        self.assertEqual(frozenset(offering['gr:description', XSD('string')]),
                         frozenset((xsdstring,)))
        self.assertEqual(frozenset(offering['gr:description', XSD('decimal')]),
                         frozenset((xsddecimal,)))
        self.assertEqual(frozenset(offering['gr:description', None]),
                         frozenset((en, fr, es, xsdstring, xsddecimal,)))
    
    def testGetAllValuesScalar(self):
        """Test getting all values for a predicate."""
        
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
            
            scalars = frozenset(('gr:description',))
        
        en = Literal('foo', language='en')
        fr = Literal('bar', language='fr')
        es = Literal('baz', language='es')
        graph = Graph()
        offering = Offering.new(graph, 'http://example.com/offering')
        offering['gr:description'] = en
        offering['gr:description'] = fr
        offering['gr:description'] = es
        self.assertEqual(offering['gr:description'], en)
        self.assertEqual(offering['gr:description', 'en'], en)
        self.assertEqual(offering['gr:description', 'fr'], fr)
        self.assertEqual(offering['gr:description', 'es'], es)
        self.assertEqual(frozenset(offering['gr:description', None]),
                         frozenset((en, fr, es,)))
    
    def testErase(self):
        """Test erasing an object from the graph."""
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
            
            scalars = frozenset(('gr:name',))
        
        graph = Graph()
        offering1 = Offering.new(graph, 'http://example.com/offering1')
        offering2 = Offering.new(graph, 'http://example.com/offering2')
        offering1['gr:name'] = 'Foo'
        offering1['gr:description'] = set(('Baz', 'Garply',))
        offering2['gr:name'] = 'Bar'
        offering2['gr:description'] = set(('Aap', 'Mies',))
        self.assert_(offering1.is_a())
        self.assert_(offering2.is_a())
        offering1.erase()
        self.assertFalse(offering1.is_a())
        self.assert_(offering2.is_a())
        self.assertFalse(offering1['gr:name'])
        self.assertFalse(frozenset(offering1['gr:description']))
        self.assertEqual(offering2['gr:name'], Literal('Bar', language='en'))
    
    def testUnboundClass(self):
        """Test classifying objects with one or more unbound classes."""
        @pymantic.rdf.register_class('gr:Offering')
        class Offering(pymantic.rdf.Resource):
            prefixes = {
                'gr': 'http://purl.org/goodrelations/',
            }
        
        graph = Graph()
        funky_class = NamedNode('http://example.com/AFunkyClass')
        funky_subject = NamedNode('http://example.com/aFunkyResource')
        
        offering1 = Offering.new(graph, 'http://example.com/offering1')
        graph.add(Triple(offering1.subject, RDF('type'), funky_class))
        self.assertEqual(type(pymantic.rdf.Resource.classify(graph, offering1.subject)),
                         Offering)
        graph.add(Triple(funky_subject, RDF('type'), funky_class))
        self.assertEqual(type(pymantic.rdf.Resource.classify(graph, funky_subject)),
                         pymantic.rdf.Resource)
