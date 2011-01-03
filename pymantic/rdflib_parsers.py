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
