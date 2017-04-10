import OntologyAnalyzer

owl = OntologyAnalyzer.Owl("./ontologies/Photography.owl")
for class_name in owl.classes:
    print(class_name)
