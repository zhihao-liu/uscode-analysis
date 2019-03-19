import logging
from uscode import Section, USCode, prefix_tag
from collections import defaultdict


class CitationNode:
    def __init__(self, section):
        self.section = section
        self.indegree = 0
        self.outedges = defaultdict(int)


class CitationNetwork:
    def __init__(self, usc):
        self.nodes = {}
        self.n_edges = 0

        self.init_nodes(usc)
        self.build_network()

    def init_nodes(self, usc):
        logging.info('Intializing nodes...')
        for sec in usc.get_all_sections():
            key = sec.get_attrib('identifier')
            if not key:
                continue
            self.nodes[key] = CitationNode(sec)

    def build_network(self):
        logging.info('Building network...')
        for node in self.nodes.values():
            for ref in node.section.elem.iter(prefix_tag('ref')):
                ref_key = ref.attrib.get('href')
                if ref_key in self.nodes:
                    self.add_edge(node, self.nodes[ref_key])

    def add_edge(self, src, dst):
        if dst not in src.outedges:
            self.n_edges += 1
            dst.indegree += 1
        src.outedges[dst] += 1
