"""Provides common classes and functions for modelling an RDF graph using
Python objects."""

import os.path
import urlparse
import re
import logging
from cStringIO import StringIO
from string import Template

import pymantic.util as util
from pymantic.primitives import *

log = logging.getLogger(__name__)

class MetaResource(type):
    """Aggregates Prefix and scalar information."""

    _classes = {} # Map of RDF classes to Python classes.

    def __new__(cls, name, bases, dct):
        prefixes = PrefixMap()
        scalars = set()
        for base in bases:
            if hasattr(base, 'prefixes'):
                prefixes.update(base.prefixes)
            if hasattr(base, 'scalars'):
                scalars.update(base.scalars)
        if 'prefixes' in dct:
            for prefix in dct['prefixes']:
                prefixes[prefix] = Prefix(dct['prefixes'][prefix])
        dct['prefixes'] = prefixes
        if 'scalars' in dct:
            for scalar in dct['scalars']:
                scalars.add(parse_curie(scalar, prefixes))
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

    1) Bind prefixes to prefixes, and refer to them using CURIEs when
       accessing predicates or explicitly resolving CURIEs. Store a dictionary
       mapping prefixes to URLs in the 'prefixes' attribute of your subclass.
       The prefixes dictionaries on all parents are merged with this
       dictionary, and those at the bottom are prioritized. The values in the
       dictionaries will automatically be turned into rdflib Prefix objects.

    2) Define predicates as scalars. This asserts that a given predicate on this
       resource will only have zero or one value for a given language or
       data-type, or one reference to another resource. This is done using the
       'scalars' set, which is processed and merged just like prefixes.

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

    prefixes = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'}

    scalars = frozenset(('rdfs:label',))

    lang = 'en'

    rdf_classes = frozenset()

    def __init__(self, graph, subject):
        self.graph = graph
        if not isinstance(subject, NamedNode) and not isinstance(subject, BlankNode):
            subject = NamedNode(subject)
        self.subject = subject

    @classmethod
    def new(cls, graph, subject = None):
        """Add type information to the graph for a new instance of this Resource."""
        #for prefix, Prefix in cls.prefixes.iteritems():
            #graph.bind(prefix, Prefix)
        if subject is None:
            subject = BlankNode()
        if not isinstance(subject, NamedNode):
            subject = NamedNode(subject)
        for rdf_class in cls.rdf_classes:
            graph.add(Triple(subject, cls.resolve('rdf:type'), rdf_class))
        return cls(graph, subject)

    def erase(self):
        """Erase all tripes for this resource from the graph."""
        for triple in list(self.graph.match(self.subject, None, None)):
            self.graph.remove(triple)

    def is_a(self):
        """Test to see if the subject of this resource has all the necessary
        RDF classes applied to it."""
        if hasattr(self, 'rdf_classes'):
            for rdf_class in self.rdf_classes:
                if not any(self.graph.match(self.subject,
                                                   self.resolve('rdf:type'),
                                                   rdf_class)):
                    return False
        return True

    @classmethod
    def resolve(cls, key):
        """Use this class's prefixes to resolve a curie"""
        return parse_curie(key, cls.prefixes)

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.subject == other.subject
        elif isinstance(other, NamedNode) or isinstance(other, str) or\
             isinstance(other, unicode):
            return unicode(self.subject) == unicode(other)
        return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        else:
            return not eq

    def __hash__(self):
        return hash(self.subject)

    def bare_literals(self, predicate):
        """Objects for a predicate that are language-less, datatype-less Literals."""
        return [t.object for t in self.graph.match(self.subject, predicate, None) if\
                hasattr(t.object, 'language') and t.object.language is None and\
                hasattr(t.object, 'datatype') and t.object.datatype is None]

    def objects_by_lang(self, predicate, lang=None):
        """Objects for a predicate that match a specified language or, if
        language is None, have a language specified."""
        if lang:
            return [t.object for t in self.graph.match(self.subject, predicate, None) if\
                    hasattr(t.object, 'language') and lang_match(lang, t.object.language)]
        elif lang == '':
            return self.bare_literals(predicate)
        else:
            return [t.object for t in self.graph.match(self.subject, predicate, None) if\
                    hasattr(t.object, 'language') and t.object.language is not None]

    def objects_by_datatype(self, predicate, datatype=None):
        """Objects for a predicate that match a specified datatype or, if
        datatype is None, have a datatype specified."""
        if datatype:
            return [t.object for t in self.graph.match(self.subject, predicate, None) if\
                    hasattr(t.object, 'datatype') and t.object.datatype == datatype]
        elif datatype == '':
            return self.bare_literals(predicate)
        else:
            return [t.object for t in self.graph.match(self.subject, predicate, None) if\
                    hasattr(t.object, 'datatype') and t.object.datatype is not None]

    def objects_by_type(self, predicate, resource_class = None):
        """Objects for a predicate that are instances of a particular Resource
        subclass or, if resource_class is none, are Resources."""
        selected_objects = []
        for t in self.graph.match(self.subject, predicate, None):
            obj = t.object
            if isinstance(obj, BlankNode) or isinstance(obj, NamedNode):
                if resource_class is None or\
                   isinstance(self.classify(self.graph, obj),
                              resource_class):
                    selected_objects.append(obj)
        return selected_objects

    def objects(self, predicate):
        """All objects for a predicate."""
        return [t.object for t in self.graph.match(self.subject, predicate, None)]

    def object_of(self, predicate = None):
        """All subjects for which this resource is an object for the given
        predicate."""
        if predicate is None:
            for triple in self.graph.match(None, None, self.subject):
                yield (self.classify(self.graph, triple.subject), triple.predicate)
        else:
            predicate = self.resolve(predicate)
            for triple in self.graph.match(None, predicate, self.subject):
                yield self.classify(self.graph, triple.subject)

    def __getitem__(self, key):
        """Fetch predicates off this subject by key dictionary-style.

        This is the primary mechanism for predicate access. You can either
        provide a predicate name, as a complete URL or CURIE:

        resource['rdfs:label']
        resource['http://www.w3.org/2000/01/rdf-schema#label']

        Or a predicate name and a datatype or language:

        resource['rdfs:label', 'en']

        Passing in a value of None will result in all values for the predicate
        in question being returned."""
        predicate, objects = self._objects_for_key(key)
        if predicate not in self.scalars or (isinstance(key, tuple) and key[1] is None):
            def getitem_iter_results():
                for obj in objects:
                    yield self.classify(self.graph, obj)
            return getitem_iter_results()
        else:
            return self.classify(self.graph, util.one_or_none(objects))

    def get_scalar(self, key):
        """As __getitem__ access, but pretend the key is a scalar even if it isn't.

        Expect random exceptions if using this carelessly."""
        predicate, objects = self._objects_for_key(key)
        return self.classify(self.graph, util.one_or_none(objects))

    # Set item

    def __setitem__(self, key, value):
        """Sets objects for predicates for this subject by key dictionary-style.
        Returns 'self', for easy chaining.

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
        predicate, lang, datatype, rdf_class = self._interpret_key(key)
        value = literalize(self.graph, value, lang, datatype)
        if not isinstance(key, tuple):
            # Implicit specification.
            objects = self._objects_for_implicit_set(predicate, value)
        else:
            # Explicit specification.
            objects = self._objects_for_explicit_set(predicate, value, lang,
                                                     datatype, rdf_class)
        for obj in objects:
            self.graph.remove(Triple(self.subject, predicate, obj))
        if isinstance(value, frozenset):
            for obj in value:
                if isinstance(obj, Resource):
                    self.graph.add(Triple(self.subject, predicate, obj.subject))
                else:
                    self.graph.add(Triple(self.subject, predicate, obj))
        else:
            if isinstance(value, Resource):
                self.graph.add(Triple(self.subject, predicate, value.subject))
            else:
                self.graph.add(Triple(self.subject, predicate, value))

        return self

    # Delete item

    def __delitem__(self, key):
        """Deletes predicates for this subject by key dictionary-style.

        del resource[key] will always remove the same things from the graph as
        resource[key] returns."""
        predicate, objects = self._objects_for_key(key)
        for obj in objects:
            self.graph.remove(Triple(self.subject, predicate, obj))

    # Membership test

    def __contains__(self, predicate):
        """Uses the same logic as __getitem__ to determine if a predicate or
        filtered predicate is present for this object."""
        predicate, objects = self._objects_for_key(predicate)
        if objects:
            return True
        return False
    
    def __iter__(self):
        for s, p, o in self.graph.match(self.subject, None, None):
            yield p, o

    @classmethod
    def in_graph(cls, graph):
        """Iterate through all instances of this Resource in the graph."""
        subjects = set()
        for rdf_class in cls.rdf_classes:
            if not subjects:
                subjects.update([t.subject for t in graph.match(
                    None, cls.resolve('rdf:type'), rdf_class)])
            else:
                subjects.intersection_update([t.subject for t in graph.match(
                    None, cls.resolve('rdf:type'), rdf_class)])
        return set(cls(graph, subject) for subject in subjects)

    def __repr__(self):
        return "<%r: %s>" % (type(self), self.subject)

    def __str__(self):
        if self['rdfs:label']:
            return self['rdfs:label'].value
        else:
            return str(self.subject)

    @classmethod
    def classify(cls, graph, obj):
        """Classify an object into an appropriate registered class, or Resource.

        May create a new class if necessary that is a subclass of two or more
        registered Resource classes."""
        if obj is None:
            return None
        if isinstance(obj, Literal):
            return obj
        if any(graph.match(obj, cls.resolve('rdf:type'), None)):
            #retrieve_resource(graph, obj)
            if not any(graph.match(obj, cls.resolve('rdf:type'), None)):
                return Resource(graph, obj)
        types = frozenset([t.object for t in graph.match(
            obj, cls.resolve('rdf:type'), None)])
        python_classes = tuple(cls.__metaclass__._classes[t] for t in types if\
                               t in cls.__metaclass__._classes)
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

    def _interpret_key(self, key):
        """Break up a key into a predicate name and optional language or
        datatype specifier."""
        lang = None
        datatype = None
        rdf_class = None
        if isinstance(key, tuple) and len(key) >= 2:
            if key[1] is None:
                pass # All values are already None, do nothing.
            elif isinstance(key[1], MetaResource):
                rdf_class = key[1]
            elif is_language(key[1]):
                lang = key[1]
            else:
                datatype = self._interpret_datatype(key[1])
            predicate = self.resolve(key[0])
        else:
            predicate = self.resolve(key)
        if not isinstance(key, tuple) and predicate in self.scalars:
            lang = self.lang
        return predicate, lang, datatype, rdf_class

    def _interpret_datatype(self, datatype):
        """Deal with xsd:string vs. plain literal"""
        if datatype == '':
            return ''
        elif datatype == 'http://www.w3.org/2001/XMLSchema#string':
            return ''
        else:
            return datatype


    def _objects_for_key(self, key):
        """Find objects that are potentially interesting when doing normal
        dictionary key-style access - IE, __getitem__, __delitem__, __contains__,
        and pretty much everything but __setitem__."""
        predicate, lang, datatype, rdf_class = self._interpret_key(key)
        # log.debug("predicate: %r lang: %r datatype: %r rdf_class: %r", predicate, lang, datatype, rdf_class)
        if lang is None and datatype is None and rdf_class is None:
            objects = self.objects(predicate)
        elif lang:
            objects = self.objects_by_lang(predicate, lang)
            if not isinstance(key, tuple) and predicate in self.scalars and not objects:
                objects += self.objects_by_type(predicate)
                if not objects:
                    objects += self.objects_by_datatype(predicate)
                if not objects:
                    objects += self.bare_literals(predicate)
            if predicate not in self.scalars:
                objects += self.objects_by_type(predicate)
        elif datatype:
            objects = self.objects_by_datatype(predicate, datatype)
            if predicate not in self.scalars:
                objects += self.objects_by_type(predicate)
        elif rdf_class:
            objects = self.objects_by_type(predicate, rdf_class)
        elif lang == '' or datatype == '':
            objects = self.bare_literals(predicate)
        else:
            raise KeyError('Invalid key: ' + repr(key))
        return predicate, objects

    def _objects_for_implicit_set(self, predicate, value):
        """Find the objects that should be removed from the graph when doing a
        dictionary-style set with implicit type information."""
        if (isinstance(value, frozenset) or (isinstance(value, tuple) and\
                                             not isinstance(value, Literal))) and\
           predicate in self.scalars:
            raise ValueError('Cannot store sequences in scalars')
        elif predicate in self.scalars and isinstance(value, Literal)\
             and value.language:
            return self.objects_by_lang(predicate, value.language) +\
                   self.objects_by_datatype(predicate) +\
                   self.objects_by_type(predicate) +\
                   self.bare_literals(predicate)
        else:
            return self.objects(predicate)

    def _objects_for_explicit_set(self, predicate, value, lang, datatype, rdf_class):
        """Find the objects that should be removed from the graph when doing a
        dictionary-style set with explicit type information."""
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

    def copy(self, target_subject):
        """Create copies of all triples with this resource as their subject
        with the target subject as their subject. Returns a classified version
        of the target subject."""
        if not isinstance(target_subject, NamedNode) and\
           not isinstance(target_subject, BlankNode):
            target_subject = NamedNode(target_subject)
        for t in self.graph.match(self.subject, None, None):
            self.graph.add((target_subject, t.predicate, t.object))
        return self.classify(self.graph, target_subject)
    
    def as_(self, target_class):
        return target_class(self.graph, self.subject)
    

class List(Resource):
    """Convenience class for dealing with RDF lists.

    Requires considerable use of as_, due to the utter lack of type information
    on said lists."""
    scalars = frozenset(('rdf:first', 'rdf:rest'))

    def __iter__(self):
        """Iterating over lists works differently from normal Resources."""
        current = self
        while current.subject != self.resolve('rdf:nil'):
            yield current['rdf:first']
            current = current['rdf:rest']
            if current.subject != self.resolve('rdf:nil'):
                current = current.as_(type(self))
    
    @classmethod
    def is_list(cls, node, graph):
        """Determine if a given node is plausibly the subject of a list element."""
        return bool(list(graph.match(
            subject = node, predicate = cls.resolve('rdf:rest'))))
            

def literalize(graph, value, lang, datatype):
    """Convert either a value or a sequence of values to either a Literal or
    a Resource."""
    if isinstance(value, set) or isinstance(value, frozenset) or\
       isinstance(value, list) or (isinstance(value, tuple) and\
                                   not isinstance(value, Literal)):
        return frozenset(objectify_value(graph, v, lang, datatype) for v in value)
    else:
        return objectify_value(graph, value, lang, datatype)

def objectify_value(graph, value, lang = None, datatype = None):
    """Convert a single value into either a Literal or a Resource."""
    if isinstance(value, BlankNode) or isinstance(value, NamedNode):
        return Resource.classify(graph, value)
    elif isinstance(value, Literal) or isinstance(value, Resource):
        return value
    elif isinstance(value, str) or isinstance(value, unicode):
        return Literal(value, language = lang, datatype = datatype)
    else:
        return Literal(value)

def check_objects(graph, value, lang, datatype, rdf_class):
    """Determine that value or the things in values are appropriate for the
    specified explicit object access key."""
    if isinstance(value, frozenset) or (isinstance(value, tuple) and\
                                        not isinstance(value, Literal)):
        for v in value:
            if (lang and (not hasattr(v, 'language') or\
                          not lang_match(v.language, lang))) or \
               (datatype and v.datatype != datatype) or \
               (rdf_class and not isinstance(v, rdf_class)):
                return False
        return True
    else:
        return (lang and lang_match(value.language, lang)) or \
               (datatype and value.datatype == datatype) or \
               (rdf_class and isinstance(value, rdf_class))
