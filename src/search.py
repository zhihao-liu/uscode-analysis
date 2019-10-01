import itertools
from boolean import BooleanAlgebra
import networkx as nx

from uscode import Section
import citation_network
import util


boolean = BooleanAlgebra()


def booleanify(val):
    return boolean.TRUE if val else boolean.FALSE


class SearchResult:
    def __init__(self, result, occurrence):
        self.result = result
        self.occurrence = occurrence


class SearchEngine:
    def __init__(self, uscode, network=None):
        self.uscode = uscode
        self.network = network or citation_network.build(uscode)
        self.pagerank = nx.pagerank(self.network)

    def search(self, query, mode='fulltext'):
        validate = None
        if mode == 'fulltext':
            validate = self._fulltext_validator(query)
        elif mode == 'boolean':
            validate = self._boolean_validator(query)
        else:
            raise Exception("Illegal mode")

        results = []
        for sec in self.uscode.iter_sections():
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
            results.sort(key=lambda x: self.network.in_degree(x.result.id), reverse=True)
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
