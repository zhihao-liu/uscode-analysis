import logging
import os
import itertools
import xml.etree.ElementTree as ET
import util


# wrapper of a section element
class Section:
    def __init__(self, elem):
        self.elem = elem

    def get_attrib(self, key):
        return self.elem.attrib.get(key)

    def to_string(self):
        str_builder = []
        for child in self.elem.iter():
            if str_builder and util.is_newline_tag(child.tag):
                str_builder.append('\n')
            if child.text:
                str_builder.append(child.text)
                str_builder.append(' ')

        return ''.join(str_builder)

    @property
    def location(self):
        sec_id = self.get_attrib('identifier')
        if not sec_id:
            return None
        parts = sec_id.split('/')
        return parts[-2][1:], parts[-1][1:]


class Title:
    def __init__(self, elem):
        self.elem = elem

    def get_attrib(self, key):
        return self.elem.attrib.get(key)

    def sections(self):
        sec_elems = self.elem.iter(util.prefix_tag('section'))
        for elem in sec_elems:
            sec_id = elem.attrib.get('identifier')
            if sec_id and util.is_uscode_id(sec_id):
                yield Section(elem)

    def find_section(self, section_num):
        xpath = './/{}[@identifier="{}/s{}"]'.format(util.prefix_tag('section'),
                                                     self.get_attrib('identifier'),
                                                     section_num)
        elem = title.elem.find(xpath)
        return elem and Section(elem)


# wrapper of the whole US Code with search functions
class USCode:
    def __init__(self, xml_dir):
        self.xml_dir = xml_dir
        self.titles = {}

        logging.info("Loading data...")
        for filename in os.listdir(xml_dir):
            title_num = filename[3:-4].lstrip('0').lower()
            tree = ET.parse(os.path.join(xml_dir, filename))
            self.titles[title_num] = Title(tree.getroot())

    def all_sections(self):
        return itertools.chain.from_iterable(title.sections() for title in self.titles.values())

    def find_section(self, title_num, section_num):
        title = self.titles.get(title_num)
        return title and title.find_section(section_num)
