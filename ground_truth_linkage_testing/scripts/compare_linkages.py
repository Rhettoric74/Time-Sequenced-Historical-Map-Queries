import os
import random
import sys
sys.path.append(os.pardir)
import list_multiword_paths
import multiword_name_extraction
from map_graph import FeatureNode, prims_mst, half_prims_mst, distance_threshold_graph, MapGraph
import json
import os
import numpy as np
from nltk.cluster.util import euclidean_distance
import multiprocessing
from clustering_linkages import cluster_map_nodes, distance_height_ratio_sin_angle_capitalization
from cross_validation_experiment import load_folds_from_folder

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


def compare_linkages(map_filename, annotations_filepath = "icdar24-train-png/annotations.json", linkage_method = LinkageMethod(prims_mst, FeatureNode.distance)):
    ground_truth = FeatureNode.get_ground_truth_linkages(map_filename, annotations_filepath)
    linkages = MapGraph(map_filename, annotations_filepath=annotations_filepath)
    linkage_method.connect(linkages)
    correctly_linked_phrases = []
    incorrectly_linked_phrases = []
    single_word_phrases = []
    number_correct_edges = 0
    for annotated_phrase in ground_truth:
        if len(annotated_phrase) > 1:
            found = list_multiword_paths.search_node_sequence_in_graph(linkages.nodes, annotated_phrase)
            if not found:
                incorrectly_linked_phrases.append(list_multiword_paths.express_node_sequence_as_phrase(annotated_phrase))
            else:
                correctly_linked_phrases.append(list_multiword_paths.express_node_sequence_as_phrase(annotated_phrase))
                number_correct_edges += len(annotated_phrase) - 1
        else:
            single_word_phrases.append(annotated_phrase)
    results = {"image":map_filename, "results":
                    {
                        "correctly_linked_phrases": correctly_linked_phrases,
                        "incorrectly_linked_phrases": incorrectly_linked_phrases,
                        "number_correctly_linked": len(correctly_linked_phrases),
                        "number_connections_missed": len(ground_truth) - len(correctly_linked_phrases) - len(single_word_phrases),
                        "total_number_edges": linkages.count_edges(),
                        "number_correct_edges": number_correct_edges

                    }
               }
    return results
def map_list_compare_linkages(map_list, function_name, annotations_filepath = "icdar24-train-png/annotations.json", linkage_method = LinkageMethod(prims_mst, FeatureNode.distance), output_filepath = None):
    results_dict = {"connecting_method": "MST", "distance_function":function_name, "map_results":[]}
    for map_id in map_list:
        results_dict["map_results"].append(compare_linkages(map_id, annotations_filepath, linkage_method))
    if output_filepath != None:
        with open(output_filepath, "w") as f:
            json.dump(results_dict, f)
    print("finished", function_name)
    return results_dict
    

def get_stats_from_results_file(results_filename, annotations_filepath = "icdar24-train-png/annotations.json"):
    with open(results_filename) as f:
        results_dict = json.load(f)
        true_linkages = []
        missed_linkages = []
        false_linkages = []
        sum_correct_edge_count = 0
        sum_edge_count = 0
        for map_result in results_dict["map_results"]:
            # "number_correctly_linked": 3, "number_connections_missed": 125, "number_incorrectly_linked": 401}
            #true_linkages.append(map_result["results"]["number_correctly_linked"])
            num_correctly_linked = 0
            correct_edge_count = 0
            for phrase in map_result["results"]["correctly_linked_phrases"]:
                # filter out phrases that are single words
                # from the correctly linked results
                # as single word phrases would always be correctly linked as they don't need
                # to be linked
                if phrase.count(" ") > 0:
                    num_correctly_linked += 1
                    if "number_correct_edges" not in map_result["results"]:
                        correct_edge_count += phrase.count(" ")
            if "number_correct_edges" in map_result["results"]:
                correct_edge_count = map_result["results"]["number_correct_edges"]
            if "total_number_edges" in map_result["results"]:
                sum_edge_count += map_result["results"]["total_number_edges"]
            else:
                sum_edge_count += len(multiword_name_extraction.list_all_word_labels(multiword_name_extraction.extract_map_data_from_all_annotations(map_result["image"], annotations_filepath))) - 1  
            sum_correct_edge_count += correct_edge_count
            true_linkages.append(num_correctly_linked)
            #false_linkages.append(map_result["results"]["number_incorrectly_linked"])
            missed_linkages.append(map_result["results"]["number_connections_missed"])
        recall_per_map = [true_linkages[i] / max(1, (true_linkages[i] + missed_linkages[i])) for i in range(len(true_linkages))]
        print(recall_per_map)
        #precision_per_map = [true_linkages[i] / (true_linkages[i] + false_linkages[i]) for i in range(len(true_linkages))]
        print("recall: ", sum(true_linkages)/sum(true_linkages + missed_linkages))
        print("best recall on map", max(recall_per_map), "\nworst recall on map", min(recall_per_map))
        #print("best precision on map", max(precision_per_map), "\nworst precision on map", min(precision_per_map))
        print("percentage of true linkages: ", sum_correct_edge_count / sum_edge_count)
    return (np.mean(recall_per_map))

            

if __name__ == "__main__":
    #difficult_maps_sample = ["5797073_h2_w9.png", "8817002_h4_w4.png","0068010_h2_w7.png","0071008_h3_w7.png","7807309_h6_w7.png","7911000_h2_w2.png","7810246_h7_w2.png"]
    #maps_sampled = ["5797073_h2_w9.png", "8817002_h4_w4.png","0068010_h2_w7.png","0071008_h3_w7.png","7807309_h6_w7.png","7911000_h2_w2.png","7810246_h7_w2.png"]
    #random_map_sample = ['0041033_h2_w5.png', '0066014_h2_w2.png', '6756003_h3_w8.png', '6323028_h2_w3.png', '0066046_h2_w3.png', '5802011_h4_w4.png', '0231018_h2_w6.png', '6354084_h5_w5.png', '0071013_h2_w2.png', '0071018_h6_w2.png']
    """ enough_multiword_phrases = []
    counter = 0
    for file in os.listdir("icdar24-train-png/train_images"):
        THRESHOLD = 5
        names_list = multiword_name_extraction.multiword_name_extraction_from_map(file)
        counter += 1
        #print(counter)
        if len(names_list) >= THRESHOLD:
            enough_multiword_phrases.append(file)
    print(len(enough_multiword_phrases))
    val_enough_multiword_phrases = []
    for file in os.listdir("icdar24-val-png/val_images"):
        THRESHOLD = 5
        names_list = multiword_name_extraction.multiword_name_extraction_from_map(file, data_filepath="icdar24-val-png/annotations.json")
        counter += 1
        #print(counter)
        if len(names_list) >= THRESHOLD:
            val_enough_multiword_phrases.append(file)
    print(len(val_enough_multiword_phrases))
    #print(random_map_sample)
    #descriptors_to_functions = {"distance_height_ratio_sin_angle_capitalization":FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty}
    weights = [1.76, 0.88, 0.88]
    name = "train_weights_1.76_0.88_0.88"
    output_file_name = "weighted_mst_results/" + name + ".json"
    linkage_method =  LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction(weights))
    train_results = map_list_compare_linkages(enough_multiword_phrases, name, "icdar24-train-png/annotations.json", linkage_method, output_file_name)
    val_name = "val_weights_1.76_0.88_0.88"
    val_output_file_name = "weighted_mst_results/" + val_name + ".json"
    train_results = map_list_compare_linkages(val_enough_multiword_phrases, val_name, "icdar24-val-png/annotations.json", linkage_method, val_output_file_name)
     """
    """ weights_list = [[0.5 * i, 0.25 * j, 0.25 * k] for i in range(5) for j in range(5) for k in range(5)]
    weights_strings = ["weights_" + format(weights[0], ".2f") + "_" + format(weights[1], ".2f") + "_" + format(weights[2], ".2f") for weights in weights_list]
    function_inputs_list = []
    for i in range(len(weights_list)):
        weights = weights_list[i]
        name = weights_strings[i]
        linkage_method = LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction(weights))
        output_file_name = "weighted_mst_results/" + name + ".json"
        function_inputs_list.append((enough_multiword_phrases, name, "icdar24-train-png/annotations.json", linkage_method, output_file_name))
    print(function_inputs_list[0])
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_cores)
    # Use starmap to apply the function with multiple arguments
    results = pool.starmap(map_list_compare_linkages, function_inputs_list)
    pool.close()
    pool.join()
    best_recall = - float("inf")
    best_function = None
    best_weights = None
    weights_and_recalls = "a,b,c,recall\n"
    for i, name in enumerate(weights_strings):
        recall = get_stats_from_results_file("weighted_mst_results/" + name + ".json")
        if recall > best_recall:
            best_function = name
            best_recall = recall
        weights_and_recalls += str(weights_list[i][0]) + "," + str(weights_list[i][1]) + "," + str(weights_list[i][2]) + "," + str(recall) + "\n"
    #print(best_function, best_recall)
    #print(weights_and_recalls)
    with open("recall_data.csv", "w") as f:
        f.write(weights_and_recalls)
    """
    """ weights_list = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [1, 1, 1]]
    for weights in weights_list:
        name = "test_weights_" + "_".join([str(weight) for weight in weights])
        print(name)
        output_file_name = "weighted_mst_results/" + name + ".json"
        linkage_method =  LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction(weights))
        test_maps = []
        with open("icdar24-test-png-annotations.json", "r") as f:
            for map_annotation in json.load(f):
                test_maps.append(map_annotation["image"])
        print(len(test_maps))
        train_results = map_list_compare_linkages(test_maps, name, "icdar24-test-png-annotations.json", linkage_method, output_file_name)
        get_stats_from_results_file(output_file_name, "icdar24-test-png-annotations.json") """ 
    test_maps = []
    with open("icdar24-test-png-annotations.json", "r") as f:
        for map_annotation in json.load(f):
            test_maps.append(map_annotation["image"])
    print(len(test_maps))
    linkage_method = LinkageMethod(prims_mst, FeatureNode.MahalanobisMetric())
    name = "test_mahalanobis_metric"
    output_file_name = "baseline_results/" + name + ".json"
    map_list_compare_linkages(test_maps, name, "icdar24-test-png-annotations.json", linkage_method, output_file_name)
    get_stats_from_results_file(output_file_name, "icdar24-test-png-annotations.json")
    """recall:  0.8245259855408539
    best recall on map 1.0 
    worst recall on map 0.16666666666666666
    percentage of true linkages:  0.2970404752772842
    """