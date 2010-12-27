import collections
from operator import itemgetter

Triple = collections.namedtuple('Triple', 'subject predicate object')
Quad = collections.namedtuple('Quad', 'graph subject predicate object')

def q_as_t(quad):
    return Triple(quad.subject, quad.predicate, quad.object)

def t_as_q(graph, triple):
    return Quad(graph, triple.subject, triple.predicate, triple.object)

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
    
    interfaceName = "Literal"

class NamedNode(unicode):
    
    interfaceName = "NamedNode"
    
    @property
    def value(self):
        return self
    
    def __repr__(self):
        return 'NamedNode(' + super(NamedNode, self).__repr__() + ')'

class BlankNode(object):

    @property
    def value(self):
        return id(self)
    
    def __repr__(self):
        return 'BlankNode()'
    
from collections import defaultdict
def Index():
    return defaultdict(Index)
    
class TripleGraph(object):
    
    def __init__(self, graph_uri=None):
        self._uri = graph_uri
        self._triples = set()
        self._spo = Index()
        self._pos = Index()
        self._ops = Index()
        self._sop = Index()
        
    @property
    def uri(self):
        return self._uri
    
    def add(self, triple):
        self._triples.add(triple)
        self._spo[triple.subject][triple.predicate][triple.object] = triple
        self._pos[triple.predicate][triple.object][triple.subject] = triple
        self._ops[triple.object][triple.predicate][triple.subject] = triple
        self._sop[triple.subject][triple.object][triple.predicate] = triple
        
    def remove(self, triple):
        self._triples.remove(triple)
        del self._spo[triple.subject][triple.predicate][triple.object]
        del self._pos[triple.predicate][triple.object][triple.subject]
        del self._ops[triple.object][triple.predicate][triple.subject]
        del self._sop[triple.subject][triple.object][triple.predicate]
        
    def match(self, pattern):
        if pattern.subject:
            if pattern.predicate: # s, p, ???
                if pattern.object: # s, p, o
                    if pattern in self:
                        yield pattern
                else: # s, p, ?var
                    for triple in self._spo[pattern.subject][pattern.predicate].itervalues():
                        yield triple
            else: # s, ?var, ???
                if pattern.object: # s, ?var, o
                    for triple in self._sop[pattern.subject][pattern.object].itervalues():
                        yield triple
                else: # s, ?var, ?var
                    for predicate in self._spo[pattern.subject]:
                        for triple in self._spo[pattern.subject][predicate].itervalues():
                            yield triple
        elif pattern.predicate: # ?var, p, ???
            if pattern.object: # ?var, p, o
                for triple in self._ops[pattern.object][pattern.predicate].itervalues():
                    yield triple
            else: # ?var, p, ?var
                for object in self._pos[pattern.predicate]:
                    for triple in self._pos[pattern.predicate][object].itervalues():
                        yield triple
        elif pattern.object: # ?var, ?var, o
            for predicate in self._ops[pattern.object]:
                for triple in self._ops[pattern.object][predicate].itervalues():
                    yield triple
        else:
            for triple in self._triples:
                yield triple

    def __contains__(self, item):
        return item in self._triples
    
    def __len__(self):
        return len(self._triples)
    
class Dataset(object):
    
    def __init__(self):
        self._graphs = defaultdict(TripleGraph)
    
    def add(self, quad):
        self._graphs[quad.graph].add(q_as_t(quad))
        
    def remove(self, quad):
        self._graphs[quad.graph].remove(q_as_t(quad))
    
    def add_graph(self, graph, named=None):
        name = named or graph.uri
        if name:
            self._graphs[graph.uri] = graph
        else:
            raise ValueError("Graph must be named")
    
    def remove_graph(self, graph_or_uri):
        pass
    
    @property
    def graphs(self):
        return self._graphs.values()
    
    def match(self, item):
        if hasattr(item, "graph") and item.graph:
            quad = item
            matches = self._graphs[quad.graph].match(q_as_t(quad))
            for match in matches:
                yield t_as_q(quad.graph, match)
        else:
            triple = item
            for graph_uri, graph in self._graphs.iteritems():
                for match in graph.match(triple):
                    yield t_as_q(graph_uri, match)
    
    def __len__(self):
        return sum(len(g) for g in self.graphs)
    
    def __contains__(self, item):
        if hasattr(item, "graph"):
            if item.graph in self._graphs:
                graph = self._graphs[item.graph]
                return q_as_t(item) in graph
        else:
            for graph in self._graphs.itervalues():
                if item in graph:
                    return True
