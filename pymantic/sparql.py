"""Provide an interface to SPARQL query endpoints."""

from cStringIO import StringIO
import datetime
import urllib
import urlparse

import httplib2
from lxml import objectify
import pytz
import rdflib
import simplejson

import logging

log = logging.getLogger(__name__)

class SPARQLQueryException(Exception):
    """Raised when the SPARQL store returns an HTTP status code other than 200 OK."""
    pass

class UnknownSPARQLReturnTypeException(Exception):
    """Raised when the SPARQL store provides a response with an unrecognized content-type."""
    pass

class SPARQLServer(object):
    """A server that can run SPARQL queries."""

    def __init__(self, query_url, post_queries = True):
        self.query_url = query_url
        self.post_queries = post_queries

    acceptable_sparql_responses = [
        'application/sparql-results+json',
        'application/rdf+xml',
        'application/sparql-results+xml',
    ]

    def query(self, sparql, output='json'):
        """Executes a SPARQL query. The return type varies based on what the
        SPARQL store responds with:

        * application/rdf+xml: an rdflib.ConjunctiveGraph
        * application/sparql-results+json: A dictionary from simplejson
        * application/sparql-results+xml: An lxml.objectify structure

        :param sparql: The SPARQL to execute.
        :returns: The results of the query from the SPARQL store."""
        http = httplib2.Http()

        log.debug("Querying: %s with: %r", self.query_url, sparql)
        if self.post_queries:
            response, content = http.request(
                uri=self.query_url, method='POST',
                body=urllib.urlencode({'query': sparql, 'output':output }),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": ','.join(self.acceptable_sparql_responses),
                })
        else:
            params = urllib.urlencode({'query': sparql, 'output':output })
            response, content = http.request(
                uri=self.query_url + '?' + params, method='GET',
                headers={
                    "Accept": ','.join(self.acceptable_sparql_responses),
            })
        if response['status'] == '204':
            return True
        if response['status'] != '200':
            raise SPARQLQueryException('%s: %s' % (response, content))
        if response['content-type'].startswith('application/rdf+xml'):
            graph = rdflib.ConjunctiveGraph()
            graph.parse(StringIO(content), self.query_url)
            return graph
        elif response['content-type'].startswith('application/sparql-results+json'):
            return simplejson.loads(content)
        elif response['content-type'].startswith('application/sparql-results+xml'):
            return objectify.parse(StringIO(content))
        else:
            raise UnknownSPARQLReturnTypeException('Got content of type: %s' %\
                                                   response['content-type'])

class UpdateableGraphStore(SPARQLServer):
    """SPARQL server class that is capable of interacting with SPARQL 1.1
    graph stores."""

    def __init__(self, query_url, dataset_url, param_style = True, **kwargs):
        super(UpdateableGraphStore, self).__init__(query_url, **kwargs)
        self.dataset_url = dataset_url
        self.param_style = param_style

    acceptable_graph_responses = [
        'text/plain',
        'application/rdf+xml',
        'text/turtle',
        'text/rdf+n3',
    ]

    def request_url(self, graph_uri):
        if self.param_style:
            return self.dataset_url + '?' + urllib.urlencode({'graph': graph_uri})
        else:
            return urlparse.urljoin(self.dataset_url, urllib.quote_plus(graph_uri))

    def get(self, graph_uri):
        h = httplib2.Http()
        resp, content = h.request(
            uri = self.request_url(graph_uri), method = 'GET',
            headers = {'Accept': ','.join(self.acceptable_graph_responses),},)
        if resp['status'] != '200':
            raise Exception('Error from Graph Store (%s): %s' %\
                            (resp['status'], content))
        graph = rdflib.ConjunctiveGraph()
        if resp['content-type'].startswith('text/plain'):
            graph.parse(StringIO(content), publicID=graph_uri, format='nt')
        elif resp['content-type'].startswith('application/rdf+xml'):
            graph.parse(StringIO(content), publicID=graph_uri, format='xml')
        elif resp['content-type'].startswith('text/turtle'):
            graph.parse(StringIO(content), publicID=graph_uri, format='turtle')
        elif resp['content-type'].startswith('text/rdf+n3'):
            graph.parse(StringIO(content), publicID=graph_uri, format='n3')
        return graph

    def delete(self, graph_uri):
        h = httplib2.Http()
        resp, content = h.request(uri = self.request_url(graph_uri),
                                  method = 'DELETE')
        if resp['status'] != '200' and resp['status'] != '202':
            raise Exception('Error from Graph Store (%s): %s' %\
                            (resp['status'], content))

    def put(self, graph_uri, graph):
        h = httplib2.Http()
        graph_triples = graph.serialize(format = 'nt')
        resp, content = h.request(uri = self.request_url(graph_uri),
                                  method = 'PUT', body = graph_triples,
                                  headers = {'content-type': 'text/plain',},)
        if resp['status'] not in ('200', '201', '204'):
            raise Exception('Error from Graph Store (%s): %s' %\
                            (resp['status'], content))

    def post(self, graph_uri, graph):
        h = httplib2.Http()
        graph_triples = graph.serialize(format = 'nt')
        if graph_uri != None:
            resp, content = h.request(uri = self.request_url(graph_uri),
                                      method = 'POST', body = graph_triples,
                                      headers = {'content-type': 'text/plain',},)
            if resp['status'] not in ('200', '201', '204'):
                raise Exception('Error from Graph Store (%s): %s' %\
                                (resp['status'], content))
        else:
            resp, content = h.request(uri = self.dataset_url, method = 'POST',
                                      body = graph_triples,
                                      headers = {'content-type': 'text/plain',},)
            if resp['status'] != '201':
                raise Exception('Error from Graph Store (%s): %s' %\
                                (resp['status'], content))

class PatchableGraphStore(UpdateableGraphStore):
    """A graph store that supports the optional PATCH method of updating
    RDF graphs."""

    def patch(self, graph_uri, changeset):
        h = httplib2.Http()
        graph_xml = changeset.serialize(format = 'xml', encoding='utf-8')
        resp, content = h.request(
            uri = self.request_url(graph_uri), method = 'PATCH', body = graph_xml,
            headers = {'content-type': 'application/vnd.talis.changeset+xml',},)
        if resp['status'] not in ('200', '201', '204'):
            raise Exception('Error from Graph Store (%s): %s' %\
                            (resp['status'], content))
        return True

def changeset(a,b, graph_uri):
    """Create an RDF graph with the changeset between graphs a and b"""
    cs = rdflib.Namespace("http://purl.org/vocab/changeset/schema#")
    graph = rdflib.Graph()
    graph.namespace_manager.bind("cs", cs)
    removal, addition = differences(a,b)
    change_set = rdflib.BNode()
    graph.add((change_set, rdflib.RDF.type, cs["ChangeSet"]))
    graph.add((change_set, cs["createdDate"], rdflib.Literal(datetime.datetime.now(pytz.UTC).isoformat())))
    graph.add((change_set, cs["subjectOfChange"], rdflib.URIRef(graph_uri)))

    for stmt in removal:
        statement = reify(graph, stmt)
        graph.add((change_set, cs["removal"], statement))
    for stmt in addition:
        statement = reify(graph, stmt)
        graph.add((change_set, cs["addition"], statement))
    return graph

def reify(graph, statement):
    """Add reifed statement to graph"""
    s,p,o = statement
    statement_node = rdflib.BNode()
    graph.add((statement_node, rdflib.RDF.type, rdflib.RDF.Statement))
    graph.add((statement_node, rdflib.RDF.subject,s))
    graph.add((statement_node, rdflib.RDF.predicate, p))
    graph.add((statement_node, rdflib.RDF.object, o))
    return statement_node

def differences(a, b, exclude=[]):
    """Return (removes,adds) excluding statements with a predicate in exclude"""
    exclude = [rdflib.URIRef(excluded) for excluded in exclude]
    return ([s for s in a if s not in b and s[1] not in exclude],
            [s for s in b if s not in a and s[1] not in exclude])
