from map_graph import MapGraph, FeatureNode, prims_mst, half_prims_mst
import json
import sys
import os
import time
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
# Add the grandparent directory to the Python path
sys.path.append(grandparent_dir)
import config
from scripts.coordinate_geometry import extract_bounds
from scripts.geo_entity import GeoEntity
from fuzzywuzzy import fuzz
import random
from scripts.extract_year import extract_years
from scripts.match_countries_to_map_ids import countries_to_ids_dict
import multiprocessing as mp

class LinkageMethod:
    def connect(self, nodes_list):
        self.connection_function(nodes_list, self.distance_function)
    def __init__(self, connection_function, distance_function, weights = None):
        self.connection_function = connection_function
        self.weights = weights
        if weights != None:
            self.distance_function = distance_function(weights)
        self.distance_function = distance_function
        

def multiword_query(place_name, fclasses = None, similarity_threshold = 85, linkage_method = LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction([1, 1, 1]))):
    entity = GeoEntity(place_name, fclasses)
    matches = {}
    i = 0
    relevant_maps = set()
    try:
        if isinstance(entity.country, list):
            print(entity.country)
            for country in entity.country:  
                relevant_maps = relevant_maps.union(countries_to_ids_dict[country])
        else:
            relevant_maps = set(countries_to_ids_dict[entity.country])
    except:
        relevant_maps = relevant_maps.union(*countries_to_ids_dict.values()) 
    # cap the relevant maps to search at 10000 if there are more
    if len(list(relevant_maps)) > 10000:
        relevant_maps = random.sample(list(relevant_maps), 10000)
    for map_file in relevant_maps:
        if (i % 100 == 0):
            print(str(i) + " geojson files searched")
        i += 1
        #print(map_file)
        if os.path.isfile(config.GEOJSON_FOLDER + map_file + ".geojson"):
            map_graph = MapGraph(config.GEOJSON_FOLDER + map_file + ".geojson")
        else:
            print(config.GEOJSON_FOLDER + map_file + ".geojson")
            continue
        overlapping_nodes = [node for node in map_graph.nodes if entity.within_bounding(node.coordinates)]
        if len(overlapping_nodes) > 0 and len(overlapping_nodes) < 500:
            linkage_method.connect(overlapping_nodes)
            frontier = [overlapping_nodes[0]]
            explored = []
            closest_variant = None
            closest_node_sequence = None
            closest_match = 0
            iterations = 0
            while frontier != []:
                iterations += 1
                if iterations % 100 == 0:
                    print(iterations, "iterations in", map_file)
                cur_node = frontier.pop(0)
                explored.append(cur_node)
                for variant in entity.variations:
                    num_words = variant.count(" ")
                    node_sequences = search_from_node(cur_node, num_words)
                    #print(node_sequences)
                    for node_sequence in node_sequences:
                        joined_text = " ".join([node.post_ocr for node in node_sequence])
                        cur_ratio = fuzz.ratio(joined_text.upper(), variant.upper())
                        if cur_ratio > 60:
                            print(joined_text, ":", variant)
                        if cur_ratio >= similarity_threshold and cur_ratio > closest_match:
                            closest_variant = variant
                            closest_match = cur_ratio
                            print(joined_text)
                            closest_node_sequence = node_sequence
                for neighbor in cur_node.neighbors:
                    if neighbor not in explored and neighbor in overlapping_nodes:
                        frontier.append(neighbor)
            if closest_variant != None:
                print(closest_variant)
                all_points = closest_node_sequence[0].coordinates
                img_coordinates = []
                for node in closest_node_sequence:
                    img_coordinates += node.img_coordinates
                print(img_coordinates)
                if closest_variant not in matches:
                    matches[closest_variant] = [{"map_id":map_file, "fuzzy_ratio":closest_match, "year": None, "overlap_confidence": entity.overlap_confidence(all_points), "img_coordinates":img_coordinates}]
                else:
                    matches[closest_variant].append({"map_id":map_file, "fuzzy_ratio":closest_match, "year": None, "overlap_confidence": entity.overlap_confidence(all_points), "img_coordinates":[img_coordinates]})
                print(entity.largest_bounding)
                entity.update_bounds(all_points)
                print(all_points)
                print(entity.largest_bounding)
                    #print(matches)
    
    matches["largest_bounding_box"] = entity.largest_bounding

    return matches
def dated_multiword_query(feature_name, fclasses = None):
    """
    Purpose: wrapper around feature_query which matches the resulting maps with their years
    Parameters: See feature_query
    Returns: Dictionary of name variants, each mapped to a list of attestation dictionaries."""

    feature_results = multiword_query(feature_name, fclasses)
    for variant in feature_results.keys():
        if variant != "largest_bounding_box":
            extract_years(feature_results[variant])
    return feature_results


def search_from_node(node, depth, path = []):
    """
    Purpose: generate possible paths of length k from current node
    Parameters: node, map graph node, depth, the length of the target paths, path, the path that has been built so far.
    Returns: a nested list, where each list represents a path of MapGraph nodes"""
    path = path + [node]
    depth -= node.post_ocr.count(" ")
    if depth == 0:
        return [path]
    if depth < 0:
        return []
    paths = []
    for neighbor in node.neighbors:
        if neighbor not in path:
            new_paths = search_from_node(neighbor, depth - 1, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths
def conduct_query_and_write_to_file(query, fclasses,  folder_name):
    try:
        query_results = {query:dated_multiword_query(query, fclasses=fclasses)}
        query_results["geojson"] = GeoEntity(query, fclasses).geojson
        with open("analyzed_features/input_queries/" + query + "_dates.json", "w", encoding="utf-8") as fw:
            json.dump(query_results, fw)
        with open("analyzed_features/" + folder_name + "/" + query + "_dates.json", "w", encoding="utf-8") as fw:
            json.dump(query_results, fw)
    except Exception as e:
        print(e)
if __name__ == "__main__":
    queries = []
    with open("scripts/multiword_queries/lakes_list.txt", "r") as f:
        count = 0
        for line in f:
            queries.append((line.strip("\n"), ["h"], "multiword_lakes"))
            count += 1
            if count >= 25:
                break
    print(len(queries))
    with open("scripts/multiword_queries/multiword_osm_countries_list.txt", "r") as f:
        for line in f:
            queries.append((line.strip("\n"), ["a", "p"], "multiword_countries"))
    print(queries)
    """ with open("scripts/multiword_queries/15_most_populous_multiword_name_cities.txt", encoding="utf-8") as f:
        queries = f.readlines()
        queries = [query.strip("\n") for query in queries] """
    print(queries)
    pool = mp.Pool(mp.cpu_count())  # Uses all available CPU cores
    results = pool.starmap(conduct_query_and_write_to_file, queries)

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()
    
        

