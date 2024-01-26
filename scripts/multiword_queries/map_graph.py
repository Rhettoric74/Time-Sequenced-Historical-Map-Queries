import json
import math
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
        # use try except block to catch errors for non-polygon geometries
        self.minimum_bounding_box = coordinate_geometry.convex_hull_min_area_rect(self.coordinates)

        self.centroid = coordinate_geometry.get_centroid(self.coordinates)
        self.text = str(feature_obj["properties"]["text"])
        self.capitalization = self.text.isupper()
        self.img_coordinates = feature_obj["properties"]["img_coordinates"]
        self.post_ocr = feature_obj["properties"]["postocr_label"]
        self.score = feature_obj["properties"]["score"]
        self.neighbors = []
    def distance(self, other):
        """
        gives the geographic distance (in meters) between the centroids of the polygons, based on the haversine formula 
        """
        return coordinate_geometry.haversine_distance(self.centroid, other.centroid)
    def height_difference(self, other):
        return math.fabs(self.minimum_bounding_box[1][1] - other.minimum_bounding_box[1][1])
    def sin_angle_difference(self, other):
        return math.sin(math.radians(math.fabs(self.minimum_bounding_box[2] - other.minimum_bounding_box[2])))
    def distance_with_sin_angle_penalty(self, other):
        """
        Returns the distance between the centroids of the two labels, multiplied by 1 plus the sine of their angle difference.
        This is done to discourage matching nearby labels that have very different angled text."""
        return self.distance(other) * (1 + self.sin_angle_difference(other))
    def distance_sin_angle_capitalization_penalty(self, other):
        """
        Returns the distance between the centroids of the two labels, multiplied by 1 plus the sine of their angle difference, 
        and multiplied by2 if the two labels differ in capitalization 
        (i.e. one is all caps and the other contains at least one lower case letter)"""
        coeff = 1
        if self.capitalization != other.capitalization:
            coeff = 2
        return coeff * self.distance(other) * (1 + self.sin_angle_difference(other))
    
def prims_mst(nodes_list, distance_func = FeatureNode.height_difference):
    """
    Create a minimum spanning tree of a graph of nodes based on the distance function that is passed
    Parameters: nodes list: a list of Feature Nodes, """
    vertices_list = [{"vertex":node, "key":float("inf"), "parent": None} for node in nodes_list]
    all_neighbors = copy.copy(vertices_list)
    vertices_list[0]["key"] = 0
    while vertices_list != []:
        u = min(vertices_list, key = lambda vertex: vertex["key"])
        vertices_list.remove(u)
        for other_vertex in all_neighbors:
            if other_vertex != u:
                d = distance_func(other_vertex["vertex"], u["vertex"]) 
                if other_vertex in vertices_list and d < other_vertex["key"]:
                    other_vertex["parent"] = u
                    other_vertex["key"] = distance_func(other_vertex["vertex"], u["vertex"])
    for node in all_neighbors:
        if node["parent"] != None:
            if node["parent"]["vertex"] not in node["vertex"].neighbors:
                node["vertex"].neighbors.append(node["parent"]["vertex"])
            if node["vertex"] not in node["parent"]["vertex"].neighbors:
                node["parent"]["vertex"].neighbors.append(node["vertex"])
def spanning_tree_k_neighbors(nodes_list, k = 10):
    vertices_list = [{"index": i,"vertex":node, "key":float("inf"), "parent": None} for i, node in enumerate(nodes_list)]
    all_neighbors = copy.copy(vertices_list)
    vertices_list[0]["key"] = 0
    while vertices_list != []:
        u = min(vertices_list, key = lambda vertex: vertex["key"])
        vertices_list.remove(u)
        index_range = (max(u["index"] - k // 2, 0), min(u["index"] + k // 2, len(all_neighbors)))
        for other_vertex in all_neighbors[index_range[0]:index_range[1]]:
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
    def __init__(self, geojson_file, connecting_function = None):
        # time_loading = time.time()
        with open(geojson_file) as fp:
            json_obj = json.load(fp)
        self.map_id = json_obj["name"]
        self.nodes = []
        for feature_obj in json_obj["features"]:
            self.nodes.append(FeatureNode(feature_obj))
        #print("Time loading:", time.time() - time_loading)
        if connecting_function != None:
            time_connecting = time.time()
            connecting_function(self.nodes)
            #print("Time connecting:", time.time() - time_connecting)
    def __repr__(self):
        sting_representation = ""
        for node in self.nodes:
            sting_representation += node.post_ocr + "\n"
            for neighbor in node.neighbors:
                sting_representation += "    " + neighbor.post_ocr + "\n"
        return sting_representation

if __name__ == "__main__":
    print(MapGraph("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/geojson_testr_syn/11320000.geojson", prims_mst))