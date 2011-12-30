import re
import warnings

def nt_escape(node_string):
    """Properly escape strings for n-triples and n-quads serialization."""
    output_string = ''
    for char in node_string:
        if char == u'\u0009':
            output_string += '\\t'
        elif char == u'\u000A':
            output_string += '\\n'
        elif char == u'\u000D':
            output_string += '\\r'
        elif char == u'\u0022':
            output_string += '\\"'
        elif char == u'\u005C':
            output_string += '\\\\'
        elif char >= u'\u0020' and char <= u'\u0021' or\
             char >= u'\u0023' and char <= u'\u005B' or\
             char >= u'\u005D' and char <= u'\u007E':
            output_string += char.encode('utf-8')
        elif char >= u'\u007F' and char <= u'\uFFFF':
            output_string += '\\u%04X' % ord(char)
        elif char >= u'\U00010000' and char <= u'\U0010FFFF':
            output_string += '\\U%08X' % ord(char)
    return output_string

def serialize_ntriples(graph, f):
    for triple in graph:
        f.write(str(triple))

def serialize_nquads(dataset, f):
    for quad in dataset:
        f.write(str(quad))

def default_bnode_name_generator():
    i = 0
    while True:
        yield '_b' + str(i)
        i += 1

def escape_prefix_local(prefix):
    prefix, colon, local = prefix.partition(':')
    for esc_char in "~.-!$&'()*+,;=:/?#@%_":
        local = local.replace(esc_char, '\\' + esc_char)
    return ''.join((prefix,colon,local))

def turtle_string_escape(string):
    from pymantic.parsers import TurtleParser

    for escaped, value in TurtleParser.echar_map.iteritems():
        string = string.replace(value, '\\' + escaped)
    return '"' + string + '"'

def turtle_representation(node, profile, name_map, bnode_name_maker):
    """Turn a node in an RDF graph into its turtle representation."""
    if node.interfaceName == 'NamedNode':
        name = profile.prefixes.shrink(node)
        if name == node:
            name = '<' + unicode(node) + '>'
        else:
            escape_prefix_local(name)
    elif node.interfaceName == 'BlankNode':
        if node in name_map:
            name = name_map[node]
        else:
            name = bnode_name_maker.next()
            name_map[node] = name
    elif node.interfaceName == 'Literal':
        if node.datatype == profile.resolve('xsd:string'):
            # Simple string.
            name = turtle_string_escape(node.value)
        elif node.datatype == None:
            # String with language.
            name = turtle_string_escape(node.value)
            name += '@' + node.language
        elif node.datatype == profile.resolve('xsd:integer'):
            name = node.value
        elif node.datatype == profile.resolve('xsd:decimal'):
            name = node.value
        elif node.datatype == profile.resolve('xsd:double'):
            name = node.value
        elif node.datatype == profile.resolve('xsd:boolean'):
            name = node.value
        else:
            # Unrecognized data-type.
            name = turtle_string_escape(node.value)
            name += '^' + turtle_representation(node.datatype, profile, None, None)
    return name

def serialize_turtle(graph, f, base=None, profile=None,
                     bnode_name_generator=default_bnode_name_generator):
    """Serialize some turtle from a graph to f, optionally using base IRI base
    and prefix map from profile. If provided, subject_key will be used to order
    subjects, and predicate_key predicates within a subject."""

    if base is not None:
        f.write('@base <' + base + '> .\n')
    if profile is None:
        from pymantic.primitives import Profile
        profile = Profile()
    for prefix, iri in profile.prefixes:
        f.write('@prefix ' + prefix + ': <' + iri + '>\n')
    
    name_map = {}
    bnode_name_maker = bnode_name_generator()
    
    for subject in sorted(graph.subjects()):
        subject_name = turtle_name(subject, profile, name_map, bnode_name_maker)
        indent_size = len(subject_name) + 1
        for triple in sorted(graph.match(subject=name_map[subject]),
                             key=lambda t: predicate_key(t.predicate)):
            pass
