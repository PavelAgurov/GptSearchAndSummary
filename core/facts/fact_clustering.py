"""
    Fact clastering
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

from dataclasses import dataclass
from typing import Callable

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

@dataclass
class FactCluster:
    """Cluster of facts"""
    name      : str
    fact_list : list[str]


def fact_k_means(fact_list : list[str], cluster_count : int, encode_call : Callable[..., list[list[float]]]) -> list[FactCluster]:
    """Get fact clusters"""

    embeddings_array = encode_call(fact_list)
    cosine_distances = pairwise_distances(embeddings_array, metric="cosine")

    kmeans = KMeans(n_clusters=cluster_count, n_init="auto")
    kmeans.fit(cosine_distances)
    label = kmeans.labels_

    data_with_labels = np.column_stack((fact_list, label))
    data_with_labels = sorted(data_with_labels, key=lambda t: t[-1], reverse=False)

    grouped_dict = {}

    for item in data_with_labels:
        key = item[1]
        if key in grouped_dict:
            grouped_dict[key].append(item[0])
        else:
            grouped_dict[key] = [item[0]]

    result = list[FactCluster]()
    
    for group in grouped_dict.items():
        name = f'Cluster {group[0]}'
        fact_cluster = FactCluster(name, group[1])
        result.append(fact_cluster)

    return result
