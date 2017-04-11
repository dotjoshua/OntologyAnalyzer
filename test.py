import OntologyAnalyzer

for ontology_name in ["Photography", "marinetlo", "combined subject and object rich ontologies - Copy"]:
    owl = OntologyAnalyzer.Owl("./ontologies/{}.owl".format(ontology_name))
    print(owl)
