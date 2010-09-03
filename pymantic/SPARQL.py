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
