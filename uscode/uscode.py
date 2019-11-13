import os
import itertools
from collections import Counter
import json

import util


class USCodeElement:
    @property
    def location(self):
        return tuple(div[1:] for div in self.id.split('/'))


class Section(USCodeElement):
    def __init__(self, section_id, text, terms, refs):
        self.id = section_id
        self.text = text
        self.terms_ = terms
        self.refs_ = refs

    @classmethod
    def from_dict(cls, section_dict):
        return cls(section_dict['id'],
                   section_dict['text'],
                   Counter(section_dict['terms']),
                   Counter(section_dict['refs']))


class Title(USCodeElement):
    def __init__(self, title_id, sections):
        self.id = title_id
        self.sections_ = {sec.id: sec for sec in sections}

    @classmethod
    def from_dict(cls, title_dict):
        sections = (Section.from_dict(sec_dict) for sec_dict in title_dict['sections'].values())
        return cls(title_dict['id'], sections)

    def sections(self):
        return self.sections_.values()

    def section(self, section_id):
        return self.sections_[section_id]


class USCode:
    def __init__(self, titles):
        self.titles_ = {title.id: title for title in titles}

    @classmethod
    def from_dict(cls, usc_dict):
        titles = (Title.from_dict(title_dict) for title_dict in usc_dict['titles'].values())
        return cls(titles)

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            usc_dict = json.load(f)
        return USCode.from_dict(usc_dict)

    def titles(self):
        return self.titles_.values()

    def sections(self):
        return itertools.chain.from_iterable(title.sections() for title in self.titles())

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
