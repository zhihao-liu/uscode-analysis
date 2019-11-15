import os
import itertools
from collections import Counter
import json

import util


class USCodeElement:
    def __init__(self, id, terms, refs):
        self.id = id
        self.terms = terms
        self.refs = refs

    def accumulate(self, iter_elements):
        elements = {}
        terms = Counter()
        refs = Counter()
        for elem in iter_elements:
            elements[elem.id] = elem
            terms.update(elem.terms)
            refs.update(elem.refs)
        return elements, terms, refs


class Section(USCodeElement):
    def __init__(self, sec_id, terms, refs, text):
        super().__init__(sec_id, terms, refs)
        self.text = text

    @classmethod
    def from_dict(cls, sec_dict):
        return cls(sec_dict['id'],
                   Counter(sec_dict['terms']),
                   Counter(sec_dict['refs']),
                   sec_dict['text'])


class Chapter(USCodeElement):
    def __init__(self, chap_id, iter_sections):
        sections, terms, refs = self.accumulate(iter_sections)
        super().__init__(id, terms, refs)
        self.sections = sections

    @classmethod
    def from_dict(cls, chap_dict):
        chap_id = chap_dict['id']
        iter_sections = (Section.from_dict(sec_dict) for sec_dict in chap_dict['sections'].values())
        return cls(chap_id, iter_sections)

    def iter_sections(self):
        return self.sections.values()


class Title(USCodeElement):
    def __init__(self, title_id, iter_chapters):
        chapters, terms, refs = self.accumulate(iter_chapters)
        super().__init__(title_id, terms, refs)
        self.chapters = chapters
        self.sections = {sec.id: sec for chap in chapters.values() for sec in chap.iter_sections()}

    @classmethod
    def from_dict(cls, title_dict):
        title_id = title_dict['id']
        iter_chapters = (Chapter.from_dict(chap_dict) for chap_dict in title_dict['chapters'].values())
        return cls(title_id, iter_chapters)

    def iter_sections(self):
        return self.sections.values()

    def iter_chapters(self):
        return self.chapters.values()


class USCode:
    def __init__(self, titles):
        self.titles = {title.id: title for title in titles}

    @classmethod
    def from_dict(cls, usc_dict):
        titles = (Title.from_dict(title_dict) for title_dict in usc_dict['titles'].values())
        return cls(titles)

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            usc_dict = json.load(f)
        return USCode.from_dict(usc_dict)

    def iter_titles(self):
        return self.titles.values()

    def iter_chapters(self):
        return itertools.chain.from_iterable(title.iter_chapters() for title in self.iter_titles())

    def iter_sections(self):
        return itertools.chain.from_iterable(title.iter_sections() for title in self.iter_titles())

    def get_section(self, sec_id):
        title_id = util.extract_title_id(sec_id)
        return self.titles[title_id].sections[sec_id]

    def find_section(self, title_num, section_num):
        try:
            section_id = 't{}/s{}'.format(title_num, section_num)
            return self.section(section_id)
        except:
            return None
