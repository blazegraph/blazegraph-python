__all__ = ['ntriples_parser', 'nquads_parser', 'turtle_parser']

from collections import defaultdict, namedtuple, OrderedDict
from lepl import *
from lxml import etree
import re
from threading import local
from urlparse import urljoin
from pymantic.util import normalize_iri
import pymantic.primitives

def discrete_pairs(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    previous = None
    for v in iterable:
        if previous is None:
            previous = v
        else:
            yield (previous, v)
            previous = None

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
        return unichr(int(ordinal, 16))
    nt_string = unicode_re.sub(chr_match, nt_string)
    return nt_string

class BaseLeplParser(object):

    def __init__(self, environment=None):
        self.env = environment or pymantic.primitives.RDFEnvironment()
        self.profile = self.env.createProfile()
        self._call_state = local()

    def make_datatype_literal(self, values):
        return self.env.createLiteral(value = values[0], datatype = values[1])

    def make_language_literal(self, values):
        if len(values) == 2:
            return self.env.createLiteral(value = values[0],
                                                  language = values[1])
        else:
            return self.env.createLiteral(value = values[0])

    def make_named_node(self, values):
        return self.env.createNamedNode(normalize_iri(values[0]))

    def make_blank_node(self, values):
        if values[0] not in self._call_state.bnodes:
            self._call_state.bnodes[values[0]] = self.env.createBlankNode()
        return self._call_state.bnodes[values[0]]

    def _prepare_parse(self, graph):
        self._call_state.bnodes = defaultdict(self.env.createBlankNode)
        self._call_state.graph = graph

    def _cleanup_parse(self):
        del self._call_state.bnodes
        del self._call_state.graph

    def _make_graph(self):
        return self.env.createGraph()

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

    def __init__(self, environment=None):
        super(BaseNParser, self).__init__(environment)
        self.string = Regexp(r'(?:[ -!#-[\]-~]|\\[trn"\\]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})*')
        self.name = Regexp(r'[A-Za-z][A-Za-z0-9]*')
        self.absoluteURI = Regexp(r'(?:[ -=?-[\]-~]|\\[trn"\\]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})+')
        self.language = Regexp(r'[a-z]+(?:-[a-zA-Z0-9]+)*')
        self.uriref = ~Literal('<') & self.absoluteURI & ~Literal('>') \
            > self.make_named_node
        self.datatypeString = ~Literal('"') & self.string & ~Literal('"') \
            & ~Literal('^^') & self.uriref > self.make_datatype_literal
        self.langString = ~Literal('"') & self.string & ~Literal('"') \
            & Optional(~Literal('@') & self.language) > self.make_language_literal
        self.literal = self.datatypeString | self.langString
        self.nodeID = ~Literal('_:') & self.name > self.make_blank_node
        self.object_ = self.uriref | self.nodeID | self.literal
        self.predicate = self.uriref
        self.subject = self.uriref | self.nodeID
        self.comment = Literal('#') & Regexp(r'[ -~]*')

    def make_named_node(self, values):
        return self.env.createNamedNode(normalize_iri(nt_unescape(values[0])))

    def make_language_literal(self, values):
        if len(values) == 2:
            return self.env.createLiteral(value = nt_unescape(values[0]),
                                          language = values[1])
        else:
            return self.env.createLiteral(value = nt_unescape(values[0]))

class NTriplesParser(BaseNParser):
    def make_triple(self, values):
        triple = self.env.createTriple(*values)
        self._call_state.graph.add(triple)
        return triple

    def __init__(self, environment=None):
        super(NTriplesParser, self).__init__(environment)
        self.triple = self.subject & ~Plus(Space()) & self.predicate & \
            ~Plus(Space()) & self.object_ & ~Star(Space()) & ~Literal('.') \
            & ~Star(Space()) >= self.make_triple
        self.line = Star(Space()) & Optional(~self.triple | ~self.comment) & \
            ~Literal('\n')
        self.document = Star(self.line)

    def _make_graph(self):
        return self.env.createGraph()

    def parse(self, f, graph=None):
        return super(NTriplesParser, self).parse(f, graph)

ntriples_parser = NTriplesParser()

class NQuadsParser(BaseNParser):
    def make_quad(self, values):
        quad = self.env.createQuad(*values)
        self._call_state.graph.add(quad)
        return quad

    def __init__(self, environment=None):
        super(NQuadsParser, self).__init__(environment)
        self.graph_name = self.uriref
        self.quad = self.subject & ~Plus(Space()) & self.predicate \
            & ~Plus(Space()) & self.object_ & ~Plus(Space()) & self.graph_name \
            & ~Star(Space()) & ~Literal('.') & ~Star(Space()) >= self.make_quad
        self.line = Star(Space()) & Optional(~self.quad | ~self.comment) \
            & ~Literal('\n')
        self.document = Star(self.line)

    def _make_graph(self):
        return self.env.createDataset()

    def parse(self, f, dataset=None):
        return super(NQuadsParser, self).parse(f, dataset)

nquads_parser = NQuadsParser()

class ClassicTurtleParser(BaseLeplParser):

    def __init__(self, environment=None):
        super(ClassicTurtleParser, self).__init__(environment)

        self.absolute_uri_re = re.compile('^[^/]+:')

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
        self.comment = '#' & Regexp(r'[^\n\r]*') & Newline()

        # Whie space is not significant in the following rules.
        with Separator(~Star(Any(' \t\n\r'))):
            uriref = (And(~Literal('<'), relativeURI, ~Literal('>')) > self.resolve_relative_uri) > 'uriref'
            resource = (uriref | qname > dict) > self.make_named_node
            self.ws = ws = ~Whitespace() | ~self.comment

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
        self._call_state.prefixes = self.env.createPrefixMap(empty=True)
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
        triples = dict(values)
        subject = triples.get('subject')
        if not subject:
            subject = self.env.createBlankNode()
        for predicate_object_node in triples.get('predicateObjectList', ()):
            predicate = predicate_object_node.predicate[0]
            for object_ in predicate_object_node.objectList[0]:
                self._call_state.graph.add(self.env.createTriple(subject, predicate, object_))
        return subject

    def make_collection(self, values):
        prior = self.env.resolve('rdf:nil')
        for element in reversed(values):
            this = self.env.createBlankNode()
            self._call_state.graph.add(self.env.createTriple(
                subject=this, predicate=self.env.resolve('rdf:first'),
                object=element))
            self._call_state.graph.add(self.env.createTriple(
                subject=this, predicate=self.env.resolve('rdf:rest'), object=prior))
            prior = this
        return prior

    def _make_graph(self):
        return self.env.createGraph()

    def make_datatype_literal(self, values):
        datatyped = dict(values)
        return self.env.createLiteral(datatyped['quotedString'],
                                      datatype = datatyped['dataType'])

    def make_integer_literal(self, values):
        return self.env.createLiteral(values[0],
                                      datatype = self.env.resolve('xsd:integer'))

    def make_decimal_literal(self, values):
        return self.env.createLiteral(values[0],
                                      datatype = self.env.resolve('xsd:decimal'))

    def make_double_literal(self, values):
        return self.env.createLiteral(values[0],
                                      datatype = self.env.resolve('xsd:double'))

    def make_boolean_literal(self, values):
        return self.env.createLiteral(values[0],
                                      datatype = self.env.resolve('xsd:boolean'))

    def make_language_literal(self, values):
        languageable = dict(values)
        return self.env.createLiteral(languageable['quotedString'],
                                      language = languageable.get('language'))

classic_turtle_parser = ClassicTurtleParser()

TriplesClause = namedtuple('TriplesClause', ['subject', 'predicate_objects'])

PredicateObject = namedtuple('PredicateObject', ['predicate', 'object'])

BindPrefix = namedtuple('BindPrefix', ['prefix', 'iri'])

SetBase = namedtuple('SetBase', ['iri'])

NamedNodeToBe = namedtuple('NamedNodeToBe', ['iri'])

LiteralToBe = namedtuple('LiteralToBe', ['value', 'datatype', 'language'])

PrefixReference = namedtuple('PrefixReference', ['prefix', 'local'])

class TurtleParser(BaseLeplParser):
    """Parser for turtle as described at:
    http://dvcs.w3.org/hg/rdf/raw-file/e8b1d7283925/rdf-turtle/index.html"""

    RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

    echar_map = OrderedDict((
        ('\\', '\\'),
        ('t', '\t'),
        ('b', '\b'),
        ('n', '\n'),
        ('r', '\r'),
        ('f', '\f'),
        ('"', '"'),
        ("'", "'"),
    ))
    def __init__(self, environment=None):
        super(TurtleParser, self).__init__(environment)

        UCHAR = (Regexp(ur'\\u([0-9a-fA-F]{4})') |\
                 Regexp(ur'\\U([0-9a-fA-F]{8})')) >> self.decode_uchar
        
        ECHAR = Regexp(ur'\\([tbnrf\\"\'])') >> self.decode_echar
        
        PN_CHARS_BASE = Regexp(ur'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF'
                               ur'\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F'
                               ur'\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD'
                               ur'\U00010000-\U000EFFFF]') | UCHAR
        
        PN_CHARS_U = PN_CHARS_BASE | Literal('_')
        
        PN_CHARS = PN_CHARS_U | Regexp(ur'[\-0-9\u00B7\u0300-\u036F\u203F-\u2040]')
        
        PN_PREFIX = PN_CHARS_BASE & Optional(Star(PN_CHARS | Literal(".")) & PN_CHARS ) > ''.join
        
        PN_LOCAL = (PN_CHARS_U | Regexp('[0-9]')) & Optional(Star(PN_CHARS | Literal(".")) & PN_CHARS) > ''.join
        
        WS = Regexp(ur'[\t\n\r ]')
        
        ANON = ~(Literal('[') & Star(WS) & Literal(']'))
        
        NIL = Literal('(') & Star(WS) & Literal(')')
        
        STRING_LITERAL1 = (Literal("'") &\
                           Star(Regexp(ur"[^'\\\n\r]") | ECHAR | UCHAR ) &\
                           Literal("'")) > self.string_contents
 
        STRING_LITERAL2 = (Literal('"') &\
                           Star(Regexp(ur'[^"\\\n\r]') | ECHAR | UCHAR ) &\
                           Literal('"')) > self.string_contents
 
        STRING_LITERAL_LONG1 = (Literal("'''") &\
                                Star(Optional( Regexp("'|''")) &\
                                     ( Regexp(ur"[^'\\]") | ECHAR | UCHAR ) ) &\
                                Literal("'''")) > self.string_contents
 
        STRING_LITERAL_LONG2 = (Literal('"""') &\
                                Star(Optional( Regexp(ur'"|""') ) &\
                                     ( Regexp(ur'[^\"\\]') | ECHAR | UCHAR ) ) &\
                                Literal('"""')) > self.string_contents
        
        INTEGER = Regexp(ur'[+-]?[0-9]+')
 
        DECIMAL = Regexp(ur'[+-]?(?:[0-9]+\.[0-9]+|\.[0-9]+)')
        
        DOUBLE = Regexp(ur'[+-]?(?:[0-9]+\.[0-9]+|\.[0-9]+|[0-9]+)[eE][+-]?[0-9]+')
        
        IRI_REF = (~Literal('<') & (Star(Regexp(ur'[^<>"{}|^`\\\u0000-\u0020]') | UCHAR | ECHAR) > ''.join) & ~Literal('>'))
 
        PNAME_NS = Optional(PN_PREFIX) & Literal(":")
 
        PNAME_LN = PNAME_NS & PN_LOCAL
 
        BLANK_NODE_LABEL = ~Literal("_:") & PN_LOCAL 
 
        LANGTAG = ~Literal("@") & (Literal('base') | Literal('prefix') |\
                                   Regexp(ur'[a-zA-Z]+(?:-[a-zA-Z0-9]+)*'))
        
        intertoken = ~Regexp(ur'[ \t\r\n]+|#[^\r\n]+')[:]
        with Separator(intertoken):
            BlankNode = (BLANK_NODE_LABEL >> self.create_blank_node) |\
                (ANON > self.create_anon_node)
            
            prefixID = (~Literal('@prefix') & PNAME_NS & IRI_REF) > self.bind_prefixed_name
            
            base = (~Literal('@base') & IRI_REF) >> self.set_base
            
            PrefixedName = (PNAME_LN | PNAME_NS) > self.resolve_prefixed_name
            
            IRIref = PrefixedName | (IRI_REF >> self.create_named_node)
            
            BooleanLiteral = (Literal('true') | Literal('false')) >> self.boolean_value
            
            String = STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2
            
            RDFLiteral = ((String & LANGTAG) > self.langtag_string) |\
                       ((String & ~Literal('^^') & IRIref) > self.typed_string) |\
                        (String > self.bare_string)
            
            literal = RDFLiteral | (INTEGER  >> self.int_value) |\
                    (DECIMAL >> self.decimal_value) |\
                    (DOUBLE >> self.double_value) | BooleanLiteral
            
            object = Delayed()
            
            predicateObjectList = Delayed()
            
            blankNodePropertyList = ~Literal('[') & predicateObjectList & ~Literal(']') > self.make_blank_node_property_list
            
            collection = (~Literal('(') & object[:] & ~Literal(')')) > self.make_collection
            
            blank = BlankNode | blankNodePropertyList | collection
            
            subject = IRIref | blank
            
            predicate = IRIref
            
            object += IRIref | blank | literal
            
            verb = predicate | (~Literal('a') > self.create_rdf_type)
            
            objectList = ((object & (~Literal(',') & object)[:]) | object) > self.make_object
            
            predicateObjectList += ((verb & objectList &\
                                    (~Literal(';') & Optional(verb & objectList))[:]) |\
                                (verb & objectList)) > self.make_object_list
            
            triples = (subject & predicateObjectList) > self.make_triples
            
            directive = prefixID | base
            
            statement = (directive | triples) & ~Literal('.')
            
            self.turtle_doc = intertoken & statement[:] & intertoken & Eos()
            self.turtle_doc.config.clear()
    
    def _prepare_parse(self, graph):
        super(TurtleParser, self)._prepare_parse(graph)
        self._call_state.base_iri = self._base
        self._call_state.prefixes = {}
        self._call_state.current_subject = None
        self._call_state.current_predicate = None
    
    def decode_uchar(self, uchar_string):
        return unichr(int(uchar_string, 16))
    
    def decode_echar(self, echar_string):
        return self.echar_map[echar_string]
    
    def string_contents(self, string_chars):
        return ''.join(string_chars[1:-1])
    
    def int_value(self, value):
        return LiteralToBe(value, language=None,
                           datatype=NamedNodeToBe(self.profile.resolve('xsd:integer')))
    
    def decimal_value(self, value):
        return LiteralToBe(value, language=None,
                           datatype=NamedNodeToBe(self.profile.resolve('xsd:decimal')))
    
    def double_value(self, value):
        return LiteralToBe(value, language=None,
                           datatype=NamedNodeToBe(self.profile.resolve('xsd:double')))
    
    def boolean_value(self, value):
        return LiteralToBe(value, language=None,
                           datatype=NamedNodeToBe(self.profile.resolve('xsd:boolean')))
    
    def langtag_string(self, values):
        return LiteralToBe(values[0], language=values[1], datatype=None)
    
    def typed_string(self, values):
        return LiteralToBe(values[0], language=None, datatype=values[1])
    
    def bare_string(self, values):
        return LiteralToBe(values[0], language=None,
                           datatype=NamedNodeToBe(self.profile.resolve('xsd:string')))

    def create_named_node(self, iri):
        return NamedNodeToBe(iri)
    
    def create_blank_node(self, name=None):
        if name is None:
            return self.env.createBlankNode()
        return self._call_state.bnodes[name]
    
    def create_anon_node(self, anon_tokens):
        return self.env.createBlankNode()
    
    def create_rdf_type(self, values):
        return self.profile.resolve('rdf:type')
    
    def resolve_prefixed_name(self, values):
        if values[0] == ':':
            pname = ''
            local = values[1] if len(values) == 2 else ''
        elif values[-1] == ':':
            pname = values[0]
            local = ''
        else:
            pname = values[0]
            local = values[2]
        return NamedNodeToBe(PrefixReference(pname, local))
    
    def bind_prefixed_name(self, values):
        iri = values.pop()
        assert values.pop() == ':'
        pname = values.pop() if values else ''
        return BindPrefix(pname, iri)
    
    def set_base(self, base_iri):
        return SetBase(base_iri)
        
    def make_object(self, values):
        return values
    
    def make_object_list(self, values):
        return list(discrete_pairs(values))
    
    def make_blank_node_property_list(self, values):
        subject = self.env.createBlankNode()
        predicate_objects = []
        for predicate, objects in values[0]:
            for obj in objects:
                predicate_objects.append(PredicateObject(predicate, obj))
        return TriplesClause(subject, predicate_objects)
    
    def make_triples(self, values):
        subject = values[0]
        predicate_objects = [PredicateObject(predicate, obj) for
                             predicate, objects in values[1] for obj in objects]
        return TriplesClause(subject, predicate_objects)
    
    def make_collection(self, values):
        prev_node = TriplesClause(self.profile.resolve('rdf:nil'), [])
        for value in reversed(values):
            prev_node = TriplesClause(
                self.env.createBlankNode(),
                [PredicateObject(self.profile.resolve('rdf:first'), value),
                 PredicateObject(self.profile.resolve('rdf:rest'), prev_node)])
        return prev_node
    
    def _interpret_parse(self, data, sink):
        for line in data:
            if isinstance(line, BindPrefix):
                self._call_state.prefixes[line.prefix] = urljoin(
                    self._call_state.base_iri, line.iri, allow_fragments=False)
            elif isinstance(line, SetBase):
                self._call_state.base_iri = urljoin(
                    self._call_state.base_iri, line.iri, allow_fragments=False)
            else:
                self._interpret_triples_clause(line)
                
    def _interpret_triples_clause(self, triples_clause):
        assert isinstance(triples_clause, TriplesClause)
        subject = self._resolve_node(triples_clause.subject)
        for predicate_object in triples_clause.predicate_objects:
            self._call_state.graph.add(self.env.createTriple(
                subject, self._resolve_node(predicate_object.predicate),
                self._resolve_node(predicate_object.object)))
        return subject
    
    def _resolve_node(self, node):
        if isinstance(node, NamedNodeToBe):
            if isinstance(node.iri, PrefixReference):
                return self.env.createNamedNode(
                    self._call_state.prefixes[node.iri.prefix] + node.iri.local)
            else:
                return self.env.createNamedNode(
                    urljoin(self._call_state.base_iri, node.iri, 
                            allow_fragments=False))
        elif isinstance(node, TriplesClause):
            return self._interpret_triples_clause(node)
        elif isinstance(node, LiteralToBe):
            if node.datatype:
                return self.env.createLiteral(
                    node.value, datatype=self._resolve_node(node.datatype))
            else:
                return self.env.createLiteral(node.value, language=node.language)
        else:
            return node
    
    def parse(self, data, sink = None, base = ''):
        if sink is None:
            sink = self._make_graph()
        self._base = base
        self._prepare_parse(sink)
        self._interpret_parse(self.turtle_doc.parse(data), sink)
        self._cleanup_parse()

        return sink

    def parse_string(self, string, sink = None):
        return self.parse(string, sink)
    
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
