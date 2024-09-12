import os
import random
import sys
import pickle
sys.path.append(os.pardir)
import list_multiword_paths
import multiword_name_extraction
from map_graph import FeatureNode, prims_mst, half_prims_mst, MapGraph
import json
import os
import numpy as np
from nltk.cluster.util import euclidean_distance
import multiprocessing

def analyze_linkages_in_phrases_list(map_id, linked_phrases_output_dir = "phrases_v1_19_usgs_nocap_p0.5_scc", data_filepath="icdar24-val-png/annotations.json"):
    with open(linked_phrases_output_dir + "/" + map_id + ".pkl", "rb") as f:
        phrases_list = pickle.load(f)
        print("linked phrases", [phrase for phrase in phrases_list if phrase.count(" ") > 0])
        annotated_phrases = multiword_name_extraction.multiword_name_extraction_from_map(map_id + ".png", data_filepath)
        print("annotated phrases", annotated_phrases)
        correclty_linked_multiword = set(phrases_list).intersection(set(annotated_phrases))
        #recall = len(correclty_linked_multiword) / len(annotated_phrases)
        number_edges_drawn = sum([phrase.count(" ") for phrase in phrases_list])
        number_true_edges_drawn = sum([phrase.count(" ") for phrase in correclty_linked_multiword])
        if number_edges_drawn > 0 and len(annotated_phrases) > 0:
            recall = len(correclty_linked_multiword) / len(annotated_phrases)
            precision = number_true_edges_drawn / number_edges_drawn
            print("precision:", precision)
            print("recall", recall)
        return len(correclty_linked_multiword), len(annotated_phrases), number_true_edges_drawn, number_edges_drawn

def evaluate_mapkurator_phrases(maps_list, linked_phrases_ouptut_dir = "phrases_v1_19_usgs_nocap_p0.5_scc", data_filepath = "img-names-updated_icdar24-test-png-annotations.json"):
    correclty_linked_multiword, annotated_phrases, number_true_edges_drawn, number_edges_drawn = (0, 0, 0, 0)
    for map in maps_list:
        cur_correclty_linked_multiword, cur_annotated_phrases, cur_number_true_edges_drawn, cur_number_edges_drawn = analyze_linkages_in_phrases_list(map, linked_phrases_output_dir=linked_phrases_ouptut_dir, data_filepath=data_filepath)
        correclty_linked_multiword += cur_correclty_linked_multiword
        annotated_phrases += cur_annotated_phrases
        number_true_edges_drawn += cur_number_true_edges_drawn
        number_edges_drawn += cur_number_edges_drawn
    print("overall precision:", number_true_edges_drawn / number_edges_drawn)
    print("overall recall:", correclty_linked_multiword / annotated_phrases)
    return number_true_edges_drawn / number_edges_drawn, correclty_linked_multiword / annotated_phrases

        

if __name__ == "__main__":
    maps_list = [image_path.strip(".png") for image_path in os.listdir("/home/yaoyi/olso9295/linked_historical_maps/word_linking/test_images")]
    print(maps_list)
    evaluate_mapkurator_phrases(maps_list, "test_phrases_v1_19_usgs_nocap_p0.5_wcc", "img-names-updated_icdar24-test-png-annotations.json")