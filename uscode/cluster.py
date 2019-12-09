import itertools
import functools
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from sklearn.metrics import fowlkes_mallows_score

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
    def __init__(self, elems, dist_func, method='average'):
        self.elem_ids = [elem.id for elem in elems]
        dist = self.condensed_distance_matrix(elems, dist_func)
        self.linkage_matrix = hierarchy.linkage(dist, method)

    @property
    def n_samples(self):
        return len(self.elem_ids)

    def get_labels(self, n_clusters):
        tree_cut = hierarchy.cut_tree(self.linkage_matrix, n_clusters=n_clusters)
        return tree_cut.reshape(-1)

    def get_clusters(self, n_clusters):
        clusters = [[] for _ in range(n_clusters)]
        labels = self.get_labels(n_clusters)
        for elem_id, label in zip(self.elem_ids, labels):
            labels[label].append(elem_id)
        return clusters

    def plot_dendrogram(self):
        hierarchy.dendrogram(self.linkage_matrix, labels=self.elem_ids)

    @staticmethod
    def condensed_distance_matrix(elems, dist_func):
        elem_pairs = itertools.combinations(elems, 2)
        return np.array([dist_func(a, b) for a, b in elem_pairs])


def single_fm_index(clustering1, clustering2, n_clusters):
    labels1 = clustering1.get_labels(n_clusters)
    labels2 = clustering2.get_labels(n_clusters)
    return fowlkes_mallows_score(labels1, labels2)


def all_fm_indices(clustering1, clustering2):
    if clustering1.n_samples != clustering2.n_samples:
        raise ValueError("Compared clusterings must have the same number of samples")
    return [single_fm_index(clustering1, clustering2, n) for n in range(2, clustering1.n_samples)]


def fm_index(clustering1, clustering2, n_clusters=-1):
    if n_clusters == -1:
        return all_fm_indices(clustering1, clustering2)
    else:
        return single_fm_index(clustering1, clustering2, n_clusters)