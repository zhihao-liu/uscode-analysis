import os
import itertools
import xml.etree.ElementTree as ET
from boolean import BooleanAlgebra


ns_prefix = '{http://xml.house.gov/schemas/uslm/1.0}'
new_line_tags = {'section', 'subsection', 'paragraph', 'subparagraph', 'clause', 'subclause'}
boolean = BooleanAlgebra()


# utility functions
def prefix_tag(tag):
    return ns_prefix + tag


def deprefix_tag(tag):
    return tag[len(ns_prefix):]


def is_new_line(tag):
    return deprefix_tag(tag) in new_line_tags


def contains_text(node, text):
    text = text.lower()
    return any(child.text and text in child.text.lower() for child in node.iter(prefix_tag('content')))


def booleanify(val):
    return boolean.TRUE if val else boolean.FALSE


# wrapper of a section node
class Section:
    def __init__(self, node):
        self.node = node

    def to_string(self):
        str_builder = []
        for child in self.node.iter():
            if str_builder and is_new_line(child.tag):
                str_builder.append('\n')
            if child.text:
                str_builder.append(child.text)
                str_builder.append(' ')

        return ''.join(str_builder)

    @property
    def identifier(self):
        return self.node.attrib.get('identifier')

    @property
    def title_id(self):
        identifier = self.identifier
        return identifier and identifier.split('/')[-2][1:]

    @property
    def section_id(self):
        identifier = self.identifier
        return identifier and identifier.split('/')[-1][1:]


# wrapper of the whole US Code with search functions
class USCode:
    def __init__(self, xml_dir):
        self.xml_dir = xml_dir
        self.titles = {str(i): None for i in range(1, 55) if i != 53}

    def get_title(self, title_id):
        # lazy initialization of titles
        if title_id not in self.titles:
            return None
        if not self.titles[title_id]:
            self.titles[title_id] = ET.parse(os.path.join(self.xml_dir, 'usc%s.xml' % title_id))
        return self.titles[title_id]

    def find_section_by_id(self, title_id, section_id):
        title = self.get_title(title_id)
        if not title:
            return None
        node = title.getroot().find('.//%s[@identifier="/us/usc/t%s/s%s"]' % (prefix_tag('section'), title_id, section_id))
        return node and Section(node)

    def search_sections_fulltext(self, title_id, text):
        results = []
        title = self.get_title(title_id)
        for sec_node in title.getroot().iter(prefix_tag('section')):
            if contains_text(sec_node, text):
                results.append(Section(sec_node))
        return results

    def search_sections_boolean(self, title_id, query):
        title = self.get_title(title_id)
        expr = boolean.parse(query, simplify=True)

        results = []
        for sec_node in title.getroot().iter(prefix_tag('section')):
            boolean_map = {sym: booleanify(contains_text(sec_node, sym.obj)) for sym in expr.symbols}
            if expr.subs(boolean_map, simplify=True) == boolean.TRUE:
                results.append(Section(sec_node))
        return results

    def search_all_sections_fulltext(self, text):
        all_results = (self.search_sections_fulltext(title_id, text) for title_id in self.titles)
        return list(itertools.chain.from_iterable(all_results))

    def search_all_sections_boolean(self, query):
        all_results = (self.search_sections_boolean(title_id, query) for title_id in self.titles)
        return list(itertools.chain.from_iterable(all_results))
