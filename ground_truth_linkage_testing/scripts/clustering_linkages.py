from map_graph import *
from nltk.cluster.kmeans import KMeansClusterer
import numpy as np
from nltk.cluster.util import euclidean_distance

def distance_height_ratio_sin_angle_capitalization(u, v):
    # TODO: figure out how to make this metric & fast to calculate
    diff = u[:2] - v[:2]
    return math.sqrt(np.dot(diff, diff)) * (min(u[2]/v[2], v[2]/u[2])) * (1 + math.fabs(u[3] - v[3])) * (1 + math.sin(math.radians(math.fabs(u[4] - v[4]))))
def cluster_map_nodes(nodes_list, weights = [1, 1, 1], distance_func = euclidean_distance):
    # cluster into 
    num_clusters = len(nodes_list) // 5
    data = MapGraph.to_matrix(nodes_list, weights)
    kclusterer = KMeansClusterer(num_clusters, distance = distance_func, repeats=25, avoid_empty_clusters=True)
    assigned_clusters = kclusterer.cluster(data,assign_clusters=True)
    node_clusters = [[] for i in range(num_clusters)]
    for i in range(len(assigned_clusters)):
        node_clusters[assigned_clusters[i]].append(nodes_list[i])
    cluster_sizes = [len(node_cluster) for node_cluster in node_clusters]
    print("largest cluster", max(cluster_sizes), "average cluster size:", np.median(cluster_sizes))
    for cluster_subgraph in node_clusters:
        draw_complete_graph(cluster_subgraph)

if __name__ == "__main__":
    mg = MapGraph("5797073_h2_w9.png")
    cluster_map_nodes(mg.nodes)
