import os
import itertools
import json
import xml.etree.ElementTree as ET

import util


class USCodeElement:
    @property
    def location(self):
        return tuple(div[1:] for div in self.id.split('/'))

class Section(USCodeElement):
    def __init__(self, section_dict):
        self.id = section_dict['id']
        self.text = section_dict['text']
        self.terms = section_dict['terms']
        self.refs = section_dict['refs']


class Title(USCodeElement):
    def __init__(self, title_dict):
        self.id = title_dict['id']
        self.sections = {sec_id: Section(sec_dict)
                         for sec_id, sec_dict in title_dict['sections'].items()}

    def get_sections(self):
        return self.sections.values()

    def find_section(self, section_num):
        return self.sections.get('{}/s{}'.format(self.id, section_num))


class USCode:
    def __init__(self, usc_dict):
        self.titles = {title_id: Title(title_dict)
                       for title_id, title_dict in usc_dict['titles'].items()}

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            usc_dict = json.load(f)
        return cls(usc_dict)

    def get_titles(self):
        return self.titles.values()

    def get_sections(self):
        return itertools.chain.from_iterable(title.get_sections() for title in self.get_titles())

    def find_section(self, title_num, section_num):
        title = self.titles.get('t{}'.format(title_num))
        return title and title.find_section(section_num)
