from place_node import PlaceNode
import os
import copy
import json
from fuzzywuzzy import fuzz
import numpy as np
class KnowledgeGraph(object):
    def __init__(self):
        self.place_nodes = []
        self.node_hashes = {}
    def read_from_dir(self, dirname):
        for file in os.listdir(dirname):
            #print(file)
            self.place_nodes.append(PlaceNode(dirname + "/" + file))
        self.connect_nodes()
        
    
    def connect_nodes(self):
        """
        Purpose: Use Prim's algorithm to create a minimal spanning tree of the graph, with edge weights
        equal to the distance between the two 
        """
        vertices_list = [{"vertex":node, "key":float("inf"), "parent": None} for node in self.place_nodes]
        all_neighbors = copy.copy(vertices_list)
        vertices_list[0]["key"] = 0
        while vertices_list != []:
            u = min(vertices_list, key = lambda vertex: vertex["key"])
            vertices_list.remove(u)
            for other_vertex in all_neighbors:
                if other_vertex != u:
                    if other_vertex in all_neighbors and other_vertex["vertex"].distance(u["vertex"]) < other_vertex["key"]:
                        other_vertex["parent"] = u
                        other_vertex["key"] = other_vertex["vertex"].distance(u["vertex"])
        for node in all_neighbors:
            if node["parent"] != None:
                if node["parent"]["vertex"] not  in node["vertex"].neighbors:
                    node["vertex"].neighbors.append(node["parent"]["vertex"])
                if node["vertex"] not in node["parent"]["vertex"].neighbors:
                    node["parent"]["vertex"].neighbors.append(node["vertex"])
    
    def date_map(self, map_filename, sufficient_specificity = 10, ratio_threshold = 90):
        """
        Purpose: search nodes of the graph that appear on a map, and date the map based on the intersection of the ranges of 
        all name variants that are depicted.
        Parameters: map_filename, the name of a geojson processed output file for the map to be dated.
        Returns: a tuple (earliest_year, latest_year) giving a range for the date of the map"""
        with open("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/geojson_testr_syn/" + map_filename, "r") as json_file:
            feature_collection = json.load(json_file)
        cur_range = float("inf")
        timespan = (-float("inf"), float("inf"))
        nodes_queue = [self.place_nodes[0]]
        visited_nodes = {}
        num_matches = 0
        while len(nodes_queue) > 0 and cur_range > sufficient_specificity:
            cur_node = nodes_queue.pop(0)
            #print(cur_node.name)
            #print(cur_node)
            #print(timespan)
            found_neighbor = False
            visited_nodes[cur_node] = True
            for feature in feature_collection["features"]:
                post_ocr = str(feature["properties"]["postocr_label"]).upper()
                # use fuzzy string comparison to detect a match with known name variants
                coords = feature["geometry"]["coordinates"]
                # check if the point is within the entity being queried
                if cur_node.within_bounding(coords):
                    # check if features in the neighborhood match a known name
                    closest_variant = None
                    best_score = 0
                    for variant_node in cur_node.name_variant_nodes:
                        fuzzy_ratio = fuzz.ratio(post_ocr, variant_node.name_variant)
                        # check that current word is over our minimum threshold 
                        if fuzzy_ratio > ratio_threshold and (closest_variant == None or fuzzy_ratio > closest_variant.get_score() > best_score):
                            closest_variant = variant_node
                            best_score = closest_variant.get_score()
                    if closest_variant != None:
                        print(closest_variant.name_variant)
                        variant_timespan = closest_variant.get_range()
                        next_timespan = (max(timespan[0], variant_timespan[0]), min(timespan[1], variant_timespan[1]))
                        if next_timespan[1] - next_timespan[0] >= 0:
                            timespan = next_timespan
                            cur_range = timespan[1] - timespan[0]
                        for neighbor in cur_node.neighbors:
                            if neighbor not in visited_nodes:
                                nodes_queue.append(neighbor)
                        found_neighbor = True
                        num_matches += 1
                        break
            # add a different node to the queue if the place was not found
            if not found_neighbor:
                for node in self.place_nodes:
                    if node not in visited_nodes:
                        nodes_queue.append(node)
                        break

        return num_matches, timespan


    def __str__(self):
        output = ""
        for node in self.place_nodes:
            output += str(node.name) + " connected to:\n"
            for neighbor in node.neighbors:
                output += "    " +  str(neighbor.name) + ": " + str(node.distance(neighbor)) + "km away\n"
        return output



            
        
            
if __name__ == "__main__":
    kg = KnowledgeGraph()
    kg.read_from_dir("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/analyzed_features/input_queries")
    print(kg)
    for node in kg.place_nodes:
        for name_variant in node.name_variant_nodes:
            print(name_variant.name_variant, name_variant.get_range(0.5))
    for place_node in kg.place_nodes:
        print(len(place_node.name_variant_nodes))
        place_node.combine_similar_variants()
        print(len(place_node.name_variant_nodes))
    place_file = "C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/analyzed_features/german_cities/Hamburg_dates.json"
    numbers_of_matches = []
    timespan_specificities = []
    with open(place_file) as fp:
        map_collection = json.load(fp)
        for key in map_collection["Hamburg"]:
            for attestation in map_collection["Hamburg"][key]:
                num_matches, timespan = kg.date_map(attestation["map_id"] + ".geojson")
                print(timespan)
                numbers_of_matches.append(num_matches)
                timespan_specificities.append(timespan[1] - timespan[0])
    print("Average Matches found:", np.mean(numbers_of_matches))
    print("STD of matches found:", np.std(numbers_of_matches))
    print("Average timespan Specificity:", np.mean(timespan_specificities))
    print("STD of timespan specificites:", np.std(timespan_specificities))


