"""Provides common classes and functions for modelling an RDF graph using
Python objects."""

import os.path
import urlparse
import re
import logging
from cStringIO import StringIO
from string import Template

import rdflib
from rdflib.URIRef import URIRef as Original_URIRef
import httplib2

import pymantic.uri_schemes as uri_schemes
import pymantic.util as util

log = logging.getLogger(__name__)

class SaneURIRef(Original_URIRef):
    __doc__ = Original_URIRef.__doc__ + '\n    Monkey-patched by pymantic.RDF import to have a sane __eq__ method.'
    
    def __eq__(self, other):
        if isinstance(other, Original_URIRef) or isinstance(other, str) or isinstance(other, unicode):
            return unicode(self) == unicode(other)
        return NotImplemented

rdflib.URIRef = SaneURIRef # Monkey patch!

def parse_curie(curie, namespaces):
    """
    Parses a CURIE within the context of the given namespaces. Will also accept
    explicit URIs and wrap them in an rdflib URIRef.
    
    Specifically:

    1) If the CURIE is not of the form [stuff] and the prefix is in the list of
       standard URIs, it is wrapped in a URIRef and returned unchanged.
    2) Otherwise, the CURIE is parsed by the rules of CURIE Syntax 1.0:
       http://www.w3.org/TR/2007/WD-curie-20070307/ The default namespace is the
       namespace keyed by the empty string in the namespaces dictionary.
    3) If the CURIE's namespace cannot be resolved, a ValueError is raised.
    """
    definitely_curie = False
    if curie[0] == '[' and curie[-1] == ']':
        curie = curie[1:-1]
        definitely_curie = True
    prefix, sep, reference = curie.partition(':')
    if not definitely_curie:
        if prefix in uri_schemes.schemes:
            return rdflib.URIRef(curie)
    if not reference and '' in namespaces:
        reference = prefix
        return namespaces[''][reference]
    if prefix in namespaces:
        return namespaces[prefix][reference]
    else:
        raise ValueError('Could not parse CURIE prefix %s from namespaces %s' % (prefix, namespaces))

def to_curie(uri, namespaces, seperator=":", explicit=False):
    """Converts a URI to a CURIE using the prefixes defined in namespaces. If
    there is no matching prefix, return the URI unchanged.
    
    namespaces - a dictionary of prefix -> namespace mappings.
    
    separator - the character to use as the separator between the prefix and
                the local name.
                
    explicit - if True and the URI can be abbreviated, wrap the abbreviated form
               in []s to indicate that it is definitely a CURIE."""
    for prefix, namespace in namespaces.items():
        if uri.startswith(namespace):
            if explicit:
                return '[' + uri.replace(namespace, prefix + seperator) + ']'
            else:
                return uri.replace(namespace, prefix + seperator)
    return uri

class MetaResource(type):
    """Aggregates namespace information.
    
    MetaResource makes namespaces a special attribute. namespaces is a
    dictionary that is the 'union' of all namespaces attributes on a
    class and its parents."""
    def __new__(cls, name, bases, dct):
        namespaces = {}
        for base in bases:
            if hasattr(base, 'namespaces'):
                namespaces.update(base.namespaces)
        if 'namespaces' in dct:
            for namespace in dct['namespaces']:
                namespaces[namespace] = rdflib.Namespace(
                    dct['namespaces'][namespace])
        dct['namespaces'] = namespaces
        return type.__new__(cls, name, bases, dct)

class ClassificationMismatchError(Exception):
    """Raised when an attempt is made to create a Subject for a resource that
    does not match its classification constraints."""
    pass

class URLRetrievalError(Exception):
    """Raised when an attempt to retrieve a resource returns a status other
    than 200 OK."""
    pass


class PredicateProperty(property):
    """
    Provides property-style access to the objects related to a Subject
    by a given predicate. If a language is specififed only values in that
    language will be returned.
    """

    def __init__(self, predicate, docstring=None, language=None):
        self.predicate = predicate
        self.language = language
        self.__doc__ = ("""Returns list of values for predicate :term:`%s`""" 
                        % (predicate,)) + (docstring or "")
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.language:
            value = [value for value in instance[self.predicate] 
                     if value.language == self.language]
        else:
            value = list(instance[self.predicate])
        return value

class ScalarPredicateProperty(PredicateProperty):
    """
    Provides property-style access to a predicate that can only have one value.
    If a language is specififed only values in that language will be returned.
    
    None is returned if there are no values, and ValueError raised if
    there are multiples.
    """

    def __init__(self, predicate, docstring=None, language=None):
        self.predicate = predicate
        self.language = language
        self.__doc__ = ("""Returns a value for predicate :term:`%s`

""" % (predicate,)) + (docstring or "")

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = util.one_or_none(
            super(ScalarPredicateProperty, self).__get__(instance, owner))
        return value

class ResourcePredicateProperty(property):
    """
    Provides property-style access to a predicate whose object is another
    resource. These yeild further Resources.
    
    cls is the class to be used to represent the resulting Resources. The
    Resources are provided as a generator. Any Resources that do not meet the
    classification constraints of cls (and, thus, raise a
    ClassificationMismatchError on instantiation) are silently omitted from the
    resulting generator.
    """
    def __init__(self, predicate, cls, omit=True, docstring=None):
        self.omit = omit
        self.predicate = predicate
        self.cls = cls
        self.__doc__ = ("""Returns a list of values for predicate :term:`%s` as :class:`~%s.%s`""" 
                        % (predicate,cls.__module__,cls.__name__)) + (docstring or "")
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return list(self._resources(instance, owner))
    
    def _resources(self, instance, owner):
        resource_generator = instance[self.predicate]
        for resource in resource_generator:
            seq = instance.graph.seq(resource)
            if seq:
                for seq_res in seq:
                    try:
                        yield self.cls(instance.graph, seq_res)
                    except ClassificationMismatchError:
                        if self.omit:
                            continue
                        else:
                            yield seq_res
            else:
                try:
                    yield self.cls(instance.graph, resource)
                except ClassificationMismatchError:
                    if self.omit:
                        continue
                    else:
                        yield seq_res

class ScalarResourcePredicateProperty(ResourcePredicateProperty):
    """
    Provides property-style access to a Resource predicate that can
    yield only one resource.
    """
    def __init__(self, predicate, cls, docstring=None):
        super(ScalarResourcePredicateProperty, self).__init__(predicate, cls)
        self.__doc__ = ("""Returns a value for predicate :term:`%s` as :class:`~%s.%s`""" % (predicate,cls.__module__,cls.__name__)) + (docstring or "")

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = util.one_or_none(list(
            super(ScalarResourcePredicateProperty, self).__get__(instance, owner)))
        return value

class ResourceReversePredicateProperty(property):
    """
    Provides property-style access to a Resource predicate that yields the
    Resource by following the predicate backwards, using the current subject
    as the object of the graph query.
    """
    def __init__(self, predicate, cls, docstring=None):
        self.predicate = predicate
        self.cls = cls
        self.__doc__ = ("""Returns list of subjects with predicate :term:`%s` as a :class:`~%s.%s` where the predicate is the current object""" % (predicate,cls.__module__,cls.__name__)) + (docstring or "")
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return list(self._resources(instance, owner))
    
    def _resources(self, instance, owner):
        resource_generator = instance.graph.subjects(
            instance.resolve(self.predicate), instance.subject)
        for resource in resource_generator:
            try:
                yield self.cls(instance.graph, resource)
            except ClassificationMismatchError:
                continue

class SelfReferentialPredicateProperty(property):
    """
    Provides property-style access to a Resource predicate that yields the same
    type of things as the predicate is on.
    """
    def __init__(self, predicate, docstring=None):
        self.predicate = predicate
        self.__doc__ = docstring
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self._resources(instance, owner)
    
    def _resources(self, instance, owner):
        resource_generator = instance[self.predicate]
        for resource in resource_generator:
            seq = instance.graph.seq(resource)
            if seq:
                for seq_res in seq:
                    try:
                        yield type(instance)(instance.graph, seq_res)
                    except ClassificationMismatchError:
                        continue
            else:
                try:
                    yield type(instance)(instance.graph, resource)
                except ClassificationMismatchError:
                    continue
                
class ScalarSelfReferentialPredicateProperty(SelfReferentialPredicateProperty):
    """
    Provides property-style access to a Resource predicate that yields the same
    type of things as the predicate is on.
    """
    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = util.one_or_none(list(
            super(ScalarSelfReferentialPredicateProperty, self).__get__(instance, owner)))
        return value

class InverseFunctionalLookupProperty(property):
    """Look up and return instances of another resource based on the values of a
    predicate on this resource using an Inverse Functional Property.
    
    lookup_method is expected to take (graph, value) and return an iteratable
    of results."""
    
    def __init__(self, predicate, lookup_method):
        self.predicate = predicate
        self.lookup_method = lookup_method
    
    def __get__(self, instance, owner):
        for value in instance[self.predicate]:
            for result in self.lookup_method(instance.graph, value):
                yield result

class Resource(object):
    """
    Represents a resource in the RDF graph.
    
    To inherit from this class, directly or indirectly, do the following:
    
    1) Define any namespaces needed to resolve any predicates or other CURIEs.
       These should go in an attribute called 'namespaces', which should contain a
       dictionary mapping prefixes to URLs. The namespaces dictionaries on all
       parents are merged together, with those at the bottom prioritized. The
       values in the dictionaries will automatically be turned into
       rdflib.Namespace objects.
    2) Resource supports automatic "classification", which can be used to ensure
       that Resources match certain criteria. Resource itself supports
       classification by predicate - set the classification_predicate attribute to
       the predicate to check (it defaults to rdf:type) and the
       classification_value attribute to the expected value. If
       classification_value is set, attempting to instantiate that Resource class
       for any subject without that value for the classification_predicate will
       result in an exception. Both classification_value and classification_predicate
       are parsed as CURIEs. Setting these also allows for all instances of the
       Resource in a graph to be enumerated through the in_graph method.
    3) Resource supports automatic retrieval of RDF descriptions for resources
       described by HTTP URLs. To enable this, set the retrieve_http attribute on
       the graph object to True. When instantiation of a Resource object for one
       of these resources fails due to classification constraints, rdfsandvich will
       attempt to resolve the failure by retrieving the contents of the HTTP URL
       and parsing them as RDF. To limit the URLs that will be queried, set the
       "retrieve_http_whitelist" or "retrieve_http_blacklist" attributes to a list
       of regular expressions. The whitelist receives priority.
    
    If you need some other method of classification, override the
    check_classification and in_graph methods.
    """
    
    __metaclass__ = MetaResource
    
    namespaces = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}
    
    classification_predicate = 'rdf:type'
    
    label = ScalarPredicateProperty('rdfs:label')
    
    rdf_type = PredicateProperty('rdf:type')
    
    def __init__(self, graph, subject):
        self.graph = graph
        self.subject = subject
        if not self.check_classification():
            parsed_subject = urlparse.urlparse(self.subject)
            if hasattr(graph, "retrieve_http") and graph.retrieve_http and \
               (not hasattr(graph, "retrieved_uris") or \
                self.subject not in graph.retrieved_uris) and \
               parsed_subject.scheme == 'http':
                if not hasattr(graph, "retrieved_uris"):
                    graph.retrieved_uris = set()
                if self.valid_retrieve_url(graph, self.subject):
                    if hasattr(graph, 'http_cache'):
                        cache = graph.http_cache
                    else:
                        cache = None
                    http = httplib2.Http(cache=cache)
                    resp, metadata = http.request(uri=str(self.subject),
                                                  method='GET')
                    if resp['status'] == '200':
                        publicID=urlparse.urlunparse((parsed_subject.scheme,
                                                      parsed_subject.netloc,
                                                      parsed_subject.path,
                                                      '', '', ''))
                        graph.parse(StringIO(metadata), publicID=publicID)
                        graph.retrieved_uris.add(self.subject)
                        if self.check_classification():
                            return
                    else:
                        log.warn('Could not retrieve %s: %s', self.subject,
                                 resp['status'])
            raise ClassificationMismatchError()
    
    def valid_retrieve_url(self, graph, url):
        if hasattr(graph, 'retrieve_http_whitelist'):
            for entry in graph.retrieve_http_whitelist:
                regex = re.compile(entry)
                if regex.match(url):
                    log.debug('%s passed whitelist under %s', url, entry)
                    return True
            return False
        if hasattr(graph, 'retrieve_http_blacklist'):
            for entry in graph.retrieve_http_blacklist:
                regex = re.compile(entry)
                if regex.match(url):
                    log.debug('%s failed blacklist under %s', url, entry)
                    return False
        return True
    
    def check_classification(self):
        if hasattr(self, 'classification_value'):
            classes = set(self[self.classification_predicate])
            if isinstance(self.classification_value, str) or\
               isinstance(self.classification_value, unicode):
                classification_values = [self.classification_value]
            else:
                classification_values = self.classification_value
            classification_values = set(self.resolve(classification_value) for\
                                     classification_value in\
                                     classification_values)
            if classification_values.intersection(classes):
                return True
        else:
            return True
    
    @classmethod
    def for_uri(cls, graph, identifier):
        """Basically the same as __init__, but handles wrapping identifier in
        a rdflib.URIRef if necessary and handles type errors more gracefully."""
        try:
            possible = cls(graph, identifier
                                  if isinstance(identifier, rdflib.URIRef)
                                  else rdflib.URIRef(identifier))
            return possible
        except ClassificationMismatchError:
            return None
    
    @classmethod
    def in_graph(cls, graph):
        """Iterates over all the instances of this Resource found in the
        specified graph. This requires that the Resource have a RDF_type
        specified."""
        if not cls.classification_value:
            raise Exception()
        for subj in graph.subjects(cls.resolve(cls.classification_predicate),
                                   cls.resolve(cls.classification_value)):
            try:
                yield cls(graph, subj)
            except ClassificationMismatchError:
                continue
    
    @classmethod
    def resolve(cls, key):
        """Use the classes namespaces to resolve a curie"""
        return parse_curie(key, cls.namespaces)
    
    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.subject == other.subject
        elif isinstance(other, rdflib.URIRef) or isinstance(other, str) or\
             isinstance(other, unicode):
            return self.subject == other 
        return NotImplemented
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.subject)
    
    def __getitem__(self, key):
        """Fetch predicates off this subject by key dictionary-style."""
        return self.objects(self.resolve(key))
    
    def __repr__(self):
        return "<%r: %r %r>" % (type(self), self.graph, self.subject)
    
    def __str__(self):
        if self.label:
            return self.label
        else:
            return self.subject
    
    def objects(self, predicate):
        """Fetch the objects for a predicate on this subject."""
        return self.graph.objects(self.subject, predicate)
    
    def predicate_objects(self):
        """Fetch all predicate, object pairs for this subject."""
        return self.graph.predicate_objects(self.subject)

class Property(Resource):
    """A rdf:Property."""
    
    classification_value = '[rdf:Property]'
