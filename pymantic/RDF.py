"""Provides common classes and functions for modelling an RDF graph using
Python objects."""

import os.path
import urlparse
import re
import logging
from cStringIO import StringIO
from string import Template

import rdflib
from rdflib.term import URIRef as Original_URIRef
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

#rdflib.term.URIRef = SaneURIRef # Monkey patch!

def is_language(lang):
    """Is something a valid XML language?"""
    if isinstance(lang, rdflib.URIRef):
        return False
    return True

def lang_match(lang1, lang2):
    """Determines if two languages are, in fact, the same language.
    
    Eg: en is the same as en-us and en-uk."""
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
            return rdflib.term.URIRef(curie)
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
    """Aggregates namespace and scalar information."""
    
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
                namespaces[namespace] = rdflib.namespace.Namespace(
                    dct['namespaces'][namespace])
        dct['namespaces'] = namespaces
        if 'scalars' in dct:
            for scalar in dct['scalars']:
                scalars.add(parse_curie(scalar, namespaces))
        dct['scalars'] = frozenset(scalars)
        return type.__new__(cls, name, bases, dct)

def register_class(rdf_type):
    """Register a class for automatic instantiation VIA Resource.classify."""
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
    """Provides necessary context and utility methods for accessing a Resource
    in an RDF graph. Resources can be used as-is, but are likely somewhat
    unwieldy, since all predicate access must be by complete URL and produces
    sets. By subclassing Resource, you can take advantage of a number of
    quality-of-life features:
    
    1) Bind namespaces to prefixes, and refer to them using CURIEs when
       accessing predicates or explicitly resolving CURIEs. Store a dictionary
       mapping prefixes to URLs in the 'namespaces' attribute of your subclass.
       The namespaces dictionaries on all parents are merged with this
       dictionary, and those at the bottom are prioritized. The values in the
       dictionaries will automatically be turned into rdflib Namespace objects.
    
    2) Define predicates as scalars. This asserts that a given predicate on this
       resource will only have zero or one value for a given language or
       data-type, or one reference to another resource. This is done using the
       'scalars' set, which is processed and merged just like namespaces.
        
    3) Automatically classify certain RDF types as certain Resource subclasses.
       Decorate your class with the pymantic.RDF.register_class decorator, and
       provide it with the corresponding RDF type. Whenever this type is
       encountered when retrieving objects from a predicate it will
       automatically be instantiated as your class rather than a generic Resource.
       
       RDF allows for resources to have multiple types. When a resource is
       encountered with two or more types that have different python classes
       registered for them, a new python class is created. This new class
       subclasses all applicable registered classes.
       
       If you want to perform this classification manually (to, for example,
       instantiate the correct class for an arbitrary URI), you can do so by
       calling Resource.classify. You can also create a new instance of a
       Resource by calling .new on a subclass.
       
    Automatic retrieval of resources with no type information is currently
    implemented here, but is likely to be refactored into a separate persistence
    layer in the near future."""
    
    __metaclass__ = MetaResource
    
    namespaces = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}
    
    scalars = frozenset(('rdfs:label',))
        
    lang = 'en'
    
    rdf_classes = frozenset()
    
    def __init__(self, graph, subject):
        self.graph = graph
        if not isinstance(subject, rdflib.term.Node):
            subject = rdflib.term.URIRef(subject)
        self.subject = subject
        if not self.check_classification():
            retrieve_resource(graph, subject)
            if not self.check_classification():
                raise ClassificationMismatchError()
    
    @classmethod
    def new(cls, graph, subject):
        """Create a new instance of this Resource."""
        if not isinstance(subject, rdflib.term.Node):
            subject = rdflib.URIRef(subject)
        for rdf_class in cls.rdf_classes:
            graph.add((subject, cls.resolve('rdf:type'), rdf_class))
        return cls(graph, subject)
    
    def check_classification(self):
        if hasattr(self, 'rdf_classes'):
            for rdf_class in self.rdf_classes:
                if (self.subject, self.resolve('rdf:type'), rdf_class) not in self.graph:
                    return False
        return True
        
    @classmethod
    def resolve(cls, key):
        """Use this class's namespaces to resolve a curie"""
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
    
    def interpret_key(self, key):
        """Break up a key into a predicate name and optional language or
        datatype specifier."""
        lang = None
        datatype = None
        rdf_class = None
        if isinstance(key, tuple) and len(key) >= 2:
            if isinstance(key[1], MetaResource):
                rdf_class = key[1]
            elif is_language(key[1]):
                lang = key[1]
            else:
                datatype = key[1]
            key = key[0]
        else:
            lang = self.lang
        predicate = self.resolve(key)
        return predicate, lang, datatype, rdf_class

    def objects_by_lang(self, predicate, lang=None):
        """Objects for a predicate that match a specified language."""
        if lang:
            return [obj for obj in self.graph.objects(self.subject, predicate) if\
                    (hasattr(obj, 'language') and lang_match(lang, obj.language))]
        else:
            return [obj for obj in self.graph.objects(self.subject, predicate) if\
                    hasattr(obj, 'language') and obj.language is not None]
    
    def objects_by_datatype(self, predicate, datatype=None):
        if datatype:
            return [obj for obj in self.graph.objects(self.subject, predicate) if\
                    (hasattr(obj, 'datatype') and obj.datatype == datatype)]
        else:
            return [obj for obj in self.graph.objects(self.subject, predicate) if\
                    hasattr(obj, 'datatype') and obj.datatype is not None]
    
    def objects_by_type(self, predicate, rdf_class = None):
        selected_objects = []
        for obj in self.graph.objects(self.subject, predicate):
            if isinstance(obj, rdflib.BNode) or isinstance(obj, rdflib.URIRef):
                if rdf_class is None or\
                   isinstance(self.classify(self.graph, obj), rdf_class):
                    selected_objects.append(obj)
        return selected_objects

    def objects(self, predicate):
        return [obj for obj in self.graph.objects(self.subject, predicate)]
    
    def __getitem__(self, key):
        """Fetch predicates off this subject by key dictionary-style.
        
        This is the primary mechanism for predicate access. You can either
        provide a predicate name, as a complete URL or CURIE:
        
        resource['rdfs:label']
        resource['http://www.w3.org/2000/01/rdf-schema#label']
        
        Or a predicate name and a datatype or language:
        
        resource['rdfs:label', 'en']"""
        predicate, lang, datatype, rdf_class = self.interpret_key(key)
        if lang:
            objects = self.objects_by_lang(predicate, lang)
            if predicate not in self.scalars or (not objects and not isinstance(key, tuple)):
                objects += self.objects_by_type(predicate)
        elif datatype:
            objects = self.objects_by_datatype(predicate, datatype)
            if predicate not in self.scalars:
                objects += self.objects_by_type(predicate)
        elif rdf_class:
            objects = self.objects_by_type(predicate, rdf_class)
        else:
            raise KeyError('Invalid key: %s', key)
        if predicate in self.scalars:
            return self.classify(self.graph, util.one_or_none(objects))
        else:
            def getitem_iter_results():
                for obj in objects:
                    yield self.classify(self.graph, obj)
            return getitem_iter_results()
    
    # Set item
    
    def __setitem__(self, key, value):
        """Sets objects for predicates for this subject by key dictionary-style.
        
        1) Setting a predicate without a filter replaces the set of all objects
           for that predicate. The exception is assigning a Literal object with
           a language to a scalar predicate. This will only replace objects that
           share its language, though any resources or datatyped literals will
           be removed.
           
        2) Setting a predicate with a filter will only replace objects that
           match the specified filter, including all resource references for
           language or datatype filters. The exception is scalars, where
           datatyped literals and objects will replace everything else, and
           language literals can co-exist but will replace all datatyped
           literals.
        
        3) Attempting to set a literal that doesn't make sense will raise a
           ValueError. For example, including an english or dateTime literal
           when setting a predicate's objects using a French language filter
           will result in a ValueError. Object references are always acceptable
           to include."""
        predicate, lang, datatype, rdf_class = self.interpret_key(key)
        value = literalize(self.graph, value, lang, datatype)
        if not isinstance(key, tuple):
            # Implicit specification.
            objects = self._objects_for_implicit_set(predicate, value)
        else:
            # Explicit specification.
            objects = self._objects_for_explicit_set(predicate, value, lang,
                                                     datatype, rdf_class)
        for obj in objects:
            self.graph.remove((self.subject, predicate, obj))
        if isinstance(value, frozenset) or isinstance(value, tuple):
            for obj in value:
                if isinstance(obj, Resource):
                    self.graph.add((self.subject, predicate, obj.subject))
                else:
                    self.graph.add((self.subject, predicate, obj))
        else:
            if isinstance(value, Resource):
                self.graph.add((self.subject, predicate, value.subject))
            else:
                self.graph.add((self.subject, predicate, value))
    
    # Delete item
    
    def __delitem__(self, key):
        """Deletes predicates for this subject by key dictionary-style.
        
        del resource[key] will always remove the same things from the graph as
        resource[key] returns."""
        predicate, lang, datatype, rdf_class = self.interpret_key(key)
        if lang:
            objects = self.objects_by_lang(predicate, lang)
            if predicate not in self.scalars or not objects:
                objects += self.objects_by_type(predicate)
        elif datatype:
            objects = self.objects_by_datatype(predicate, datatype)
            if predicate not in self.scalars or not objects:
                objects += self.objects_by_type(predicate)
        elif rdf_class:
            objects = self.objects_by_type(predicate, rdf_class)
        else:
            raise KeyError('Invalid key: %s', key)
        for obj in objects:
            self.graph.remove((self.subject, predicate, obj))
   
    # Membership test
    
    @classmethod
    def in_graph(cls, graph):
        """Iterate through all instances of this Resource in the graph."""
        subjects = set()
        for rdf_class in cls.rdf_classes:
            if not subjects:
                subjects.update(graph.subjects(cls.resolve('rdf:type'), rdf_class))
            else:
                subjects.intersection_update(
                    graph.subjects(cls.resolve('rdf:type'), rdf_class))
        return set(cls(graph, subject) for subject in subjects)
    
    def __repr__(self):
        return "<%r: %s>" % (type(self), self.subject)
    
    def __str__(self):
        if self['rdfs:label']:
            return self['rdfs:label']
        else:
            return self.subject
    
    @classmethod
    def classify(cls, graph, obj):
        """Classify an object into an appropriate registered class, or Resource.
        
        May create a new class if necessary that is a subclass of two or more
        registered Resource classes."""
        if obj is None:
            return None
        if isinstance(obj, rdflib.term.Literal):
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
    
    def _objects_for_implicit_set(self, predicate, value):
        if (isinstance(value, frozenset) or isinstance(value, tuple)) and\
           predicate in self.scalars:
            raise ValueError('Cannot store sequences in scalars')
        elif predicate in self.scalars and isinstance(value, rdflib.Literal)\
             and value.language:
            return self.objects_by_lang(predicate, value.language) +\
                   self.objects_by_datatype(predicate) +\
                   self.objects_by_type(predicate)
        else:
            return self.objects(predicate)
    
    def _objects_for_explicit_set(self, predicate, value, lang, datatype, rdf_class):
        if not check_objects(self.graph, value, lang, datatype, rdf_class):
            raise ValueError('Improper value provided.')
        if lang and predicate in self.scalars:
            return self.objects_by_lang(predicate, lang) +\
                   self.objects_by_datatype(predicate) +\
                   self.objects_by_type(predicate)
        elif lang and predicate not in self.scalars:
            return self.objects_by_lang(predicate, lang) +\
                   self.objects_by_type(predicate)
        elif predicate in self.scalars:
            return self.objects(predicate)
        elif datatype:
            return self.objects_by_datatype(predicate, datatype) +\
                   self.objects_by_type(predicate)
        elif rdf_class:
            return self.objects_by_type(predicate, rdf_class)

def literalize(graph, value, lang, datatype):
    """Convert either a value or a sequence of values to either a Literal or
    a Resource."""
    if isinstance(value, set) or isinstance(value, frozenset):
        return frozenset(objectify_value(graph, v, lang, datatype) for v in value)
    elif isinstance(value, list) or isinstance(value, tuple):
        # Eventually return tuple.
        raise NotImplemented('Still need to do Seq handling.')
    else:
        return objectify_value(graph, value, lang, datatype)

def objectify_value(graph, value, lang = None, datatype = None):
    """Convert a single value into either a Literal or a Resource."""
    if isinstance(value, rdflib.BNode) or isinstance(value, rdflib.URIRef):
        return Resource.classify(graph, value)
    elif isinstance(value, rdflib.Literal) or isinstance(value, Resource):
        return value
    elif isinstance(value, str) or isinstance(value, unicode):
        return rdflib.Literal(value, lang = lang, datatype = datatype)
    else:
        return rdflib.Literal(value)

def check_objects(graph, value, lang, datatype, rdf_class):
    """Determine that value or the things in values are appropriate for the
    specified explicit object access key."""
    if isinstance(value, frozenset) or isinstance(value, tuple):
        for v in value:
            if (lang and not lang_match(v.language, lang)) or \
               (datatype and v.datatype != datatype) or \
               (rdf_class and not isinstance(v, rdf_class)):
                return False
        return True
    else:
        return (lang and lang_match(value.language, lang)) or \
               (datatype and value.datatype == datatype) or \
               (rdf_class and isinstance(value, rdf_class))

def retrieve_resource(graph, subject):
    """Attempt to retrieve an RDF resource VIA HTTP."""
    parsed_subject = urlparse.urlparse(subject)
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
