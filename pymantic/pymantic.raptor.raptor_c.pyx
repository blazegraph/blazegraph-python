cdef extern from "raptor2/raptor.h":
    ctypedef struct raptor_world:
        pass
    
    raptor_world *raptor_new_world()
    void raptor_free_world(raptor_world *)
    
    ctypedef struct raptor_parser:
        pass
        
    ctypedef enum raptor_term_type:
        RAPTOR_TERM_TYPE_UNKNOWN = 0
        RAPTOR_TERM_TYPE_URI     = 1
        RAPTOR_TERM_TYPE_LITERAL = 2
        RAPTOR_TERM_TYPE_BLANK   = 4
    
    ctypedef struct raptor_uri:
        pass
    
    ctypedef struct raptor_term_blank_value:
        unsigned char *string
        unsigned int string_len
    
    ctypedef struct raptor_term_literal_value:
        unsigned char *string
        unsigned int string_len
        raptor_uri *datatype
        unsigned char *language
        unsigned char language_len

    ctypedef union raptor_term_value:
        raptor_uri *uri
        raptor_term_literal_value literal
        raptor_term_blank_value blank

    ctypedef struct raptor_term:
        raptor_world* world
        int usage
        raptor_term_type type
        raptor_term_value value

    ctypedef struct raptor_statement:
        raptor_world* world
        int usage
        raptor_term* subject
        raptor_term* predicate
        raptor_term* object
        raptor_term* graph

    raptor_parser *raptor_new_parser(raptor_world *, char *)
    void raptor_free_parser(raptor_parser *)
    void raptor_parser_set_statement_handler(raptor_parser *, void *,
                                             void (*)(void*, raptor_statement*))
    void raptor_parser_parse_start(raptor_parser *, raptor_uri *)
    void raptor_parser_parse_chunk(raptor_parser *, unsigned char *, int, int)

    raptor_uri *raptor_new_uri(raptor_world *, unsigned char *)
    unsigned char *raptor_uri_as_string(raptor_uri *)

from pymantic.primitives import Triple, Quad, BlankNode

cdef class RaptorWorld:
    cdef raptor_world *_world
    
    def __cinit__(self):
        self._world = raptor_new_world()
    
    def __dealloc__(self):
        raptor_free_world(self._world)

cdef void parser_statement_handler(void *user, raptor_statement *statement):
    graph = <object>user
    if statement.subject.type == RAPTOR_TERM_TYPE_URI:
        subject = raptor_uri_as_string(statement.subject.value.uri)
    elif statement.subject.type == RAPTOR_TERM_TYPE_BLANK:
        subject = statement.subject.value.blank.string # Make into a blank node.

cdef class RaptorParser:
    cdef raptor_parser *parser
    cdef RaptorWorld world
    
    def __cinit__(self, RaptorWorld world, **kwargs):
        if 'name' in kwargs:
            self.parser = raptor_new_parser(world._world, kwargs['name'])
            self.world = world
    
    def parse(self, graph, content, base_uri):
        raptor_parser_parse_start(self.parser, raptor_new_uri(
            <raptor_world *>self.world._world, base_uri))
        content = content.read()
        raptor_parser_set_statement_handler(self.parser, <void *>graph,
                                            parser_statement_handler)
        raptor_parser_parse_chunk(self.parser, content, len(content), 0)
        raptor_parser_parse_chunk(self.parser, NULL, 0, 1)
    
    def __dealloc__(self):
        raptor_free_parser(self.parser)
