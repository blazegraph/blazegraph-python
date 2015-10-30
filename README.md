# blazegraph-python
Python client library for Blazegraph
(Pymantic fork)
========

Semantic Web and RDF library for Python


Quick Start
-----------
```python
from pymantic import sparql

server = sparql.SPARQLServer('http://127.0.0.1:9999/bigdata/sparql')

# Loading data to Blazegraph
server.update('load <file:///tmp/data.n3>')

# Executing query
result = server.query('select * where { <http://blazegraph.com/blazegraph> ?p ?o }')
for b in result['results']['bindings']:
    print "%s %s" (b['p']['value'], b['o']['value']
```

Requirements
------------

Pymantic requires Python 2.6 or higher. Lepl is used for the Turtle and NTriples parser. httplib2 is used for HTTP 
requests and the SPARQL client. simplejson and lxml are required by the SPARQL client as well.


Install
------

```
$ python setup.py install
```

This will install Pymantic and all its dependencies.


Documentation
=============

Generating a local copy of the documentation requires Sphinx:

```
$ easy_install Sphinx
```

