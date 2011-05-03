from contextlib import contextmanager
from pymantic.raptor.raptor_c import RaptorWorld, RaptorParser

@contextmanager
def raptor_world():
    world = RaptorWorld()
    yield world

def parse(graph, content, base_uri, **kwargs):
    with raptor_world() as world:
        if 'name' in kwargs:
            parser = RaptorParser(world, **kwargs)
            parser.parse(graph, content, base_uri)

