__all__ = ['NTriplesParser', 'parse_ntriples', 'NQuadsParser', 'parse_nquads', 
           'parse_turtle']

from lepl import *
from lxml import etree
import re
from threading import local
from urlparse import urljoin

unicode_re = re.compile(r'\\u([0-9]{4})')

def nt_unescape(nt_string):
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


class BaseLeplParser(object):

    def __init__(self):
        self._call_state = local()
        
    def make_datatype_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(value = values[0], datatype = values[1])
    
    def make_language_literal(self, values):
        from pymantic.primitives import Literal
        if len(values) == 2:
            return Literal(value = nt_unescape(values[0]), language = values[1])
        else:
            return Literal(value = nt_unescape(values[0]))
    
    def make_named_node(self, values):
        from pymantic.primitives import NamedNode
        return NamedNode(values[0])
    
    def make_blank_node(self, values):
        from pymantic.primitives import BlankNode
        if values[0] not in self._call_state.bnodes:
            self._call_state.bnodes[values[0]] = BlankNode()
        return self._call_state.bnodes[values[0]]
    
    def _prepare_parse(self, graph):
        self._call_state.bnodes = {}
        self._call_state.graph = graph
        
    def _cleanup_parse(self):
        del self._call_state.bnodes
        del self._call_state.graph
    
    def _make_graph(self):
        raise NotImplementedError()
    
    def parse(self, f, sink = None):
        if sink is None:
            sink = self._make_graph()
        self._prepare_parse(sink)
        self.document.parse_file(f)
        self._cleanup_parse()
        
        return sink


class BaseNParser(BaseLeplParser):
    """Base parser that establishes common grammar rules and interfaces used for
    parsing both n-triples and n-quads."""
    
    
    def __init__(self):
        super(BaseNParser, self).__init__()
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
    
    def parse(self, f, graph):
        return super(NTriplesParser, self).parse(f, graph)

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
    
    def parse(self, f, dataset):
        return super(NQuadsParser, self).parse(f, dataset)

def parse_nquads(f, dataset = None):
    parser = NQuadsParser()
    return parser.parse(f, dataset)


class TurtleParser(BaseLeplParser):
    
    def __init__(self):
        super(TurtleParser, self).__init__()
        
        # White space is significant in the following rules.
        hex_ = Any('0123456789ABCDEF')
        character_escape = Or(And(Literal('r\u'), hex_[4]),
                              And(Literal(r'\U'), hex_[8]),
                              Literal(r'\\'))
        character = Or(character_escape,
                       Regexp(ur'[\u0020-\u005B\]-\U0010FFFF]'))
        echaracter = character | Any(r'\t\n\r')
        ucharacter = Or(character_escape,
                        Regexp(ur'[\u0020-\u003D\u003F-\u005B\]-\U0010FFFF]')) | r'\>'
        scharacter = Or(character_escape,
                        Regexp(ur'[\u0020-\u0021\u0023-\u005B\]-\U0010FFFF]')) | r'\"'
        lcharacter = echaracter | '\"' | '\u009' | '\u000A' | '\u000D'
        longString = And('"""', Star(lcharacter), '"""')
        string = And('"', Star(scharacter), '"')
        quotedString = string | longString
        relativeURI = Star(ucharacter)
        uriref = And('<', relativeURI, '>')
        
        # Whie space is not significant in the following rules.
        with Separator(~Star(Any(' \t\n\r'))):
            prefixStartChar = Regexp(ur'[A-Z]') | Regexp(ur'[a-z]') | Regexp(ur'[\u00C0-\u00D6]') | Regexp(ur'[\u00D8-\u00F6]') | Regexp(ur'[\u00F8-\u02FF]') | Regexp(ur'[\u0370-\u037D]') | Regexp(ur'[\u037F-\u1FFF]') | Regexp(ur'[\u200C-\u200D]') | Regexp(ur'[\u2070-\u218F]') | Regexp(ur'[\u2C00-\u2FEF]') | Regexp(ur'[\u3001-\uD7FF]') | Regexp(ur'[\uF900-\uFDCF]') | Regexp(ur'[\uFDF0-\uFFFD]') | Regexp(ur'[\U00010000-\U000EFFFF]')
            nameStartChar = prefixStartChar | "_"
            nameChar = nameStartChar | '-' | Regexp(ur'[0-9]') | '\u00B7' | Regexp(ur'[\u0300-\u036F]') | Regexp(ur'[\u203F-\u2040]')
            name = nameStartChar & nameChar[:]
            prefixName = prefixStartChar & nameChar[:]
            language = Lower()[1:] & Regexp(r'-[a-z0-9]+')[:]
            qname = Optional(prefixName) & ':' & Optional(name)
            nodeID = '_:' & name
            resource = uriref | qname
            comment = '#' & Star(AnyBut('\u000A\u000D'))
            ws = Whitespace() or comment
            
            blank = Delayed()
            integer = Regexp(r'(-|+)?[0-9]+')
            decimal = Regexp(r'(-|+)?([0-9]+\.[0-9]*|\.([0-9])+|([0-9])+)')
            exponent = Regexp(r'[eE](-|+)?[0-9]+')
            boolean = Literal('true') | Literal('false')
            datatypeString = quotedString & "^^" & resource
            literal = Or ( quotedString & Optional('@' & language), 
                           datatypeString,
                           integer,
                           decimal,
                           boolean )
            object_ = resource | blank | literal
            predicate = resource
            subject = resource | blank
            verb = predicate | Literal('a')
            itemList = object_[1:]
            collection = Literal('(') & Optional(itemList) & Literal(')')
            objectList = object_ & (Literal(',') & object_)[:]
            predicateObjectList = verb & objectList & (Literal(';') & verb & objectList)[:] & Optional(';')
            blank += Or (nodeID, Literal('[') & Literal(']'), collection,
                         Literal('[') & predicateObjectList & Literal(']'))
            triples = subject & predicateObjectList
            base = Literal('@base') & Plus(ws) & uriref
            prefixId = Literal('@prefix') & Plus(ws) & Optional(prefixName) & ':' & uriref
            directive = prefixId | base
            statement = Or (directive & '.', triples & '.', Plus(ws))
            self.document = Star(statement)
        
def parse_turtle(f, graph = None):
    parser = TurtleParser()
    return parser.parse(f, graph)

scheme_re = re.compile(r'[a-zA-Z](?:[a-zA-Z0-9]|\+|-|\.)*')

class RDFXMLParser(object):
    def __init__(self):
        self.namespaces = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',}
        self._call_state = local()
        
    def clark(self, prefix, tag):
        return '{%s}%s' % (self.namespaces[prefix], tag)
    
    def parse(self, f, sink = None):
        self._call_state.bnodes = {}
        tree = etree.parse(f)
        if tree.getroot() != self.clark('rdf', 'RDF'):
            raise ValueError('Invalid XML document.')
        for element in tree.getroot():
            self._handle_resource(element, sink)
    
    def _handle_resource(element, sink):
        from pymantic.primitives import BlankNode, NamedNode
        subject = self._determine_subject(element)
        if element.tag != self.clark('rdf', 'Description'):
            pass
    
    def _determine_subject(element):
        if self.clark('rdf', 'resource') not in element.attrib and\
           self.clark('rdf', 'nodeID') not in element.attrib and\
           self.clark('rdf', 'ID') not in element.attrib:
            return BlankNode()
        elif self.clark('rdf', 'nodeID') in element.attrib:
            node_id = element.attrib[self.clark('rdf', 'nodeID')]
            if node_id not in self._call_state.bnodes:
                self._call_state.bnodes[node_id] = BlankNode()
            return self._call_state.bnodes[node_id]
        elif self.clark('rdf', 'ID') in element.attrib:
            return NamedNode(element.base + '#' +\
                             element.attrib[self.clark('rdf', 'ID')])
        elif self.clark('rdf', 'resource') in element.attrib:
            resource = element.attrib[self.clark('rdf', 'resource')]
            if not scheme_re.match(resource):
                return NamedNode(urljoin(element.base, resource))
            else:
                return NamedNode(resource)
