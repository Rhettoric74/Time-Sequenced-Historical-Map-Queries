import json
import sys
import os
import time
sys.path.append("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/scripts")
import coordinate_geometry
import copy
class FeatureNode:
    def __init__(self, feature_obj):
        self.geojson = feature_obj
        self.type = feature_obj["type"]
        self.geometry_type = feature_obj["geometry"]["type"]
        self.coordinates = feature_obj["geometry"]["coordinates"]
        self.centroid = coordinate_geometry.get_centroid(self.coordinates)
        self.text = feature_obj["properties"]["text"]
        self.post_ocr = feature_obj["properties"]["postocr_label"]
        self.score = feature_obj["properties"]["score"]
        self.neighbors = []
    def distance(self, other):
        return coordinate_geometry.haversine_distance(self.centroid, other.centroid)
def prims_mst(nodes_list):
    vertices_list = [{"vertex":node, "key":float("inf"), "parent": None} for node in nodes_list]
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
class MapGraph:
    def __init__(self, geojson_file, connecting_function = prims_mst):
        time_loading = time.time()
        with open(geojson_file) as fp:
            json_obj = json.load(fp)
        self.map_id = json_obj["name"]
        self.nodes = []
        for feature_obj in json_obj["features"]:
            self.nodes.append(FeatureNode(feature_obj))
        print("Time loading:", time.time() - time_loading)
        if connecting_function != None:
            time_connecting = time.time()
            connecting_function(self.nodes)
            print("Time connecting:", time.time() - time_connecting)
    def __repr__(self):
        sting_representation = ""
        for node in self.nodes:
            sting_representation += node.post_ocr + "\n"
            for neighbor in node.neighbors:
                sting_representation += "    " + neighbor.post_ocr + "\n"
        return sting_representation

if __name__ == "__main__":
    MapGraph("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/random_hundred_geojson_testr_syn/0018126.geojson", prims_mst)