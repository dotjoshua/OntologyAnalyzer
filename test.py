import OntologyAnalyzer

owl = OntologyAnalyzer.Owl("./ontologies/Photography.owl")
print(owl.get_comment_stats())
pass
