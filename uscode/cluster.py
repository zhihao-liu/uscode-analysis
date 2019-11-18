import itertools
import functools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

import util


def iou_distance(i, u):
    return 1 - i / max(1, u)


def vectorization_distance(elem1, elem2):
    return util.dict_distance(elem1.terms, elem2.terms)


def citation_distance(elem1, elem2):
    n_inter = sum((elem1.refs & elem2.refs).values())
    n_union = sum((elem1.refs | elem2.refs).values())
    return iou_distance(n_inter, n_union)


def unweighted_citation_distance(elem1, elem2):
    n_inter = len(elem1.refs.keys() & elem2.refs.keys())
    n_union = len(elem1.refs.keys() | elem2.refs.keys())
    return iou_distance(n_inter, n_union)


class CitationSinks:
    def __init__(self, elems, network):
        self.sinks_from = {elem.id: network.sinks_from(elem.id) for elem in elems}

    def distance(self, elem1, elem2):
        sinks1 = self.sinks_from[elem1.id]
        sinks2 = self.sinks_from[elem2.id]

        n_inter = len(sinks1 & sinks2)
        n_union = len(sinks1 | sinks2)
        return iou_distance(n_inter, n_union)


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
