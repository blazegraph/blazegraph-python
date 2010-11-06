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

def is_language(lang):
    """Is something a valid XML language?"""
    return True

def lang_match(lang1, lang2):
    if lang1 is None or lang2 is None:
        return True
    return lang1 == lang2

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

# TODO: Is it possible that, rather than inheriting from Resource,
#  MetaResource should perform all the necessary bindings?

class MetaResource(type):
    """Aggregates namespace information.
    
    MetaResource makes namespaces a special attribute. namespaces is a
    dictionary that is the 'union' of all namespaces attributes on a
    class and its parents."""
    
    _classes = {} # Map of RDF classes to Python classes.
    
    def __new__(cls, name, bases, dct):
        namespaces = {}
        scalars = set()
        for base in bases:
            if hasattr(base, 'namespaces'):
                namespaces.update(base.namespaces)
            if hasattr(base, 'scalars'):
                scalars.update(base.scalars)
        if 'namespaces' in dct:
            for namespace in dct['namespaces']:
                namespaces[namespace] = rdflib.Namespace(
                    dct['namespaces'][namespace])
        dct['namespaces'] = namespaces
        if 'scalars' in dct:
            for scalar in dct['scalars']:
                scalars.add(parse_curie(scalar, namespaces))
        dct['scalars'] = scalars
        return type.__new__(cls, name, bases, dct)

def register_class(rdf_type):
    def _register_class(python_class):
        rdf_class = python_class.resolve(rdf_type)
        MetaResource._classes[python_class.resolve(rdf_type)] = python_class
        python_class.rdf_classes = frozenset((python_class.resolve(rdf_type),))
        return python_class
    return _register_class

class URLRetrievalError(Exception):
    """Raised when an attempt to retrieve a resource returns a status other
    than 200 OK."""
    pass

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
    
    scalars = ['rdfs:label',]
    
    lang = 'en'
        
    def __init__(self, graph, subject):
        self.graph = graph
        if not isinstance(subject, rdflib.URIRef):
            subject = rdflib.URIRef(subject)
        self.subject = subject
        if not self.check_classification():
            retrieve_resource(graph, subject)
            if not self.check_classification():
                raise ClassificationMismatchError()
    
    def check_classification(self):
        if hasattr(self, 'rdf_classes'):
            for rdf_class in self.rdf_classes:
                if (self.subject, self.resolve('rdf:type'), rdf_class) not in self.graph:
                    return False
        return True
        
    @classmethod
    def resolve(cls, key):
        """Use the classes namespaces to resolve a curie"""
        return parse_curie(key, cls.namespaces)
    
    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.subject == other.subject
        elif isinstance(other, rdflib.URIRef) or isinstance(other, str) or\
             isinstance(other, unicode):
            return unicode(self.subject) == unicode(other)
        return NotImplemented
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.subject)
    
    def safe_graph_add(self, predicate, obj, fallback_lang, fallback_datatype):
        """Ensures that we're adding appropriate objects to an RDF graph."""
        if not isinstance(obj, rdflib.Literal) and not isinstance(obj, rdflib.URIRef):
            obj = rdflib.Literal(obj, lang=fallback_lang, datatype=fallback_datatype)
        self.graph.add((self.subject, predicate, obj))

    def objects_by(self, predicate, lang, datatype):
        return [obj for obj in self.graph.objects(self.subject, predicate) if\
                (hasattr(obj, 'language') and lang_match(lang, obj.language)) or
                not hasattr(obj, 'language')]
    
    def __getitem__(self, key):
        """Fetch predicates off this subject by key dictionary-style."""
        lang = None
        datatype = None
        if isinstance(key, tuple) and len(key) >= 2:
            if is_language(key[1]):
                lang = key[1]
            else:
                datatype = key[1]
            key = key[0]
        if lang is None and datatype is None:
            lang = self.lang
        predicate = self.resolve(key)
        objects = self.objects_by(predicate, lang, datatype)
        if predicate in self.scalars:
            return self.classify(self.graph, util.one_or_none(objects))
        else:
            def getitem_iter_results():
                for obj in objects:
                    yield self.classify(self.graph, obj)
            return getitem_iter_results()
    
    # Set item
    
    def __setitem__(self, key, value):
        """Sets predicates for this subject by key dictionary-style."""
        lang = None
        datatype = None
        if isinstance(key, tuple) and len(key) >= 2:
            if is_language(key[1]):
                lang = key[1]
            else:
                datatype = key[1]
            key = key[0]
        if lang is None and datatype is None:
            lang = self.lang
        predicate = self.resolve(key)
        objects = self.objects_by(predicate, lang, datatype)
        for obj in objects:
            self.graph.remove((self.subject, predicate, obj))
        
        if predicate in self.scalars:
            self.safe_graph_add(predicate, value, lang, datatype)
        else:
            if isinstance(value, list) or isinstance(value, tuple) or\
               isinstance(value, set) or isinstance(value, frozenset):
                for v in value:
                    self.safe_graph_add(predicate, v, lang, datatype)
            else:
                self.safe_graph_add(predicate, v, lang, datatype)
    
    # Delete item
    
    # Membership test
    
    # Iteration
    
    def __repr__(self):
        return "<%r: %s>" % (type(self), self.subject)
    
    def __str__(self):
        if self['rdfs:label']:
            return self['rdfs:label']
        else:
            return self.subject
    
    @classmethod
    def classify(cls, graph, obj):
        if isinstance(obj, rdflib.Literal):
            return obj
        if (obj, cls.resolve('rdf:type'), None) not in graph:
            retrieve_resource(graph, obj)
            if (obj, cls.resolve('rdf:type'), None) not in graph:
                return Resource(graph, obj)
        types = frozenset(graph.objects(obj, cls.resolve('rdf:type')))
        python_classes = tuple(cls.__metaclass__._classes[t] for t in types)
        if len(python_classes) == 0:
            return Resource(graph, obj)
        elif len(python_classes) == 1:
            return python_classes[0](graph, obj)
        else:
            if types not in cls.__metaclass__._classes:
                the_class = cls.__metaclass__.__new__(
                    cls.__metaclass__, ''.join(python_class.__name__ for\
                                               python_class in python_classes),
                    python_classes, {'_autocreate': True})
                cls.__metaclass__._classes[types] = the_class
                the_class.rdf_classes = frozenset(types)
            return cls.__metaclass__._classes[types](graph, obj)

def retrieve_resource(graph, subject):
    """Attempt to retrieve an RDF resource VIA HTTP."""
    parsed_subject = urlparse.urlparse(self.subject)
    publicID=urlparse.urlunparse((parsed_subject.scheme,
                                  parsed_subject.netloc,
                                  parsed_subject.path,
                                  '', '', ''))
    if hasattr(graph, "retrieve_http") and graph.retrieve_http and \
       (not hasattr(graph, "retrieved_uris") or \
        publicID not in graph.retrieved_uris) and \
       (parsed_subject.scheme == 'http' or parsed_subject.scheme == 'https'):
        if not hasattr(graph, "retrieved_uris"):
            graph.retrieved_uris = set()
        if _valid_retrieve_url(graph, self.subject):
            if hasattr(graph, 'http_cache'):
                cache = graph.http_cache
            else:
                cache = None
            http = httplib2.Http(cache=cache)
            resp, content = http.request(uri=str(publicID), method='GET')
            if resp['status'] == '200':
                graph.parse(StringIO(content), publicID=publicID)
                graph.retrieved_uris.add(publicID)
            else:
                log.debug('Could not retrieve %s: %s', publicID, resp['status'])

def _valid_retrieve_url(graph, url):
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

class Property(Resource):
    """A rdf:Property."""
    
    classification_value = '[rdf:Property]'
