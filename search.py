import itertools
from boolean import BooleanAlgebra
from uscode import Section
from citation_network import CitationNetwork
import util


boolean = BooleanAlgebra()


def booleanify(val):
    return boolean.TRUE if val else boolean.FALSE


class Search:
    def __init__(self, uscode, citation_network=None):
        self.uscode = uscode
        self.network = citation_network or CitationNetwork(uscode.all_sections())

    def fulltext(self, text):
        results = [(sec, self.network.nodes[sec.attrib('identifier')].indegree)
                   for sec in self._search_all_fulltext(text)]
        self._rank_results(results)
        return results

    def boolean(self, query):
        results = [(sec, self.network.nodes[sec.attrib('identifier')].indegree)
                   for sec in self._search_all_boolean(query)]
        self._rank_results(results)
        return results

    def _search_all_fulltext(self, text):
        return itertools.chain.from_iterable(self._search_title_fulltext(title, text)
                                             for title in self.uscode.titles.values())

    def _search_all_boolean(self, query):
        return itertools.chain.from_iterable(self._search_title_boolean(title, query)
                                             for title in self.uscode.titles.values())

    @staticmethod
    def _search_title_fulltext(title, text):
        for sec_elem in title.elem.iter(util.prefix_tag('section')):
            sec_id = sec_elem.attrib.get('identifier')
            if not sec_id or not util.is_uscode_id(sec_id):
                continue

            if util.contains_text(sec_elem, text):
                yield Section(sec_elem)

    @staticmethod
    def _search_title_boolean(title, query):
        expr = boolean.parse(query, simplify=True)
        for sec_elem in title.elem.iter(util.prefix_tag('section')):
            sec_id = sec_elem.attrib.get('identifier')
            if not sec_id or not util.is_uscode_id(sec_id):
                continue

            boolean_map = {sym: booleanify(util.contains_text(sec_elem, sym.obj))
                           for sym in expr.symbols}
            if expr.subs(boolean_map, simplify=True) == boolean.TRUE:
                yield Section(sec_elem)

    @staticmethod
    def _rank_results(results):
        results.sort(key=lambda x: x[1], reverse=True)
