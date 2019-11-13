import itertools
import functools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

import util


def vectorization_distance(section1, section2):
    return util.dict_distance(section1.terms_, section2.terms_)


def citation_distance(section1, section2, weighted=True):
    cites1, cites2 = section1.refs_, section2.refs_
    if not weighted:
        cites1, cites2 = cites1.keys(), cites2.keys()

    n_shared = len(cites1 & cites2)
    n_total = len(cites1 | cites2)
    return 1 - n_shared / max(1, n_total)


class CitationSinks:
    def __init__(self, elems, network):
        self.sinks_from = {elem.id: network.sinks_from(elem.id) for elem in elems}

    def distance(self, section1, section2):
        sinks1 = self.sinks_from[section1.id]
        sinks2 = self.sinks_from[section2.id]

        n_shared = len(sinks1 & sinks2)
        n_total = len(sinks1 | sinks2)
        return 1 - n_shared / max(1, n_total)


class Clustering:
    def __init__(self, elems, dist_func):
        self.elem_ids = [elem.id for elem in elems]
        self.dist_mat = self.build_distance_matrix(elems, dist_func)

    def get_clusters(self, n_clusters):
        model = AgglomerativeClustering(n_clusters=n_clusters,
                                        affinity='precomputed',
                                        linkage='average')
        model.fit(self.dist_mat)
        clusters = util.group_by_label(self.elem_ids, model.labels_)
        return list(clusters.values())

    def plot_dendrogram(self):
        model = AgglomerativeClustering(compute_full_tree=True,
                                        affinity='precomputed',
                                        linkage='average')
        model.fit(self.dist_mat)

        index_pairs = itertools.combinations(range(len(self.elem_ids)), 2)
        flat_dist = np.array([self.dist_mat[i][j] for i, j in index_pairs])
        linkage_matrix = linkage(flat_dist, 'average')
        dendrogram(linkage_matrix, labels=self.elem_ids)

    @staticmethod
    def build_distance_matrix(elems, dist_func):
        n_elems = len(elems)
        dist_mat = np.zeros((n_elems, n_elems))

        for (i, elem1), (j, elem2) in itertools.combinations(enumerate(elems), 2):
            dist = dist_func(elem1, elem2)
            dist_mat[i][j] = dist_mat[j][i] = dist

        return dist_mat
