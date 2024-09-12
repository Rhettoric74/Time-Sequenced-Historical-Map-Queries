import cv2
import numpy as np
import map_graph
from map_graph import FeatureNode, MapGraph, MahalanobisMetric
from analyze_recall_data import find_mahalanobis_metric
import multiword_name_extraction
import list_multiword_paths
import os
import clustering_linkages

CORRECTLY_LINKED_COLOR = (0, 255, 0)
INCORRECTLY_LINKED_COLOR = (0, 0, 255)
SINGLE_WORD_COLOR = (255, 0, 0)

def draw_features_and_linkages(map_filename, map_graph, destination_filename = None, show_image = False, map_dir = "icdar24-train-png/train_images"):
    # Read an image
    image = cv2.imread(map_dir + "/" +  map_filename)
    annotated_phrases = FeatureNode.get_ground_truth_linkages(map_filename)
    correctly_linked_nodes = set()
    incorrectly_linked_nodes = set()
    for annotated_phrase in annotated_phrases:
        if len(annotated_phrase) > 1:
            found = list_multiword_paths.search_node_sequence_in_graph(map_graph.nodes, annotated_phrase)
            if found:
                for node in annotated_phrase:
                    correctly_linked_nodes.add(node)
            else:
                for node in annotated_phrase:
                    incorrectly_linked_nodes.add(node)
    correctly_linked_subgraph = MapGraph()
    correctly_linked_subgraph.nodes = list(correctly_linked_nodes)
    incorrectly_linked_subgraph = MapGraph()
    incorrectly_linked_subgraph.nodes = list(incorrectly_linked_nodes)
    #print(correctly_linked_nodes)



    for node in map_graph.nodes:
        label_color = SINGLE_WORD_COLOR
        if node in correctly_linked_subgraph:
            label_color = CORRECTLY_LINKED_COLOR
        elif node in incorrectly_linked_subgraph:
            label_color = INCORRECTLY_LINKED_COLOR
        # Draw the rectangle on the original image
        box = cv2.boxPoints(node.minimum_bounding_box)
        box = np.intp(box)
        cv2.drawContours(image, [box], 0, label_color, 2)
        height_message = "height: " + "{:.1f}".format(node.get_height())
        angle_message = "angle: " + "{:.1f}".format(node.get_angle())
        capitalization_message = "capitalization: " + str(int(node.capitalization))
        text_coords =  list(node.minimum_bounding_box[0])
        angle = np.radians(node.minimum_bounding_box[2])

        padded_box = cv2.boxPoints(node.padded_bounding_box)
        padded_box = np.intp(padded_box)
        cv2.drawContours(image, [padded_box], 0, label_color, 2)

        # text_coords[0] -= np.cos(angle) * node.minimum_bounding_box[1][0] / 2
        text_coords[1] += np.cos(angle) * node.minimum_bounding_box[1][1] / 2
        text_coords = np.intp(text_coords)
        cv2.putText(image, height_message, text_coords, cv2.FONT_HERSHEY_SIMPLEX, 0.4, label_color, 1)
        cv2.putText(image, angle_message, (text_coords[0], text_coords[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, label_color, 1)
        cv2.putText(image, capitalization_message, (text_coords[0], text_coords[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, label_color, 1)

        # draw lines to the neighboring bounding boxes
        for neighbor in node.neighbors:
            edge_color = INCORRECTLY_LINKED_COLOR
            if neighbor in correctly_linked_subgraph:
                edge_color = CORRECTLY_LINKED_COLOR
            rectangles = [node.minimum_bounding_box, neighbor.minimum_bounding_box]
            medians = [[], []]
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
            best_pair = None
            smallest_distance = float("inf")
            for s in medians[0]:
                for o in medians[1]:
                    # compute distance between the medians
                    d = np.linalg.norm([s[0] - o[0],  s[1] - o[1]]) 
                    if d < smallest_distance:
                        best_pair = (s, o)
                        smallest_distance = d
            point1 = np.intp(best_pair[0])
            point2 = np.intp(best_pair[1])
            
            # Create a LineString feature
            cv2.line(image, point1, point2, edge_color, 2)

    # Display the result
    if destination_filename:
        path = "scripts/annotated_linkage_visualizations/" + destination_filename
        cv2.imwrite(path, image)
    if show_image:
        cv2.imshow('Linkage Visualization', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # map_filename = "0041003_h2_w7.png"
    difficult_maps_sample = ["5797073_h2_w9.png", "8817002_h4_w4.png","0068010_h2_w7.png","0071008_h3_w7.png","7807309_h6_w7.png","7911000_h2_w2.png","7810246_h7_w2.png"]
    random_map_sample = ['0041033_h2_w5.png', '0066014_h2_w2.png', '6756003_h3_w8.png', '6323028_h2_w3.png', '0066046_h2_w3.png', '5802011_h4_w4.png', '0231018_h2_w6.png', '6354084_h5_w5.png', '0071013_h2_w2.png', '0071018_h6_w2.png']
    weights_list = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 10, 0], [1, 0, 10], [1, 10, 10]]
    descriptors_to_functions = {
        "distance_height_ratio_sin_angle_penalty": FeatureNode.distance_height_ratio_sin_angle_capitalization_penalty,
        "distance_only":FeatureNode.distance, "height_ratio_only":FeatureNode.height_ratio, "sin_angle_difference_only":FeatureNode.sin_angle_difference, 
        "distance_height_ratio":FeatureNode.distance_height_ratio, "distance_sin_angle_capitalization_penalty" :FeatureNode.distance_sin_angle_capitalization_penalty,
        "distance_height_ratio_sin_angle": FeatureNode.distance_height_ratio_sin_angle, "distance_sin_angle_penalty": FeatureNode.distance_with_sin_angle_penalty,
    }
    """ for map_filename in difficult_maps_sample:
        for descriptor, distance_function in descriptors_to_functions.items():
            mg = map_graph.MapGraph(map_filename)
            map_graph.prims_mst(mg.nodes, distance_function)
            map_annotations = multiword_name_extraction.extract_map_data_from_all_annotations(map_filename)
            draw_features_and_linkages(map_filename, mg, "mst_" + descriptor + "_" + map_filename) """
    map_filename = "0231018_h2_w6.png"
    mg = map_graph.MapGraph(map_filename)
    map_graph.prims_mst(mg.nodes, FeatureNode.EdgeCostFunction([1, 1, 1]))
    map_annotations = multiword_name_extraction.extract_map_data_from_all_annotations(map_filename)
    draw_features_and_linkages(map_filename, mg, "equation_1.png", True)
    mg = map_graph.MapGraph(map_filename)
    map_graph.distance_threshold_graph(mg.nodes)
    map_annotations = multiword_name_extraction.extract_map_data_from_all_annotations(map_filename)
    draw_features_and_linkages(map_filename, mg, "character_distance_threshold.png", True)