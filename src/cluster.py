import itertools
import functools
import numpy as np
from sklearn.cluster import AgglomerativeClustering

import util


def vectorization_distance(section1, section2):
    return util.dict_distance(section1.terms, section2.terms)


class CitationSinks:
    def __init__(self, sections, network):
        self.sinks_from = {section: network.sinks_from(section.id) for section in sections}

    def distance(self, section1, section2):
        sinks1 = self.sinks_from[section1]
        sinks2 = self.sinks_from[section2]

        n_shared = len(sinks1 & sinks2)
        n_total = len(sinks1) + len(sinks2) - n_shared
        return 1 - n_shared / max(1, n_total)


class Clustering:
    def __init__(self, sections, dist_func):
        self.section_ids = [sec.id for sec in sections]
        self.dist_mat = self.build_distance_matrix(sections, dist_func)

    def get_clusters(self, n_clusters):
        clustering = AgglomerativeClustering(n_clusters=n_clusters,
                                             affinity='precomputed',
                                             linkage='average')
        clustering.fit(self.dist_mat)

        clusters = util.group_by_label(self.section_ids, clustering.labels_)
        return list(clusters.values())

    @staticmethod
    def build_distance_matrix(sections, dist_func):
        n_sections = len(sections)
        dist_mat = np.zeros((n_sections, n_sections))

        for (i, sec1), (j, sec2) in itertools.combinations(enumerate(sections), 2):
            dist = dist_func(sec1, sec2)
            dist_mat[i][j] = dist
            dist_mat[j][i] = dist

        return dist_mat
