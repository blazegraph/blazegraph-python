"""Provide an interface to SPARQL query endpoints."""

import urllib
from cStringIO import StringIO

import simplejson
import httplib2
import rdflib
from lxml import objectify

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
    
    def __init__(self, query_url):
        self.query_url = query_url
        
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
        response, content = http.request(
            uri=self.query_url, method='POST',
            body=urllib.urlencode({'query': sparql, 'output':output }), 
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            })
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
    
    def __init__(self, query_url, dataset_url):
        super(UpdateableRDFStore, self).__init__(query_url)
        self.dataset_url = dataset_url
    
    def request_url(self, graph_uri):
        return urllib.urlencode({'graph': graph_uri})
    
    def get(self, graph_uri):
        h = httplib2.Http()
        resp, content = h.request(
            uri = self.request_url(graph_uri), method = 'GET',
            headers = {'Accept': 'text/plain,application/rdf+xml,text/turtle,text/rdf+n3',},)
        if resp['status'] != '200':
            raise Exception('Error from Graph Store (%s): %s' %\
                            (resp['status'], content))
        graph = rdflib.ConjunctiveGraph()
        if resp['content-type'].startswith('text/plain'):
            graph.parse(StringIO(content), publiCID=graph_uri, format='nt')
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

class PatchableGraphStore(SPARQLServer):
    """A graph store that supports the optional PATCH method of updating
    RDF graphs."""
    
    def patch(self, graph_uri, changeset):
        h = httplib2.Http()
        
