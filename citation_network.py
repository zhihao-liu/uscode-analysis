import logging
from collections import defaultdict
from uscode import Section, USCode
import util


class CitationNode:
    def __init__(self, section):
        self.section = section
        self.indegree = 0
        self.outedges = defaultdict(int)

    @property
    def outdegree(self):
        return len(self.outedges)


class CitationNetwork:
    def __init__(self, sections):
        self.nodes = {}
        self.n_edges = 0

        self._init_nodes(sections)
        self._build_network()

    @property
    def n_nodes(self):
        return len(self.nodes)

    def _init_nodes(self, sections):
        logging.info("Intializing nodes...")
        for sec in sections:
            sec_id = sec.get_attrib('identifier')
            if not (sec_id and sec_id.startswith('/us/usc')):
                continue
            self.nodes[sec_id] = CitationNode(sec)

    def _build_network(self):
        logging.info("Building network...")
        for node in self.nodes.values():
            for ref_elem in node.section.elem.iter(util.prefix_tag('ref')):
                ref_id = ref_elem.attrib.get('href')
                if not ref_id or not util.is_uscode_id(ref_id):
                    continue

                ref_id = util.id_level(ref_id, 5) # trim the identifier to the section level
                if ref_id in self.nodes:
                    self._add_edge(node, self.nodes[ref_id])

    def total_weight(self):
        return sum(weight for node in self.nodes.values() for weight in node.outedges.values())

    def _add_edge(self, src, dst):
        if dst not in src.outedges:
            self.n_edges += 1
            dst.indegree += 1
        src.outedges[dst] += 1
