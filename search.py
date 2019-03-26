import itertools
from boolean import BooleanAlgebra
import networkx as nx

from uscode import Section
from citation_network import CitationNetwork
import util


boolean = BooleanAlgebra()


def booleanify(val):
    return boolean.TRUE if val else boolean.FALSE


class SearchEngine:
    def __init__(self, uscode):
        self.uscode = uscode
        self.citation_network = CitationNetwork(uscode.sections())
        self.pagerank = nx.pagerank(self.citation_network.graph)

    def search(self, query, mode='fulltext', rank='pagerank'):
        search_title = None
        if mode == 'fulltext':
            search_title = self._search_title_fulltext
        elif mode == 'boolean':
            search_title = self._search_title_boolean
        else:
            raise Exception("Illegal mode")

        rank_results = None
        if rank == 'pagerank':
            rank_results = self._rank_results_with_pagerank
        elif rank == 'indegree':
            rank_results = self._rank_results_by_indegree
        else:
            raise Exception("Illegal rank")

        results = (search_title(title, query) for title in self.uscode.titles.values())
        results = list(itertools.chain.from_iterable(results))
        rank_results(results)
        return results

    @staticmethod
    def _search_title_fulltext(title, query):
        for sec_elem in title.elem.iter(util.prefix_tag('section')):
            sec_id = sec_elem.attrib.get('identifier')
            if not sec_id or not util.is_uscode_id(sec_id):
                continue

            if util.contains_text(sec_elem, query):
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

    def _rank_results_by_indegree(self, results):
        results.sort(key=lambda x: self.citation_network.graph.in_degree(x.id), reverse=True)

    def _rank_results_with_pagerank(self, results):
        results.sort(key=lambda x: self.pagerank[x.id], reverse=True)
