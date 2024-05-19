import json
import math
import sys
import numpy as np
import time
import os
from multiword_name_extraction import extract_map_data_from_all_annotations
sys.path.append("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/scripts")
sys.path.append(os.path.dirname("config.py"))
import coordinate_geometry
import copy

# can change this constant from one to multiply a padding to the padded_bounding_box attribute
# so far this attribute has not been used.
PADDING_RATIO = 1
        
class FeatureNode:
    def __init__(self, feature_obj):
        self.vertices = feature_obj["vertices"]
        self.text = feature_obj["text"]
        self.minimum_bounding_box = coordinate_geometry.convex_hull_min_area_rect(self.vertices)
        self.padded_bounding_box = (self.minimum_bounding_box[0], (PADDING_RATIO * self.minimum_bounding_box[1][0], 
                                            PADDING_RATIO * self.minimum_bounding_box[1][1]), self.minimum_bounding_box[2])
        #print(self.minimum_bounding_box)
        self.neighbors = set()
        self.illegible = feature_obj["illegible"]
        self.truncated = feature_obj["truncated"]
        self.num_letters = len([ch for ch in self.text if ch.isalpha()])
        self.capitalization = self.text.isupper()
    def equals(self, other):
        """Consider two FeatureNodes (i.e. text labels) identical if they have the same text and vertices
        does not override the built-in __eq__ method in order to allow objects to be hashed normally"""
        return (self.text == other.text) and (self.vertices ==  other.vertices)
    def get_ground_truth_linkages(map_filename):
        """Purpose: create a list of FeatureNodes containing the linkages contained in the ground truth file
        Parameters: map_filename, a string filename of the map image to retrieve the ground truth Phrases for
        Returns: a doubly-nested list of phrases for the given map with all groups of labels from the annotations file."""
        phrases_list = []
        map_data = extract_map_data_from_all_annotations(map_filename)
        for group in map_data["groups"]:
            cur_list = []
            for label in group:
                cur_node = FeatureNode(label)
                cur_list.append(cur_node)
            phrases_list.append(cur_list)

        return phrases_list
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
    class EdgeCostFunction:
        """Purpose: creates an edge cost function with customized weighting of the features.
        The function takes the form:
        distance*(height_ratio**a)*(1 + b*sin_angle_difference)*(1 + c*capitalization_difference)
        where a, b, and c, are the weights this function is instantiated with"""
        def __init__(self, weights):
            self.a = weights[0]
            self.b = weights[1]
            self.c = weights[2]
        def __call__(self, label1, label2):
            edge_cost =  FeatureNode.distance(label1, label2) * (FeatureNode.height_ratio(label1, label2) ** self.a) 
            edge_cost *= (1 + self.b * FeatureNode.sin_angle_difference(label1, label2)) * (1 + self.c * FeatureNode.capitalization_difference(label1, label2))
            return edge_cost
            
    def height_difference(self, other):
        return math.fabs(self.get_height() - other.get_height())
    def height_ratio(self, other):
        """
        Purpose: make the height difference feature scale better with the size of the bounding boxes, by returning the ratio of their sizes instead 
        of their absolute value difference."""
        return max(self.get_height() / other.get_height(), other.get_height() / self.get_height())
    def capitalization_difference(self, other):
        """Purpose: represent whether the two labels have different capitalization
        Parameters: self and other, two FeatureNode objects to compare.
        Returns: 0 if the labels are either both in all caps or neither in all caps, 1 otherwise"""
        if self.capitalization != other.capitalization and self.num_letters > 1 and other.num_letters > 1:
            return 1
        return 0
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
    
    
    def to_vector(self, weights = [1000, 100, 100]):
        """Purpose: gives a vector representation of the text label
        Returns: a numpy array containing the label center location, height, capitalization, and angle"""
        c = 0
        if self.capitalization:
            c = 1
        return np.array([self.minimum_bounding_box[0][0], self.minimum_bounding_box[0][1], weights[0] * self.get_height(), weights[1] * self.capitalization, c, weights[2] * self.get_angle()])

class EdgeCostFunction:
        """Purpose: creates an edge cost function with customized weighting of the features.
        The function takes the form:
        distance*(height_ratio**a)*(1 + b*sin_angle_difference)*(1 + c*capitalization_difference)
        where a, b, and c, are the weights this function is instantiated with"""
        def __init__(self, weights):
            self.a = weights[0]
            self.b = weights[1]
            self.c = weights[2]
        def __call__(self, label1, label2):
            edge_cost =  FeatureNode.distance(label1, label2) * (FeatureNode.height_ratio(label1, label2) ** self.a) 
            edge_cost *= (1 + self.b * FeatureNode.distance) * (1 + self.c * FeatureNode.capitalization_difference(label1, label2))
            return edge_cost    
def prims_mst(nodes_list, distance_func = FeatureNode.EdgeCostFunction([1, 1, 1])):
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
            node["vertex"].neighbors.add(node["parent"]["vertex"])
            node["parent"]["vertex"].neighbors.add(node["vertex"])
    
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
        if node["parent"] != None and node["key"] <= median_distance:
            node["vertex"].neighbors.add(node["parent"]["vertex"])
            node["parent"]["vertex"].neighbors.add(node["vertex"])
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
            node["vertex"].neighbors.add(node["parent"]["vertex"])
            node["parent"]["vertex"].neighbors.add(node["vertex"])
def draw_complete_graph(nodes_list):
    """
    Purpose: draw edges between each vertex of the graph and all other vertices of the graph."""
    for node in nodes_list:
        for other_node in nodes_list:
            if not (node is other_node):
                node.neighbors.add(other_node)
                other_node.neighbors.add(other_node)
class MapGraph:
    def __init__(self, map_filename = None, connecting_function = None):

        self.nodes = []
        if map_filename != None:
            map_data = extract_map_data_from_all_annotations(map_filename)
            for group in map_data["groups"]:
                for label in group:
                    cur_node = FeatureNode(label)
                    self.nodes.append(cur_node)

            #print("Time loading:", time.time() - time_loading)
            if connecting_function != None:
                #time_connecting = time.time()
                connecting_function(self.nodes)
                #print("Time connecting:", time.time() - time_connecting)
    def __repr__(self):
        sting_representation = ""
        for node in self.nodes:
            sting_representation += node.text + "\n"
            for neighbor in node.neighbors:
                sting_representation += "    " + neighbor.text + "\n"
        return sting_representation
    def to_matrix(nodes_list, weights = [1000, 100, 100]):
        """
        Purpose: represent all of the nodes in the graph as a matrix
        Returns: a matrix containing the vector representation of each node"""
        return np.array([node.to_vector(weights) for node in nodes_list])
    def __contains__(self, node):
        for graph_node in self.nodes:
            if node.equals(graph_node):
                return True
        return False

if __name__ == "__main__":
    print("\n".join([" ".join([label.text for label in phrase]) for phrase in FeatureNode.get_ground_truth_linkages("5797073_h2_w9.png")]))