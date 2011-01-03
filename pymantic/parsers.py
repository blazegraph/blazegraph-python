__all__ = ['NTriplesParser', 'parse_ntriples', 'NQuadsParser', 'parse_nquads',]

from lepl import *
import re
from threading import local

unicode_re = re.compile(r'\\u([0-9]{4})')

def nt_unquote(nt_string):
    """Un-do nt escaping style."""
    output_string = ''
    nt_string = nt_string.replace('\\t', u'\u0009')
    nt_string = nt_string.replace('\\n', u'\u000A')
    nt_string = nt_string.replace('\\r', u'\u000D')
    nt_string = nt_string.replace('\\"', u'\u0022')
    nt_string = nt_string.replace('\\\\', u'\u005C')
    def chr_match(matchobj):
        ordinal = matchobj.group(1)
        return chr(ordinal)
    nt_string = unicode_re.sub(chr_match, nt_string)
    return nt_string

class BaseNParser(object):
    """Base parser that establishes common grammar rules and interfaces used for
    parsing both n-triples and n-quads."""
    
    def make_datatype_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(value = values[0], datatype = values[1])
    
    def make_language_literal(self, values):
        from pymantic.primitives import Literal
        if len(values) == 2:
            return Literal(value = nt_unquote(values[0]), language = values[1])
        else:
            return Literal(value = nt_unquote(values[0]))
    
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
    
    def _prepare_parse(self, graph):
        self._call_state.bnodes = {}
        self._call_state.graph = graph
        
    def _cleanup_parse(self):
        del self._call_state.bnodes
        del self._call_state.graph
    
    def _make_graph(self):
        raise NotImplementedError()
    
    def parse(self, f, graph = None):
        if graph is None:
            graph = self._make_graph()
        self._prepare_parse(graph)
        self.document.parse_file(f)
        self._cleanup_parse()
        
        return graph

class NTriplesParser(BaseNParser):
    def make_triple(self, values):
        from pymantic.primitives import Triple
        triple = Triple(*values)
        self._call_state.graph.add(triple)
        return triple

    def __init__(self):
        super(NTriplesParser, self).__init__()
        self.triple = self.subject & ~Plus(Space()) & self.predicate & ~Plus(Space()) & self.object_ & ~Star(Space()) & ~Literal('.') & ~Star(Space()) >= self.make_triple
        self.line = Star(Space()) & Optional(~self.triple | ~self.comment) & ~Literal('\n')
        self.document = Star(self.line)
    
    def _make_graph(self):
        from pymantic.primitives import Graph
        return Graph()

def parse_ntriples(f, graph = None):
    parser = NTriplesParser()
    return parser.parse(f, graph)

class NQuadsParser(BaseNParser):
    def make_quad(self, values):
        from pymantic.primitives import Quad
        quad = Quad(*values)
        self._call_state.graph.add(quad)
        return quad

    def __init__(self):
        super(NTripleParser, self).__init__()
        self.graph_name = self.uriref
        self.quad = self.subject & ~Plus(Space()) & self.predicate & ~Plus(Space()) &\
            self.object_ & ~Plus(Space()) & self.graph_name & ~Star(Space()) &\
            ~Literal('.') & ~Star(Space()) >= self.make_quad
        self.line = Star(Space()) & Optional(~self.quad | ~self.comment) & ~Literal('\n')
        self.document = Star(self.line)
    
    def _make_graph(self):
        from pymantic.primitives import Dataset
        return Dataset()

def parse_nquads(f, graph = None):
    parser = NQuadsParser()
    return parser.parse(f, graph)
