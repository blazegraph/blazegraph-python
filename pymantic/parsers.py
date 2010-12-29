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

def parse_ntriples(stream, graph):
    bnodes = {}
    
    def make_datatype_literal(values):
        from pymantic.primitives import Literal
        return Literal(value = values[0], datatype = values[1])
    
    def make_language_literal(values):
        from pymantic.primitives import Literal
        if len(values) == 2:
            return Literal(value = values[0], language = values[1])
        else:
            return Literal(value = values[0])
    
    def make_named_node(values):
        from pymantic.primitives import NamedNode
        return NamedNode(values[0])
    
    def make_blank_node(values):
        from pymantic.primitives import BlankNode
        if values[0] not in bnodes:
            bnodes[values[0]] = BlankNode()
        return bnodes[values[0]]
    
    def make_triple(values):
        from pymantic.primitives import Triple
        triple = Triple(*values)
        graph.add(triple)
        return triple

    string = Regexp(r'[^"\\]*(?:\\.[^"\\]*)*')
    name = Regexp(r'[A-Za-z][A-Za-z0-9]*')
    absoluteURI = Regexp(r'[^:]+:[^\s"<>]+')
    language = Regexp(r'[a-z]+(?:-[a-z0-9]+)*')
    uriref = ~Literal('<') & absoluteURI & ~Literal('>') > make_named_node
    datatypeString = ~Literal('"') & string & ~Literal('"') & ~Literal('^^') & uriref > make_datatype_literal
    langString = ~Literal('"') & string & ~Literal('"') & Optional(~Literal('@') & language) > make_language_literal
    literal = datatypeString | langString
    nodeID = ~Literal('_:') & name > make_blank_node
    object_ = uriref | nodeID | literal
    predicate = uriref
    subject = uriref | nodeID
    triple = subject & ~Plus(Space()) & predicate & ~Plus(Space()) & object_ & ~Star(Space()) & ~Literal('.') & ~Star(Space()) >= make_triple
    comment = Literal('#') & Regexp(r'[ -~]*')
    line = Star(Space()) & Optional(~triple | ~comment) & ~Literal('\n')
    document = Star(line)
    
    document.parse_file(stream)
    
    return graph
