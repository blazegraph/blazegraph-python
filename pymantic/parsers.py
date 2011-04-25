__all__ = ['ntriples_parser', 'nquads_parser', 'turtle_parser']

from lepl import *
from lxml import etree
import re
from threading import local
from urlparse import urljoin
from pymantic.util import normalize_iri

unicode_re = re.compile(r'\\u([0-9A-Za-z]{4})|\\U([0-9A-Za-z]{8})')

def nt_unescape(nt_string):
    """Un-do nt escaping style."""
    output_string = u''
    nt_string = nt_string.decode('utf-8')
    nt_string = nt_string.replace('\\t', u'\u0009')
    nt_string = nt_string.replace('\\n', u'\u000A')
    nt_string = nt_string.replace('\\r', u'\u000D')
    nt_string = nt_string.replace('\\"', u'\u0022')
    nt_string = nt_string.replace('\\\\', u'\u005C')
    def chr_match(matchobj):
        ordinal = matchobj.group(1) or matchobj.group(2)
        return unichr(ordinal)
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
            return Literal(value = values[0], language = values[1])
        else:
            return Literal(value = values[0])
    
    def make_named_node(self, values):
        from pymantic.primitives import NamedNode
        return NamedNode(normalize_iri(values[0]))
    
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
    
    def parse_string(self, string, sink = None):
        if sink is None:
            sink = self._make_graph()
        self._prepare_parse(sink)
        self.document.parse(string)
        self._cleanup_parse()
        
        return sink

class BaseNParser(BaseLeplParser):
    """Base parser that establishes common grammar rules and interfaces used for
    parsing both n-triples and n-quads."""
    
    def __init__(self):
        super(BaseNParser, self).__init__()
        self.string = Regexp(r'(?:[ -!#-[\]-~]|\\[trn"\\]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})*')
        self.name = Regexp(r'[A-Za-z][A-Za-z0-9]*')
        self.absoluteURI = Regexp(r'(?:[ -=?-[\]-~]|\\[trn"\\]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})+')
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
        
    def make_named_node(self, values):
        from pymantic.primitives import NamedNode
        return NamedNode(normalize_iri(nt_unescape(values[0])))
    
    def make_language_literal(self, values):
        from pymantic.primitives import Literal
        if len(values) == 2:
            return Literal(value = nt_unescape(values[0]), language = values[1])
        else:
            return Literal(value = nt_unescape(values[0]))

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

ntriples_parser = NTriplesParser()

class NQuadsParser(BaseNParser):
    def make_quad(self, values):
        from pymantic.primitives import Quad
        quad = Quad(*values)
        self._call_state.graph.add(quad)
        return quad

    def __init__(self):
        super(NQuadsParser, self).__init__()
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

nquads_parser = NQuadsParser()

class TurtleParser(BaseLeplParser):
    
    def __init__(self):
        super(TurtleParser, self).__init__()
        
        self.absolute_uri_re = re.compile('^[^/]+:')
        
        from pymantic.primitives import Namespace
        
        self.rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
        
        # White space is significant in the following rules.
        hex_ = Any('0123456789ABCDEF')
        character_escape = Or(And(Literal('r\u'), hex_[4]),
                              And(Literal(r'\U'), hex_[8]),
                              Literal(r'\\'))
        character = Or(character_escape,
                       Regexp(ur'[\u0020-\u005B\]-\U0010FFFF]'))
        echaracter = character | Any('\t\n\r')
        ucharacter = Or(character_escape,
                        Regexp(ur'[\u0020-\u003D\u003F-\u005B\]-\U0010FFFF]')) | r'\>'
        scharacter = Or(character_escape,
                        Regexp(ur'[\u0020-\u0021\u0023-\u005B\]-\U0010FFFF]')) | r'\"'
        lcharacter = echaracter | '\"' | '\u009' | '\u000A' | '\u000D'
        longString = ~Literal('"""') & lcharacter[:,...] & ~Literal('"""')
        string = ~Literal('"') & scharacter[:,...] & ~Literal('"')
        quotedString = longString | string > 'quotedString'
        relativeURI = ucharacter[...]
        prefixStartChar = Regexp(ur'[A-Z]') | Regexp(ur'[a-z]') | Regexp(ur'[\u00C0-\u00D6]') | Regexp(ur'[\u00D8-\u00F6]') | Regexp(ur'[\u00F8-\u02FF]') | Regexp(ur'[\u0370-\u037D]') | Regexp(ur'[\u037F-\u1FFF]') | Regexp(ur'[\u200C-\u200D]') | Regexp(ur'[\u2070-\u218F]') | Regexp(ur'[\u2C00-\u2FEF]') | Regexp(ur'[\u3001-\uD7FF]') | Regexp(ur'[\uF900-\uFDCF]') | Regexp(ur'[\uFDF0-\uFFFD]') | Regexp(ur'[\U00010000-\U000EFFFF]')
        nameStartChar = prefixStartChar | "_"
        nameChar = nameStartChar | '-' | Regexp(ur'[0-9]') | '\u00B7' | Regexp(ur'[\u0300-\u036F]') | Regexp(ur'[\u203F-\u2040]')
        name = (nameStartChar & nameChar[:])[...] > 'name'
        prefixName = (prefixStartChar & nameChar[:])[...] > 'prefixName'
        language = Regexp(r'[a-z]+ (?:-[a-z0-9]+)*') > 'language'
        qname = ((Optional(prefixName) & ~Literal(':') & Optional(name) > dict) > self.resolve_prefix) > 'qname'        
        nodeID = ~Literal('_:') & name > self.make_blank_node
        
        # Whie space is not significant in the following rules.
        with Separator(~Star(Any(' \t\n\r'))):
            uriref = (And(~Literal('<'), relativeURI, ~Literal('>')) > self.resolve_relative_uri) > 'uriref'
            resource = (uriref | qname > dict) > self.make_named_node
            comment = '#' & Star(AnyBut('\u000A\u000D'))
            ws = ~Whitespace() or ~comment
            
            blank = Delayed()
            integer = Regexp(r'(?:-|\+)?[0-9]+') > self.make_integer_literal
            decimal = Regexp(r'(?:-|\+)?(?:[0-9]+\.[0-9]*|\.(?:[0-9])+)') > self.make_decimal_literal
            exponent = r'[eE](?:-|\+)?[0-9]+'
            double = Regexp(r'(?:-|\+)?(?:[0-9]+\.[0-9]*' + exponent + r'|\.[0-9]+' + exponent + r'|[0-9]+' + exponent + ')') > self.make_double_literal
            boolean = Literal('true') | Literal('false') > self.make_boolean_literal
            datatypeString = quotedString & "^^" & (resource > 'dataType') > self.make_datatype_literal
            literal = Or ( datatypeString,
                           quotedString & Optional(~Literal('@') & language) > self.make_language_literal,
                           double,
                           decimal,
                           integer,
                           boolean )
            object_ = resource | blank | literal
            predicate = resource
            subject = resource | blank > 'subject'
            verb = predicate | Literal('a') > 'predicate'
            collection = ~Literal('(') & object_[:] & ~Literal(')') > self.make_collection
            objectList = (object_ & (~Literal(',') & object_)[:] > List) > 'objectList'
            predicateObjectList = ((verb & objectList > Node) & (~Literal(';') & (verb & objectList > Node))[:] & ~Optional(';') > List) > 'predicateObjectList'
            blank += Or (nodeID, collection,
                         (~Literal('[') & ~Literal(']') > self.make_triples),
                         (~Literal('[') & predicateObjectList & ~Literal(']') > self.make_triples)
                         )
            triples = subject & predicateObjectList > self.make_triples
            base = (~Literal('@base') & Plus(ws) & uriref > dict) > self.record_base
            prefixId = (~Literal('@prefix') & Plus(ws) & Optional(prefixName) & ~Literal(':') & uriref > dict) > self.record_prefix
            directive = prefixId | base
            statement = Or (directive & '.', triples & '.', Plus(ws))
            self.document = Star(statement)
    
    def _prepare_parse(self, graph):
        super(TurtleParser, self)._prepare_parse(graph)
        self._call_state.prefixes = {}
        self._call_state.base_uri = None
    
    def record_base(self, values):
        self._call_state.base_uri = values[0]['uriref']
        return ''
    
    def record_prefix(self, values):
        prefix = values[0]
        self._call_state.prefixes[prefix.get('prefixName', '')] = prefix['uriref']
        return ''
    
    def resolve_relative_uri(self, values):
        relative_uri = values[0]
        if self.absolute_uri_re.match(relative_uri):
            return relative_uri
        else:
            return self._call_state.base_uri + relative_uri
    
    def resolve_prefix(self, values):
        qname = values[0]
        return self._call_state.prefixes[qname.get('prefixName', '')] + qname.get('name', '')
    
    def make_named_node(self, values):
        resource = values[0]
        return super(TurtleParser, self).make_named_node(
            (resource.get('uriref') or resource.get('qname'),))
    
    def make_triples(self, values):
        from pymantic.primitives import Triple, BlankNode
        triples = dict(values)
        subject = triples.get('subject')
        if not subject:
            subject = BlankNode()
        for predicate_object_node in triples.get('predicateObjectList', ()):
            predicate = predicate_object_node.predicate[0]
            for object_ in predicate_object_node.objectList[0]:
                self._call_state.graph.add(Triple(subject, predicate, object_))
        return subject
    
    def make_collection(self, values):
        from pymantic.primitives import BlankNode, Triple
        prior = self.rdf('nil')
        for element in reversed(values):
            this = BlankNode()
            self._call_state.graph.add(Triple(this, self.rdf('first'), element))
            self._call_state.graph.add(Triple(this, self.rdf('rest'), prior))
            prior = this
        return prior
    
    def _make_graph(self):
        from pymantic.primitives import Graph
        return Graph()
    
    def make_datatype_literal(self, values):
        from pymantic.primitives import Literal
        datatyped = dict(values)
        return Literal(datatyped['quotedString'], datatype = datatyped['dataType'])
    
    def make_integer_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(values[0], datatype = self.xsd('integer'))
    
    def make_decimal_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(values[0], datatype = self.xsd('decimal'))
    
    def make_double_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(values[0], datatype = self.xsd('double'))
    
    def make_boolean_literal(self, values):
        from pymantic.primitives import Literal
        return Literal(values[0], datatype = self.xsd('boolean'))
    
    def make_language_literal(self, values):
        print values
        from pymantic.primitives import Literal
        languageable = dict(values)
        return Literal(languageable['quotedString'], language = languageable.get('language'))

turtle_parser = TurtleParser()

scheme_re = re.compile(r'[a-zA-Z](?:[a-zA-Z0-9]|\+|-|\.)*')

class RDFXMLParser(object):
    RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    
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
    
    def _handle_resource(self, element, sink):
        from pymantic.primitives import BlankNode, NamedNode, Triple
        subject = self._determine_subject(element)
        if element.tag != self.clark('rdf', 'Description'):
            resource_class = self._resolve_tag(element)
            sink.add(Triple(subject, NamedNode(self.RDF_TYPE), resource_class))
        for property_element in element:
            if property_element.tag == self.clark('rdf', 'li'):
                pass
            else:
                predicate = self._resolve_tag(property_element)
            if self.clark('rdf', 'resource') in property_element.attrib:
                object_ = self._resolve_uri(
                    property_element, property_element.attrib[self.clark(
                        'rdf', 'resource')])
                sink.add(Triple(subject, NamedNode(predicate), NamedNode(object_)))
        return subject
    
    def _resolve_tag(self, element):
        if element.tag[0] == '{':
            tag_bits = element[1:].partition('}')
            return NamedNode(tag_bits[0] + tag_bits[2])
        else:
            return NamedNode(urljoin(element.base, element.tag))
    
    def _determine_subject(self, element):
        if self.clark('rdf', 'about') not in element.attrib and\
           self.clark('rdf', 'nodeID') not in element.attrib and\
           self.clark('rdf', 'ID') not in element.attrib:
            return BlankNode()
        elif self.clark('rdf', 'nodeID') in element.attrib:
            node_id = element.attrib[self.clark('rdf', 'nodeID')]
            if node_id not in self._call_state.bnodes:
                self._call_state.bnodes[node_id] = BlankNode()
            return self._call_state.bnodes[node_id]
        elif self.clark('rdf', 'ID') in element.attrib:
            if not element.base:
                raise ValueError('No XML base for %r', element)
            return NamedNode(element.base + '#' +\
                             element.attrib[self.clark('rdf', 'ID')])
        elif self.clark('rdf', 'about') in element.attrib:
            return self._resolve_uri(element, element.attrib[
                self.clark('rdf', 'resource')])
    
    def _resolve_uri(self, element, uri):
        if not scheme_re.match(uri):
            return NamedNode(urljoin(element.base, uri))
        else:
            return NamedNode(uri)
