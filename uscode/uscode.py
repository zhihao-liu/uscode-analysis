import os
import itertools
from collections import Counter
import json

import util


class USCodeElement:
    def __init__(self, elem_id, terms, refs):
        self.id = elem_id
        self.terms = terms
        self.refs = refs

    def update_features(self, subelem):
        self.terms.update(subelem.terms)
        self.refs.update(subelem.refs)


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
    def __init__(self, chap_id):
        super().__init__(chap_id, Counter(), Counter())


class Title(USCodeElement):
    def __init__(self, title_id):
        super().__init__(title_id, Counter(), Counter())
        self.chapters = {}
        self.sections = {}

    def iter_sections(self):
        return self.sections.values()

    def iter_chapters(self):
        return self.chapters.values()


class USCode:
    def __init__(self):
        self.titles = {}

    @classmethod
    def from_json(cls, path):
        usc = USCode()
        with open(path) as f:
            usc_obj = json.load(f)

        for title_obj in usc_obj['titles'].values():
            title_id = title_obj['id']
            usc.titles[title_id] = title = Title(title_id)

            for chap_obj in title_obj['chapters'].values():
                chap_id = chap_obj['id']
                title.chapters[chap_id] = chap = Chapter(chap_id)

                for sec_obj in chap_obj['sections'].values():
                    sec_id = sec_obj['id']
                    title.sections[sec_id] = sec = Section.from_dict(sec_obj)

                    title.update_features(sec)
                    chap.update_features(sec)

        return usc

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
