import urllib
import unittest
from nose import SkipTest

import mock_http

# from pymantic.sparql import SPARQLServer, SPARQLQueryException

class TestSparql(unittest.TestCase):
    def setUp(self):
        raise SkipTest
        self.mock_port = 48558
        self.mock_endpoint = mock_http.MockHTTP(self.mock_port)
    
    def testMockSPARQL(self):
        """Test a SPARQL query against a mocked-up endpoint."""
        test_query = """PREFIX dc: <http://purl.org/dc/terms/>
        SELECT ?product ?title WHERE { ?product dc:title ?title } LIMIT 10"""
        test_json = '{"head": {"vars": ["product", "title"]}, "results": {"bindings": [{"product": {"type": "uri", "value": "test_product"}, "title": {"xml:lang": "en", "type": "literal", "value": "Test Title"}}]}}'
        
        self.mock_endpoint.expects(
            method='POST', times=mock_http.once, path='/tenuki/sparql',
            headers={'Content-Type': 'application/x-www-form-urlencoded',},
            params={'query': test_query, 'output': 'json',}).will(
                body=test_json, headers={'content-type': 'application/sparql-results+json'})
        sparql = SPARQLServer('http://localhost:%d/tenuki/sparql' % self.mock_port)
        try:
            results = sparql.query(test_query)
        finally:
            self.assert_(self.mock_endpoint.verify())
        self.assertEqual(results['results']['bindings'][0]['product']['value'],
                         'test_product')
        self.assertEqual(results['results']['bindings'][0]['title']['value'],
                         'Test Title')
    
    def testMockSPARQLError(self):
        """Test a SPARQL query against a mocked-up endpoint."""
        test_query = """PREFIX dc: <http://purl.org/dc/terms/>
        SELECT ?product ?title WHERE { ?product dc:title ?title } LIMIT 10"""
        self.mock_endpoint.expects(
            method='POST', times=mock_http.once, path='/tenuki/sparql',
            headers={'Content-Type': 'application/x-www-form-urlencoded',},
            params={'query': test_query, 'output': 'json',}).will(
                http_code=500)
        sparql = SPARQLServer('http://localhost:%d/tenuki/sparql' % self.mock_port)
        try:
            self.assertRaises(SPARQLQueryException, sparql.query, test_query)
        finally:
            self.assert_(self.mock_endpoint.verify())
