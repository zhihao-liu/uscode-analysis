import os
import itertools
import json

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
        self.sections_ = {sec_id: Section(sec_dict)
                         for sec_id, sec_dict in title_dict['sections'].items()}

    def sections(self):
        return list(self.iter_sections())

    def iter_sections(self):
        return self.sections_.values()

    def section(self, section_id):
        return self.sections_[section_id]


class USCode:
    def __init__(self, usc_dict):
        self.titles_ = {title_id: Title(title_dict)
                        for title_id, title_dict in usc_dict['titles'].items()}

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            usc_dict = json.load(f)
        return cls(usc_dict)

    def titles(self):
        return list(self.iter_titles())

    def iter_titles(self):
        return self.titles_.values()

    def sections(self):
        return list(self.iter_sections())

    def iter_sections(self):
        return itertools.chain.from_iterable(title.iter_sections() for title in self.iter_titles())

    def title(self, title_id):
        return self.titles_[title_id]

    def section(self, section_id):
        title_id = extract_title_id(section_id)
        return self.title(title_id).section(section_id)

    def find_section(self, title_num, section_num):
        try:
            section_id = 't{}/s{}'.format(title_num, section_num)
            return self.section(section_id)
        except:
            return None
