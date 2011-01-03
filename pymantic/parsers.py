__all__ = ['NTripleParser', 'parse_ntriples']

from rdflib.parser import Parser
from rdflib.plugins.parsers.ntriples import NTriplesParser, ParseError, r_wspace, r_wspaces, r_tail
from rdflib import ConjunctiveGraph

class NQSink(object):
    def __init__(self, graph):
        # NQuads is a context-aware format.
        self.graph = ConjunctiveGraph(store = graph.store)

    def quad(self, s, p, o, c):
        self.graph.get_context(c).add((s, p, o))


class NQParser(Parser):
    """parser for the nquads format, often stored with the .nq extension

    See http://sw.deri.org/2008/07/n-quads/"""

    def __init__(self):
        super(NQParser, self).__init__()

    def parse(self, source, sink, baseURI=None):
        f = source.getByteStream() # TODO getCharacterStream?
        parser = NQuadsParser(NQSink(sink))
        parser.parse(f)
        f.close()

class NQuadsParser(NTriplesParser):
    """An N-Quads Parser.

    Usage::

         p = NQuadsParser(sink=MySink())
         sink = p.parse(f) # file; use parsestring for a string
    """

    def parseline(self):
        self.eat(r_wspace)
        if (not self.line) or self.line.startswith('#'):
            return # The line is empty or a comment

        subject = self.subject()
        self.eat(r_wspaces)

        predicate = self.predicate()
        self.eat(r_wspaces)

        object = self.object()
        self.eat(r_wspaces)
        
        graph = self.graph()
        self.eat(r_tail)

        if self.line:
            raise ParseError("Trailing garbage")
        self.sink.quad(subject, predicate, object, graph)
    
    def graph(self):
        graph = self.uriref()
        if not graph:
            raise ParseError('Graph must be a uriref')
        return graph

from lepl import *
from threading import local

class BaseNParser(object):
    """Base parser that establishes common grammar rules used for parsing both
    n-triples and n-quads."""
    
    def make_datatype_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(value = values[0], datatype = values[1])
    
    def make_language_literal(self, values):
        from pymantic.primitives import Literal
        if len(values) == 2:
            return Literal(value = values[0], language = values[1])
        else:
            return Literal(value = values[0])
    
    def make_named_node(self, values):
        from pymantic.primitives import NamedNode
        return NamedNode(values[0])
    
    def make_blank_node(self, values):
        from pymantic.primitives import BlankNode
        if values[0] not in self._call_state.bnodes:
            self._call_state.bnodes[values[0]] = BlankNode()
        return self._call_state.bnodes[values[0]]
    
    def __init__(self):
        self._call_state = local()

        self.string = Regexp(r'[^"\\]*(?:\\.[^"\\]*)*')
        self.name = Regexp(r'[A-Za-z][A-Za-z0-9]*')
        self.absoluteURI = Regexp(r'[^:]+:[^\s"<>]+')
        self.language = Regexp(r'[a-z]+(?:-[a-zA-Z0-9]+)*')
        self.uriref = ~Literal('<') & self.absoluteURI & ~Literal('>') > self.make_named_node
        self.datatypeString = ~Literal('"') & self.string & ~Literal('"') & ~Literal('^^') & self.uriref > self.make_datatype_literal
        self.langString = ~Literal('"') & self.string & ~Literal('"') & Optional(~Literal('@') & self.language) > self.make_language_literal
        self.literal = self.datatypeString | self.langString
        self.nodeID = ~Literal('_:') & self.name > self.make_blank_node
        self.object_ = self.uriref | self.nodeID | self.literal
        self.predicate = self.uriref
        self.subject = self.uriref | self.nodeID
        self.comment = Literal('#') & Regexp(r'[ -~]*')
    
    def _prepare_parse(self):
        self._call_state.bnodes = {}

class NTripleParser(BaseNParser):
    def make_triple(self, values):
        from pymantic.primitives import Triple
        triple = Triple(*values)
        self._call_state.graph.add(triple)
        return triple

    def __init__(self):
        super(NTripleParser, self).__init__()
        self.triple = self.subject & ~Plus(Space()) & self.predicate & ~Plus(Space()) & self.object_ & ~Star(Space()) & ~Literal('.') & ~Star(Space()) >= self.make_triple
        self.line = Star(Space()) & Optional(~self.triple | ~self.comment) & ~Literal('\n')
        self.document = Star(self.line)
    
    def _prepare_parse(self, graph):
        super(NTripleParser, self)._prepare_parse()
        self._call_state.graph = graph
    
    def parse(self, f, graph = None):
        if graph is None:
            from pymantic.primitives import Graph
            graph = Graph()
        self._prepare_parse(graph)
        self.document.parse_file(f)
        
        return graph

def parse_ntriples(f, graph = None):
    parser = NTripleParser()
    return parser.parse(f, graph)
