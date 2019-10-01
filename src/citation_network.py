import networkx as nx


class CitationNetwork(nx.DiGraph):
    def __init__(self, uscode):
        super().__init__()

        for sec in uscode.iter_sections():
            self.add_node(sec.id)
            for ref_id, ref_count in sec.refs.items():
                self.add_edge(sec.id, ref_id, weight=ref_count)

    def sinks_from(self, node):
        citations = nx.descendants(self, node)
        return {c for c in citations if self.out_degree(c) == 0}
