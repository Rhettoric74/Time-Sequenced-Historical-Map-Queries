import json
import math
import sys
import os
import numpy as np
import time
sys.path.append("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/scripts")
sys.path.append(os.path.dirname("config.py"))
import config
import coordinate_geometry
import copy
class FeatureNode:
    def __init__(self, feature_obj):
        self.geojson = feature_obj
        self.type = feature_obj["type"]
        self.geometry_type = None
        if feature_obj["geometry"]:
            self.geometry_type = feature_obj["geometry"]["type"]
        self.coordinates = feature_obj["geometry"]["coordinates"]
        # transform the coordinates to WGS 84 if needed
        if config.COORD_SYSTEM != "EPSG:4326":
            self.coordinates = coordinate_geometry.transform_coords_list(self.coordinates)
        self.centroid = coordinate_geometry.get_centroid(self.coordinates)
        self.text = str(feature_obj["properties"]["text"])
        self.capitalization = self.text.isupper()
        self.img_coordinates = feature_obj["properties"]["img_coordinates"]
        if config.COORD_SYSTEM != "EPSG:4326":
            self.img_coordinates = coordinate_geometry.convert_image_coords_to_indices(self.img_coordinates)
        self.minimum_bounding_box = coordinate_geometry.convex_hull_min_area_rect(self.img_coordinates)
        self.post_ocr = feature_obj["properties"]["postocr_label"]
        self.score = feature_obj["properties"]["score"]
        self.neighbors = []
        self.num_letters = len([ch for ch in self.text if ch.isalpha()])
    def get_height(self):
        """
        Gives height dimension of the label's bounding box. If the label is multiple characters long, it is assumed that
        whichever dimension of the bounding box is smaller should be the height dimension.
        Returns: a numerical value representing the height of the feature's minimum bounding box
        """
        if self.num_letters > 1:
            return min(self.minimum_bounding_box[1][0], self.minimum_bounding_box[1][1])
        else:
            return self.minimum_bounding_box[1][1]
    def distance(self, other):
        """
        gives the geographic distance (in meters) between the two polygons, based on the haversine formula distance
        computed for pairs of coordinates on the medians of each side of their minimum bounding boxes
        """
        # get the medians of the four edges of each bounding box
        medians = [[], []]
        rectangles = [self.minimum_bounding_box, other.minimum_bounding_box]
        for i in range(len(rectangles)): 
            # Extract the rectangle properties
            center, size, angle = rectangles[i]
            cx, cy = center
            width, height = size

            # Calculate the medians with rotation consideration
            rotation_rad = np.radians(angle)  # Convert rotation angle to radians

            # Calculate the rotated medians
            medians[i].append([
                cx - 0.5 * width * np.cos(rotation_rad),
                cy - 0.5 * width * np.sin(rotation_rad)
            ])
            medians[i].append([
                cx + 0.5 * width * np.cos(rotation_rad),
                cy + 0.5 * width * np.sin(rotation_rad)
            ])
            medians[i].append([
                cx - 0.5 * height * np.sin(rotation_rad),
                cy + 0.5 * height * np.cos(rotation_rad)
            ])
            medians[i].append([
                cx + 0.5 * height * np.sin(rotation_rad),
                cy - 0.5 * height * np.cos(rotation_rad)
            ])
        distances = [coordinate_geometry.euclidean_distance(s, o) for s in medians[0] for o in medians[1]]
        return min(distances)
    def height_difference(self, other):
        return math.fabs(self.get_height() - other.get_height())
    def height_ratio(self, other):
        """
        Purpose: make the height difference feature scale better with the size of the bounding boxes, by returning the ratio of their sizes instead 
        of their absolute value difference."""
        return max(self.get_height() / other.get_height(), other.get_height() / self.get_height())
    def distance_height_ratio(self, other):
        return self.distance(other) * self.height_ratio(other)
    def overlays(self, other):
        s_center, s_dims, s_rot = self.minimum_bounding_box
        o_center, o_dims, o_rot = other.minimum_bounding_box
        sx, sy = s_center
        s_width, s_height = s_dims
        ox, oy = o_center
        intersecting = sx + s_width * np.cos(s_rot) / 2 >= ox and sx - s_width * np.cos(s_rot) / 2 <= ox
        intersecting &= sy + s_height * np.sin(s_rot) / 2 >= oy and sy - s_height * np.cos(s_rot) / 2 <= oy
        return intersecting
    def get_angle(self):
        angle = self.minimum_bounding_box[2]
        # rotate the angle by 90 degrees if the "height" dimension of the box is not they y axis.
        if self.get_height() != self.minimum_bounding_box[1][1]:
            angle += 90
        return angle
    def sin_angle_difference(self, other):
        # disregard angle differences for very short words, because they often have high error in 
        # their computed angles
        if self.num_letters <= 2 or other.num_letters <= 2:
            return 0
        return math.sin(math.radians(math.fabs(self.get_angle() - other.get_angle())))
    def distance_height_ratio_sin_angle(self, other):
        return self.distance_height_ratio(other) * (1 + self.sin_angle_difference(other))
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
        if self.capitalization != other.capitalization and self.num_letters > 1 and other.num_letters > 1:
            coeff = 2
        return coeff * self.distance(other) * (1 + self.sin_angle_difference(other))
    def distance_height_ratio_sin_angle_capitalization_penalty(self, other):
        return self.distance_sin_angle_capitalization_penalty(other) * self.height_ratio(other)
    
def prims_mst(nodes_list, distance_func = FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty):
    """
    Create a minimum spanning tree of a graph of nodes based on the distance function that is passed
    Parameters: nodes list: a list of Feature Nodes, 
        distance_func: a function to compute the distance between two feature nodes
    Returns: None, modifies the nodes list to connect them into a MST"""
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
def half_prims_mst(nodes_list, distance_func = FeatureNode.height_difference):
    """
    Create a minimum spanning tree of a graph of nodes based on the distance function that is passed,
    and then removes all of the edges that have a distance that is greater than average
    Parameters: nodes list: a list of Feature Nodes, 
        distance_func: a function to compute the distance between two feature nodes
    Returns: None, modifies the nodes list to connect them into a MST with the half of the edges with the longest
    distances removed"""
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
    median_distance = np.median([v["key"] for v in all_neighbors])
    for node in all_neighbors:
        if node["parent"] != None:
            if node["parent"]["vertex"] not in node["vertex"].neighbors and node["key"] < median_distance:
                node["vertex"].neighbors.append(node["parent"]["vertex"])
            if node["vertex"] not in node["parent"]["vertex"].neighbors and node["parent"]["key"] < median_distance:
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
        with open(geojson_file, "r", encoding="utf-8") as fp:
            try:
                json_obj = json.load(fp)
                
                if "name" in json_obj:
                    self.map_id = json_obj["name"]
                self.nodes = []
                for feature_obj in json_obj["features"]:
                    try:
                        new_node = FeatureNode(feature_obj)
                        self.nodes.append(new_node)
                    except:
                        pass
                #print("Time loading:", time.time() - time_loading)
                if connecting_function != None:
                    time_connecting = time.time()
                    connecting_function(self.nodes)
                    #print("Time connecting:", time.time() - time_connecting)
            except:
                print("Unable to load map graph from:", geojson_file)
                self.map_id = None
                self.nodes = []

    def __repr__(self):
        sting_representation = ""
        for node in self.nodes:
            sting_representation += node.post_ocr + "\n"
            for neighbor in node.neighbors:
                sting_representation += "    " + neighbor.post_ocr + "\n"
        return sting_representation

if __name__ == "__main__":
    print(MapGraph("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/geojson_testr_syn/11320000.geojson", prims_mst))