cdef extern from "raptor2/raptor.h":
    ctypedef struct raptor_world:
        pass
    
    raptor_world *raptor_new_world()
    void raptor_free_world(raptor_world *)
    
    ctypedef struct raptor_parser:
        pass
    
    raptor_parser *raptor_new_parser(raptor_world *, char *)
    void raptor_free_parser(raptor_parser *)

cdef class RaptorWorld:
    cdef raptor_world *_world
    
    def __cinit__(self):
        self._world = raptor_new_world()
    
    def __dealloc__(self):
        raptor_free_world(self._world)

cdef class RaptorParser:
    cdef raptor_parser *parser
    
    def __cinit__(self, RaptorWorld world, **kwargs):
        if 'name' in kwargs:
            self.parser = raptor_new_parser(world._world, kwargs['name'])
    
    def __dealloc__(self):
        raptor_free_parser(self.parser)
