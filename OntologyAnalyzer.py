import xml.etree.ElementTree as ET


class Owl:
    def __init__(self, filename):
        self.nodes = {}
        self.xml = ET.parse(filename)

        for item in self.xml.getroot():
            if item.tag.strip().endswith("Class"):
                owl_class = OwlClass(item)
                self.nodes[owl_class.owl_id] = owl_class

        for owl_id, owl_node in self.nodes.items():
            for i, val in enumerate(owl_node.parents):
                owl_node.parents[i] = self.nodes[val]

    def check_hierarchy(self):
        cycles = []
        for owl_id, owl_node in self.nodes.items():
            if type(owl_node) == OwlClass:
                path = owl_node.has_ancestor(owl_node)
                if path:
                    cycles += path
        return cycles


class OwlNode:
    def __init__(self, owl_id):
        self.owl_id = owl_id
        self.visiting = False

    def __eq__(self, target):
        return self.owl_id == target.owl_id


class OwlClass(OwlNode):
    def __init__(self, xml_node):
        self.parents = []

        for key, value in xml_node.attrib.items():
            if key.strip().endswith("about"):
                OwlNode.__init__(self, value)
                break

        for item in xml_node:
            if item.tag.strip().endswith("subClassOf"):
                for key, value in item.attrib.items():
                    if key.endswith("resource"):
                        self.parents.append(value)

    def has_ancestor(self, target):
        self.visiting = True
        result = []
        if target in self.parents:
            result = [self.owl_id]
        for parent in self.parents:
            if not parent.visiting:
                path = parent.has_ancestor(target)
                if path:
                    result += path
        self.visiting = False
        return result
