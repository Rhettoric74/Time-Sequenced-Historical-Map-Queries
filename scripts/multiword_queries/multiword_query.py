from map_graph import MapGraph, FeatureNode, prims_mst, half_prims_mst
import json
import sys
import os
import time
sys.path.append("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis")
import config
from scripts.geo_entity import GeoEntity
from scripts.coordinate_geometry import extract_bounds
from fuzzywuzzy import fuzz
import random
from scripts.extract_year import extract_years
from scripts.match_countries_to_map_ids import countries_to_ids_dict


def multiword_query(place_name, fclasses = None, similarity_threshold = 85, connecting_function = prims_mst):
    entity = GeoEntity(place_name, fclasses)
    matches = {}
    i = 0
    relevant_maps = set()
    if isinstance(entity.country, list):
        print(entity.country)
        for country in entity.country:
            relevant_maps = relevant_maps.union(countries_to_ids_dict[country])
    else:
        relevant_maps = set(countries_to_ids_dict[entity.country])
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
            connecting_function(overlapping_nodes, FeatureNode.distance_sin_angle_capitalization_penalty)
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
                all_points = []
                for node in closest_node_sequence:
                    all_points += node.coordinates
                if closest_variant not in matches:
                    matches[closest_variant] = [{"map_id":map_file, "fuzzy_ratio":closest_match, "year": None, "overlap_confidence": entity.overlap_confidence(all_points)}]
                else:
                    matches[closest_variant].append({"map_id":map_file, "fuzzy_ratio":closest_match, "year": None, "overlap_confidence": entity.overlap_confidence(all_points)})
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
if __name__ == "__main__":
    queries = ["Cape Town", "Corpus Christi", "Salt Lake City", "New Delhi", "New South Wales"]
    print(os.path.isdir("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/ground_truth_linkage_testing/mst_results/mst_distance_height_ratio_sin_angle_capitalization"))
    for query in queries:
        try:
            print(query)
            query_results = {query:dated_multiword_query(query)}
            query_results["geojson"] = GeoEntity(query).geojson
            with open("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/analyzed_features/input_queries/" + query + "_dates.json", "w", encoding="utf-8") as fw:
                json.dump(query_results, fw)
            with open("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/scripts/multiword_queries/multiword_query_results/mst_distance_height_ratio_sin_angle_capitalization/" + query + "_dates.json", "w", encoding="utf-8") as fw:
                json.dump(query_results, fw)
        except Exception as e:
            print(e)
            continue
        

