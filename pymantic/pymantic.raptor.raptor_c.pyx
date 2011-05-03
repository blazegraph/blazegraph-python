cdef extern from "raptor2/raptor.h":
    ctypedef struct raptor_world:
        pass
    
    raptor_world *raptor_new_world()
    void raptor_free_world(raptor_world *)
    
    ctypedef struct raptor_parser:
        pass
    
    ctypedef struct raptor_statement:
        pass
    
    ctypedef struct raptor_uri:
        pass
    
    raptor_parser *raptor_new_parser(raptor_world *, char *)
    void raptor_free_parser(raptor_parser *)
    void raptor_parser_set_statement_handler(raptor_parser *, void *,
                                             void (*)(void*, raptor_statement*))
    void raptor_parser_parse_start(raptor_parser *, raptor_uri *)
    void raptor_parser_parse_chunk(raptor_parser *, unsigned char *, int, int)

    raptor_uri *raptor_new_uri(raptor_world *, unsigned char *)

cdef class RaptorWorld:
    cdef raptor_world *_world
    
    def __cinit__(self):
        self._world = raptor_new_world()
    
    def __dealloc__(self):
        raptor_free_world(self._world)

cdef void parser_statement_handler(void *user, raptor_statement *statement):
    graph = <object>user
    print "A statement!"

cdef class RaptorParser:
    cdef raptor_parser *parser
    cdef RaptorWorld world
    
    def __cinit__(self, RaptorWorld world, **kwargs):
        if 'name' in kwargs:
            self.parser = raptor_new_parser(world._world, kwargs['name'])
            self.world = world
    
    def parse(self, graph, content):
        raptor_parser_parse_start(self.parser, raptor_new_uri(
            <raptor_world *>self.world._world, 'http://example.com/'))
        content = content.read()
        print content
        raptor_parser_set_statement_handler(self.parser, <void *>graph,
                                            parser_statement_handler)
        raptor_parser_parse_chunk(self.parser, content, len(content), 0)
        raptor_parser_parse_chunk(self.parser, NULL, 0, 1)
    
    def __dealloc__(self):
        raptor_free_parser(self.parser)
