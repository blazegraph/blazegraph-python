from primitives import Graph, BlankNode, Triple
from rdf import Resource, register_class


class ChangeTrackingGraph(Graph):

    def __init__(self, graph_uri=None):
        super(Graph, self).__init__()
        self._added = set()
        self._removed = set()

    def add(self, triple):
        if not self.contains(triple):
            super(Graph, self).add(triple)
            self._added.add(triple)

    def remove(self, triple):
        if self.contains(triple):
            super(Graph, self).remove(triple)
            self._removed.add(triple)

    def changes(self, cls=Changes):
        return cls(added=frozenset(self._added),
                    removed=frozenset(self._removed))


class ChangeSet(object):

    def __init__(self, added, removed):
        self.added = added
        self.removed = removed

CHANGESET_NS = "http://purl.org/vocab/changeset/schema#"
NS_DICT = dict(cs=CHANGESET_NS)


class CSR(Resource):
    namespaces = NS_DICT


@register_class("cs:ChangeSet")
class CS(CSR):
    scalars = ["cs:subjectOfChange"]


@register_class("rdf:Statement")
class Statement(CSR):
    scalars = ["rdf:subject", "rdf:predicate", "rdf:object"]

    @classmethod
    def from_triple(cls, graph, triple):
        statement = Statement.new(graph)
        statement["rdf:subject"] = triple.subject
        statement["rdf:predicate"] = triple.predicate
        statement["rdf:object"] = triple.object
        return statement


class ChangeSetGraph(ChangeSet):

    def as_resource(self):
        change_graph = Graph()
        cs = CS.new(change_graph)
        addition_statements = set()
        for triple in self.added:
            addition_statements.add(Statement.from_triple(change_graph, triple))
        cs["cs:addition"] = addition_statements
        removal_statements = set()
        for triple in self.removed:
            removal_statements.add(Statement.from_triple(change_graph, triple))
        cs["cs:removal"] = removal_statements
        return cs
