from map_graph import MapGraph, FeatureNode
from multiword_name_extraction import extract_map_data_from_all_annotations
import pandas as pd
import io
import json
import os
import multiword_name_extraction
import random
import multiprocessing as mp


def load_df_from_map_graph(map_graph:MapGraph):
    # define the field names for the map graph
    df = pd.DataFrame(columns=["label1", "label2", "normalized_distance", "height_ratio", "sine_angle_difference", "capitalization_difference", "connected"])
    already_visited_nodes = set()
    cur_idx = 0
    for node in map_graph.nodes:
        already_visited_nodes.add(node)
        for other_node in map_graph.nodes:
            if other_node not in already_visited_nodes:
                connected = 0
                if node in other_node.neighbors or other_node in node.neighbors:
                    connected = 1
                df.loc[cur_idx] = [node.text, other_node.text, node.distance(other_node), node.height_ratio(other_node), node.sin_angle_difference(other_node), node.capitalization_difference(other_node), connected]
                cur_idx += 1
    return df
def load_all_maps_into_df(map_annotations_filepath, filtered_ids_list = None):
    with open(map_annotations_filepath) as f:
        map_annotations = json.load(f)
        map_graphs_list = []
        for annotation in map_annotations:
            #print(annotation["image"])
            if filtered_ids_list == None or annotation["image"] in filtered_ids_list:
                map_graphs_list.append(MapGraph(annotation["image"], "annotations", map_annotations_filepath))
        num_cores = mp.cpu_count()
        with mp.Pool(processes=num_cores) as pool:
            df_list = pool.map(load_df_from_map_graph, map_graphs_list)
            return pd.concat(df_list, ignore_index=True)

if __name__ == "__main__":
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
    print(len(val_enough_multiword_phrases)) """
    test_enough_multiword_phrases = []
    for map_annotation in multiword_name_extraction.AnnotationsSingleton().get_annotations("icdar24-test-png-annotations.json"):
        THRESHOLD = 5
        names_list = multiword_name_extraction.multiword_name_extraction_from_map(map_annotation["image"], data_filepath="icdar24-test-png-annotations.json")
        #print(counter)
        if len(names_list) >= THRESHOLD:
            test_enough_multiword_phrases.append(map_annotation["image"])
    print(len(test_enough_multiword_phrases))
    """ print("computing training data")
    df = load_all_maps_into_df("icdar24-train-png/annotations.json", enough_multiword_phrases)
    print(df)
    df.to_csv("filtered_train_label_pair_attributes.csv", index=False)
    print("computing val data")
    filtered_val_df = load_all_maps_into_df("icdar24-val-png/annotations.json", val_enough_multiword_phrases)
    print(filtered_val_df)
    filtered_val_df.to_csv("filtered_val_label_pair_attributes.csv", index=False)
    print("computing test data") """
    """ unfiltered_test_df = load_all_maps_into_df("icdar24-test-png-annotations.json")
    print(unfiltered_test_df)
    unfiltered_test_df.to_csv("test_label_pair_attributes.csv", index=False) """
    filtered_test_df = load_all_maps_into_df("icdar24-test-png-annotations.json", random.sample(test_enough_multiword_phrases, 100))
    print(filtered_test_df)
    filtered_test_df.to_csv("filtered_test_label_pair_attributes.csv", index=False)



