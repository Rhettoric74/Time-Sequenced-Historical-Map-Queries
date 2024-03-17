import os
import sys
sys.path.append(os.pardir)
import list_multiword_paths
import multiword_name_extraction
from map_graph import FeatureNode, prims_mst, half_prims_mst, MapGraph
import json
import os
import numpy as np
from nltk.cluster.util import euclidean_distance
from clustering_linkages import cluster_map_nodes, distance_height_ratio_sin_angle_capitalization

class LinkageMethod:
    def connect(self, map_graph):
        if self.weights == None:
            self.connection_function(map_graph.nodes, self.distance_function)
        else:
            self.connection_function(map_graph.nodes, self.weights, self.distance_function)
    def __init__(self, connection_function, distance_function, weights = None):
        self.connection_function = connection_function
        self.distance_function = distance_function
        self.weights = weights 


def compare_linkages(map_filename, depth_limit = 2, linkage_method = LinkageMethod(prims_mst, FeatureNode.distance)):
    ground_truth = multiword_name_extraction.multiword_name_extraction_from_map(map_filename)
    linkages = MapGraph(map_filename)
    linkage_method.connect(linkages)
    linked_phrases = list_multiword_paths.list_all_multiword_paths(linkages, depth_limit)
    correctly_linked_phrases = []
    incorrectly_linked_phrases = []
    for annotated_phrase in ground_truth:
        found = False
        for phrase in linked_phrases:
            joined_phrase = " ".join([node.text for node in phrase])
            if joined_phrase == annotated_phrase:
                found = True
                break
        if not found:
            incorrectly_linked_phrases.append(annotated_phrase)
        else:
            correctly_linked_phrases.append(annotated_phrase)
    results = {"image":map_filename, "results":
                    {
                        "correctly_linked_phrases":correctly_linked_phrases,
                        # "incorrectly_linked_phrases":incorrectly_linked_phrases,
                        "number_correctly_linked":len(correctly_linked_phrases),
                        "number_connections_missed":len(ground_truth) - len(correctly_linked_phrases),
                        "number_incorrectly_linked":len(linked_phrases) - len(correctly_linked_phrases)
                    }
               }
    return results

def get_stats_from_results_file(results_filename):
    with open(results_filename) as f:
        results_dict = json.load(f)
        true_linkages = []
        missed_linkages = []
        false_linkages = []
        for map_result in results_dict["map_results"]:
            # "number_correctly_linked": 3, "number_connections_missed": 125, "number_incorrectly_linked": 401}
            true_linkages.append(map_result["results"]["number_correctly_linked"])
            false_linkages.append(map_result["results"]["number_incorrectly_linked"])
            missed_linkages.append(map_result["results"]["number_connections_missed"])
        recall_per_map = [true_linkages[i] / max(1, (true_linkages[i] + missed_linkages[i])) for i in range(len(true_linkages))]
        print(recall_per_map)
        precision_per_map = [true_linkages[i] / (true_linkages[i] + false_linkages[i]) for i in range(len(true_linkages))]
        print("recall: ", sum(true_linkages)/sum(true_linkages + missed_linkages))
        print("best recall on map", max(recall_per_map), "\nworst recall on map", min(recall_per_map))
        print("best precision on map", max(precision_per_map), "\nworst precision on map", min(precision_per_map))
        print("percentage of true linkages: ", sum(true_linkages) / sum(true_linkages + false_linkages))
    return (np.mean(recall_per_map))

            

if __name__ == "__main__":
    depth_limit = 3
    maps_sampled = ["5797073_h2_w9.png", "8817002_h4_w4.png","0068010_h2_w7.png","0071008_h3_w7.png","7807309_h6_w7.png","7911000_h2_w2.png","7810246_h7_w2.png"]
    random_map_sample = ['0041033_h2_w5.png', '0066014_h2_w2.png', '6756003_h3_w8.png', '6323028_h2_w3.png', '0066046_h2_w3.png', '5802011_h4_w4.png', '0231018_h2_w6.png', '6354084_h5_w5.png', '0071013_h2_w2.png', '0071018_h6_w2.png']
    print(random_map_sample)
    descriptors_to_functions = {
        "distance_height_ratio_sin_angle_penalty": FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty,
        "distance_only":FeatureNode.distance, "height_ratio_only":FeatureNode.height_ratio, "sin_angle_difference_only":FeatureNode.sin_angle_difference, 
        "distance_height_ratio":FeatureNode.distance_height_ratio, "distance_sin_angle_capitalization_penalty" :FeatureNode.distance_sin_angle_capitalization_penalty,
        "distance_height_ratio_sin_angle": FeatureNode.distance_height_ratio_sin_angle, "distance_sin_angle_penalty": FeatureNode.distance_with_sin_angle_penalty, 
    }
    #descriptors_to_functions = {"distance_height_ratio_sin_angle_capitalization":FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty}
    weights_list = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 10, 0], [1, 0, 10], [1, 10, 10]]
    for name, distance_function in descriptors_to_functions.items():
        results_dict = {"connecting_method": "MST", "distance_function":"euclidean_distance", "depth_limit":depth_limit, "map_results":[]}
        print(len(weights_list))
        for map in random_map_sample:
            results_dict["map_results"].append(compare_linkages(map, depth_limit, LinkageMethod(prims_mst, distance_function)))
        with open(os.getcwd().strip("/scripts") + "/mst_results/" + name + "_depth_limit_"  + "_depth_limit_" + str(depth_limit) + ".json", "w") as f:
            json.dump(results_dict, f)
            print("finished", name)
    best_recall = - float("inf")
    best_function = None
    best_weights = None
    for name in descriptors_to_functions.keys():
        print(name)
        recall = get_stats_from_results_file(os.getcwd().strip("/scripts") + "/mst_results/" + name + "_depth_limit_" + str(depth_limit) + ".json")
        if recall > best_recall:
            best_function = name
            best_recall = recall
        print()
    """ for weights in weights_list:
            print(weights)
            recall = get_stats_from_results_file(os.getcwd().strip("/scripts") + "/kmeans_results/" + str(weights[0]) + "-" + str(weights[1]) + "-" + str(weights[2]) + "_depth_limit_" + str(depth_limit) + ".json")
            if recall > best_recall:
                best_recall = recall
                best_weights = weights
            print() """
    print(best_function, best_recall, best_weights)



