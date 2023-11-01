from map_graph import MapGraph
import json
import sys
import os
import time
sys.path.append("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis")
import config
from scripts.geo_entity import GeoEntity
import copy
from fuzzywuzzy import fuzz


def multiword_query(place_name, fclasses = None, similarity_threshold = 60):
    entity = GeoEntity(place_name, fclasses)
    num_words = place_name.count(" ") + 1
    matches = []
    for map_file in os.listdir("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/" + config.GEOJSON_FOLDER):
        print(map_file)
        map_graph = MapGraph("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/" + config.GEOJSON_FOLDER + map_file)
        overlapping_nodes = [node for node in map_graph.nodes if entity.within_bounding(node.coordinates)]
        if len(overlapping_nodes) > 0:
            frontier = [overlapping_nodes[0]]
            explored = []
            while frontier != []:
                cur_node = frontier.pop(0)
                for node_sequence in search_from_node(cur_node, num_words):
                    joined_text = " ".join([node.post_ocr for node in node_sequence])
                    print(joined_text)
                    closest_variant = None
                    closest_match = 0
                    for variant in entity.variations:
                        cur_ratio = fuzz.ratio(joined_text, place_name.upper())
                        if cur_ratio >= similarity_threshold and cur_ratio > closest_match:
                            closest_variant = variant
                            closest_match = cur_ratio
                    if closest_variant != None:
                        matches.append({"name_variant":closest_variant, "map_id":map_file, "fuzzy_ratio":cur_ratio})
                        print(matches)
                for neighbor in cur_node.neighbors:
                    if neighbor not in explored and neighbor in overlapping_nodes:
                        frontier.append(neighbor)
    return matches


def search_from_node(node, depth):
    nodes_lists = [[neighbor] for neighbor in node.neighbors]
    for i in range(depth - 1):
        for nodes_list in nodes_lists:
            nodes_lists.remove(nodes_list)
            for neighbor in nodes_list[-1].neighbors:
                if neighbor not in nodes_list:
                    nodes_lists.append(nodes_list + [neighbor])
    return nodes_lists
if __name__ == "__main__":
    multiword_query("New york")
            
        

