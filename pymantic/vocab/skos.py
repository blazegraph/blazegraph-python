from pymantic.rdf import Resource, register_class

SKOS_NS = "http://www.w3.org/2004/02/skos/core#"
NS_DICT = dict(skos = SKOS_NS)

class SKOSResource(Resource):
    namespaces = NS_DICT
    
    scaler = ['skos:prefLabel']

@register_class("skos:Concept")
class Concept(SKOSResource):
    pass

@register_class("skos:ConceptScheme")
class ConceptScheme(SKOSResource):
    pass
