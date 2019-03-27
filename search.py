import itertools
from boolean import BooleanAlgebra
import networkx as nx

from uscode import Section
from citation_network import CitationNetwork
import util


boolean = BooleanAlgebra()


def booleanify(val):
    return boolean.TRUE if val else boolean.FALSE


class SearchResult:
    def __init__(self, result, occurrence):
        self.result = result
        self.occurrence = occurrence


class SearchEngine:
    def __init__(self, uscode):
        self.uscode = uscode
        self.citation_network = CitationNetwork(uscode.get_sections())
        self.pagerank = nx.pagerank(self.citation_network.graph)

    def search(self, query, mode='fulltext'):
        validate = None
        if mode == 'fulltext':
            validate = self._fulltext_validator(query)
        elif mode == 'boolean':
            validate = self._boolean_validator(query)
        else:
            raise Exception("Illegal mode")

        results = []
        for sec in self.uscode.get_sections():
            valid, count = validate(sec)
            if valid:
                results.append(SearchResult(sec, count))
        return results

    def rank(self, results, signal='occurrence'):
        if signal == 'occurrence':
            results.sort(key=lambda x: x.occurrence, reverse=True)
        elif signal == 'pagerank':
            results.sort(key=lambda x: self.pagerank[x.result.id], reverse=True)
        elif signal == 'indegree':
            results.sort(key=lambda x: self.citation_network.graph.in_degree(x.result.id), reverse=True)
        else:
            raise Exception("Illegal rank")

    @staticmethod
    def _fulltext_validator(query):
        terms = {util.transform_word(w) for w in query.split()}

        def validate(section):
            valid = all(w in section.terms for w in terms)
            if not valid:
                return False, -1

            count = sum(section.terms.get(w, 0) for w in terms)
            return True, count

        return validate

    @staticmethod
    def _boolean_validator(query):
        expr = boolean.parse(query, simplify=True)
        for sym in expr.get_symbols():
            sym.obj = util.transform_word(sym.obj)

        def validate(section):
            boolean_map = {sym: booleanify(sym.obj in section.terms) for sym in expr.symbols}
            valid = expr.subs(boolean_map, simplify=True) == boolean.TRUE
            if not valid:
                return False, -1

            count = sum(section.terms.get(sym.obj, 0) for sym in expr.symbols)
            return True, count

        return validate
