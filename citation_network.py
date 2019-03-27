import networkx as nx


class CitationNetwork:
    def __init__(self, sections):
        self.graph = self._build_graph(sections)

    def _build_graph(self, sections):
        graph = nx.DiGraph()

        for sec in sections:
            graph.add_node(sec.id)
            for ref_id, ref_count in sec.refs.items():
                graph.add_edge(sec.id, ref_id, weight=ref_count)

        return graph
