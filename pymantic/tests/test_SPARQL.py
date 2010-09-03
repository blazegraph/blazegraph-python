import urllib
import unittest

import mock_http

from pymantic.SPARQL import SPARQLServer, SPARQLQueryException

class TestSparql(unittest.TestCase):
    def setUp(self):
        self.mock_port = 48558
    
    def testMockSPARQL(self):
        """Test a SPARQL query against a mocked-up endpoint."""
        test_query = """PREFIX dc: <http://purl.org/dc/terms/>
        SELECT ?product ?title WHERE { ?product dc:title ?title } LIMIT 10"""
        test_json = '{"head": {"vars": ["product", "title"]}, "results": {"bindings": [{"product": {"type": "uri", "value": "test_product"}, "title": {"xml:lang": "en", "type": "literal", "value": "Test Title"}}]}}'
        mock_endpoint = mock_http.MockHTTP(self.mock_port)
        mock_endpoint.expects(
            method='POST', times=mock_http.once, path='/tenuki/sparql',
            headers={'Content-Type': 'application/x-www-form-urlencoded',},
            body=urllib.urlencode({'query': test_query, 'output': 'json',})).will(
                body=test_json, headers={'content-type': 'application/sparql-results+json'})
        sparql = SPARQLServer('http://localhost:%d/tenuki/sparql' % self.mock_port)
        results = sparql.query(test_query)
        mock_endpoint.verify()
        self.assertEqual(results['results']['bindings'][0]['product']['value'],
                         'test_product')
        self.assertEqual(results['results']['bindings'][0]['title']['value'],
                         'Test Title')
    
    def testMockSPARQLError(self):
        """Test a SPARQL query against a mocked-up endpoint."""
        test_query = """PREFIX dc: <http://purl.org/dc/terms/>
        SELECT ?product ?title WHERE { ?product dc:title ?title } LIMIT 10"""
        mock_endpoint = mock_http.MockHTTP(self.mock_port)
        mock_endpoint.expects(
            method='POST', times=mock_http.once, path='/tenuki/sparql',
            headers={'Content-Type': 'application/x-www-form-urlencoded',},
            body=urllib.urlencode({'query': test_query, 'output': 'json',})).will(
                http_code=500)
        sparql = SPARQLServer('http://localhost:%d/tenuki/sparql' % self.mock_port)
        self.assertRaises(SPARQLQueryException, sparql.query, test_query)
        mock_endpoint.verify()
