import collections
from operator import itemgetter
from BTrees.IIBTree import IIBTree
from BTrees.IOBTree import IOSet
from BTrees.OOBTree import *

Triple = collections.namedtuple('Triple', 'subject predicate object')
Quad = collections.namedtuple('Quad', 'graph subject predicate object')

class Literal(tuple):
    """Literal(value, language, datatype)""" 

    __slots__ = () 

    _fields = ('value', 'language', 'datatype') 

    def __new__(_cls, value, language=None, datatype=None):
        return tuple.__new__(_cls, (value, language, datatype)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new Literal object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'Literal(value=%r, language=%r, datatype=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'value': t[0], 'language': t[1], 'datatype': t[2]} 

    def _replace(_self, **kwds):                                                                            
        'Return a new Literal object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, ('value', 'language', 'datatype'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    value = property(itemgetter(0))
    language = property(itemgetter(1))
    datatype = property(itemgetter(2))
    
class ChainingBTree(OOBTree):
    def __getitem__(self, key):
        try:
            return OOBTree.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)
    def __missing__(self, key):
        self[key] = value = ChainingBTree()
        return value
    def __reduce__(self):
        args = ChainingBTree(),
        return type(self), args, None, None, self.items()

class TripleGraph(object):
    
    def __init__(self):
        self._triples = OOTreeSet()
        self._spo = ChainingBTree()
    
    def add(self, triple):
        self._triples.insert(triple)
        self._spo[triple.subject][triple.predicate][triple.object] = triple
        
    def remove(self, triple):
        self._triples.remove(triple)
        del self._spo[triple.subject][triple.predicate][triple.object]
        
    def match(self, pattern):
        if pattern.subject:
            if pattern.predicate: # s, p, ???
                if pattern.object: # s, p, o
                    if pattern in self:
                        yield pattern
                    else: # s, p, ?var
                        for triple in self._spo[pattern.subject][pattern.predicate].values():
                            yield triple
            else: # s, ?var, ???
                if pattern.object: # s, ?var, o
                    for predicate in self._spo[pattern.graph][pattern.subject]:
                        for triple in self._ops[pattern.object][predicate][pattern.subject].values():
                            yield triple
                else: # s, ?var, ?var
                    for predicate in self._spo[pattern.subject]:
                        for triple in self._spo[pattern.subject][predicate].values():
                            yield triple
    
    def __contains__(self, item):
        return self._triples.has_key(item)
    