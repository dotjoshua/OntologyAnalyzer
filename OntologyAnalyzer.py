import xml.etree.ElementTree as ET
import re
import numpy


class Owl:
    def __init__(self, filename):
        self.classes = {}
        self.datatypes = {}
        self.object_properties = {}
        self.datatype_properties = {}
        self.xml = ET.parse(filename)

        for item in self.xml.getroot():
            for node_type, node_class, collection in [("Class", OwlClass, self.classes),
                                                      ("Datatype", OwlDatatype, self.datatypes),
                                                      ("ObjectProperty", OwlObjectProperty, self.object_properties),
                                                      ("DatatypeProperty", OwlDatatypeProperty, self.datatype_properties)]:
                if item.tag.strip().endswith(node_type):
                    instance = node_class(item, self)
                    if instance.owl_id in collection:
                        raise OwlException("Duplicate {} definition found: {}".format(node_type, instance.owl_id))
                    collection[instance.owl_id] = instance
                    break

        for owl_id, owl_node in self.classes.items():
            for i, val in enumerate(owl_node.parents):
                owl_node.parents[i] = self.classes[val]

    def check_hierarchy(self):
        cycles = []
        for owl_id, owl_node in self.classes.items():
            if type(owl_node) == OwlClass:
                path = owl_node.has_ancestor(owl_node)
                if path:
                    cycles += path
        return cycles

    def get_comment_stats(self):
        comments = self.gather_comments()
        if not len(comments):
            return None

        stats = {}
        word_occurrences = {}
        word_count = 0
        total_word_length = 0
        for comment in comments:
            for word in re.split("( |\n|\t)+", comment.text):
                word = re.sub("[^A-Za-z]", "", word).lower()
                if not len(word):
                    continue

                word_count += 1
                total_word_length += len(word)
                if word in word_occurrences.keys():
                    word_occurrences[word] += 1
                else:
                    word_occurrences[word] = 1

        stats["word_occurrences"] = word_occurrences
        stats["avg_word_count"] = word_count / len(comments)
        stats["avg_word_length"] = total_word_length / word_count
        stats["avg_length"] = numpy.mean([len(item) for item in comments])
        stats["avg_line_count"] = numpy.mean([len(item.text.split("\n")) for item in comments])

        stats["total_word_count"] = word_count
        stats["comment_count"] = len(comments)

        return stats

    def gather_comments(self, root=None, depth=1):
        if root is None:
            root = self.xml.getroot()

        comments = []
        for item in root:
            if item.tag.strip().endswith("comment"):
                comments.append(OwlComment(item, depth, root))
            try:
                comments += self.gather_comments(item, depth + 1)
            except TypeError:
                pass
        return comments

    def __str__(self):
        return "<Owl Classes: {}, Datatypes: {}, ObjectProperties: {}, DatatypeProperties: {}, Cyclical Classes: {}>".format(
            len(self.classes), len(self.datatypes), len(self.object_properties), len(self.datatype_properties), len(self.check_hierarchy()))


class OwlNode:
    def __init__(self, owl_id, owl):
        self.owl_id = owl_id
        self.visiting = False
        self.owl = owl

    def __eq__(self, target):
        return self.owl_id == target.owl_id


class OwlComment(OwlNode):
    def __init__(self, xml_node, owl, depth=0, parent=None):
        for key, value in xml_node.attrib.items():
            if key.strip().endswith("about"):
                OwlNode.__init__(self, value, owl)
                break
        self.text = xml_node.text
        self.depth = depth
        self.parent = parent

    def __repr__(self):
        return "<OwlComment Depth: {}, Contents: {}{}>".format(self.depth, self.text[:50].replace("\n", "\\n").strip(),
                                                               "..." if len(self.text) > 50 else "")

    def __len__(self):
        return len(self.text)


class OwlClass(OwlNode):
    def __init__(self, xml_node, owl):
        self.parents = []

        for key, value in xml_node.attrib.items():
            if key.strip().endswith("about"):
                OwlNode.__init__(self, value, owl)
                break

        for item in xml_node:
            if item.tag.strip().endswith("subClassOf"):
                for key, value in item.attrib.items():
                    if key.endswith("resource"):
                        self.parents.append(value)

    def has_ancestor(self, target):
        self.locate_ancestors(target, lambda x, y: x == y)

    def locate_ancestors(self, target, equiv_function):
        self.visiting = True
        result = []
        for parent in self.parents:
            if equiv_function(target, parent):
                result = [self.owl_id]
                break
        for parent in self.parents:
            if not parent.visiting:
                path = parent.locate_ancestors(target, equiv_function)
                if path:
                    result += path
        self.visiting = False
        return result


class OwlDatatype(OwlNode):
    def __init__(self, xml_node, owl):
        self.parents = []

        for key, value in xml_node.attrib.items():
            if key.strip().endswith("about"):
                OwlNode.__init__(self, value, owl)


class OwlObjectProperty(OwlNode):
    def __init__(self, xml_node, owl):
        self.parents = []

        for key, value in xml_node.attrib.items():
            if key.strip().endswith("about"):
                OwlNode.__init__(self, value, owl)
                break


class OwlDatatypeProperty(OwlNode):
    def __init__(self, xml_node, owl):
        self.parents = []

        for key, value in xml_node.attrib.items():
            if key.strip().endswith("about"):
                OwlNode.__init__(self, value, owl)
                break


class OwlException(Exception):
    def __init__(self, *args):
        super(OwlException, self).__init__(*args)
