import itertools
import functools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram

import util


def vectorization_distance(section1, section2):
    return util.dict_distance(section1.terms_, section2.terms_)


class CitationSinks:
    def __init__(self, elems, network):
        self.sinks_from = {elem.id: network.sinks_from(elem.id) for elem in elems}

    def distance(self, section1, section2):
        sinks1 = self.sinks_from[section1.id]
        sinks2 = self.sinks_from[section2.id]

        n_shared = len(sinks1 & sinks2)
        n_total = len(sinks1) + len(sinks2) - n_shared
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

        distance = np.arange(model.children_.shape[0])
        n_observations = np.arange(2, model.children_.shape[0] + 2)
        linkage_matrix = np.column_stack([model.children_, distance, n_observations]).astype(float)

        dendrogram(linkage_matrix, labels=self.elem_ids)

    @staticmethod
    def build_distance_matrix(elems, dist_func):
        n_elems = len(elems)
        dist_mat = np.zeros((n_elems, n_elems))

        for (i, elem1), (j, elem2) in itertools.combinations(enumerate(elems), 2):
            dist = dist_func(elem1, elem2)
            dist_mat[i][j] = dist_mat[j][i] = dist

        return dist_mat
