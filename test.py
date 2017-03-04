import OntologyAnalyzer

owl = OntologyAnalyzer.Owl("./ontologies/Photography.owl")
print(owl.check_hierarchy())
pass
