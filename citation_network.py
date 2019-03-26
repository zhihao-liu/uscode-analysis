import logging
import networkx as nx

from uscode import Section, USCode
import util


class CitationNetwork:
    def __init__(self, sections):
        self.graph = nx.DiGraph()
        self._build_network(sections)

    def total_weight(self):
        return sum(w for _, _, w in self.graph.edges.data('weight'))

    def _build_network(self, sections):
        for sec in sections:
            self.graph.add_node(sec.id)
            for ref_elem in sec.elem.iter(util.prefix_tag('ref')):
                ref_id = ref_elem.attrib.get('href')
                if not ref_id or not util.is_uscode_id(ref_id):
                    continue
                ref_id = util.id_level(ref_id, 5)
                self._update_edge(sec.id, ref_id)

    def _update_edge(self, src, dst, weight=1):
        if (src, dst) not in self.graph.edges:
            self.graph.add_edge(src, dst, weight=0)
        self.graph[src][dst]['weight'] += weight
