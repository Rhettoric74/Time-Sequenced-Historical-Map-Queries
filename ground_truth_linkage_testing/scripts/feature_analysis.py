import json
from map_graph import FeatureNode
import numpy as np
import matplotlib.pyplot as plt

def analyze_height_similarity_among_linked_text(data_filepath = "icdar24-train-png/annotations.json"):
    with open(data_filepath, "r") as f:
        all_data = json.load(f)
        height_ratios_per_group = []
        max_height_ratio = 1
        max_height_ratio_details = None
        for map_data in all_data:
            for group in map_data["groups"]:
                if len(group) > 1:
                    feature_nodes = [FeatureNode(group[i]) for i in range(len(group))]
                    geometric_mean_height_ratio = 1
                    for i in range(len(group) - 1):
                        geometric_mean_height_ratio *= feature_nodes[i].height_ratio(feature_nodes[i + 1])
                    geometric_mean_height_ratio = geometric_mean_height_ratio ** (1 / (len(group) - 1))
                    if geometric_mean_height_ratio > max_height_ratio:
                        max_height_ratio = geometric_mean_height_ratio
                        max_height_ratio_details = " ".join([label["text"] for label in group]), map_data["image"], 
                    height_ratios_per_group.append(geometric_mean_height_ratio)
        height_ratios_per_group.sort()
        print("Mean height ratio:", np.mean(height_ratios_per_group))
        print("Median height ratio:", np.median(height_ratios_per_group))
        print("standard deviation height ratio", np.std(height_ratios_per_group))
        print("Maximum height ratio:", max_height_ratio, "in", max_height_ratio_details)
        plt.plot(height_ratios_per_group)
        plt.xlabel('Rank')
        plt.ylabel('height ratio')
        plt.title('Plot height ratios')

        # Display the plot
        plt.show()

def analyze_angle_similarity_among_linked_text(data_filepath = "icdar24-train-png/annotations.json"):
    with open(data_filepath, "r") as f:
        all_data = json.load(f)
        sin_angle_dif_per_group = []
        for map_data in all_data:
            for group in map_data["groups"]:
                if len(group) > 1:
                    feature_nodes = [FeatureNode(group[i]) for i in range(len(group))]
                    avg_sin_angle_dif = 0
                    for i in range(len(group) - 1):
                        angle_difference = feature_nodes[i].sin_angle_difference(feature_nodes[i + 1])
                        if angle_difference > 0.9:
                            print("High angle difference:", feature_nodes[i].text, feature_nodes[i + 1].text)
                            print("in map:", map_data["image"])
                        avg_sin_angle_dif += angle_difference
                    avg_sin_angle_dif = avg_sin_angle_dif / (len(group) - 1)
                    sin_angle_dif_per_group.append(avg_sin_angle_dif)
        print("Mean sin angle difference:", np.mean(sin_angle_dif_per_group))
        print("Median sin angle difference:", np.median(sin_angle_dif_per_group))
        print("standard deviation sin angle difference", np.std(sin_angle_dif_per_group))
        sin_angle_dif_per_group.sort()
        plt.plot(sin_angle_dif_per_group)
        plt.xlabel('Rank')
        plt.ylabel('height ratio')
        plt.title('Plot of sin angle difference per group')

        # Display the plot
        plt.show()
def analyze_distance_similarity_among_linked_text(data_filepath = "icdar24-train-png/annotations.json"):
    with open(data_filepath, "r") as f:
        all_data = json.load(f)
        average_distance_per_group = []
        max_distance_group_and_map = None
        max_distance = 0
        for map_data in all_data:
            for group in map_data["groups"]:
                if len(group) > 1:
                    feature_nodes = [FeatureNode(group[i]) for i in range(len(group))]
                    avg_distance = 0
                    for i in range(len(group) - 1):
                        distance = feature_nodes[i].distance(feature_nodes[i + 1])
                        avg_distance += distance
                    avg_distance = avg_distance / (len(group) - 1)
                    if avg_distance > max_distance:
                        max_distance = avg_distance
                        max_distance_group_and_map = group, map_data["image"]
                    average_distance_per_group.append(avg_distance)
        print("Mean sin angle difference:", np.mean(average_distance_per_group))
        print("Median sin angle difference:", np.median(average_distance_per_group))
        print("standard deviation sin angle difference", np.std(average_distance_per_group))
        print(max_distance_group_and_map)
        average_distance_per_group.sort()
        plt.plot(average_distance_per_group)
        plt.xlabel('Rank')
        plt.ylabel('Average Distance')
        plt.title('Plot of average distances per group, in terms of pixels between pairs of label bounding boxes')

        # Display the plot
        plt.show()

if __name__ == "__main__":
    #analyze_height_similarity_among_linked_text()
    #analyze_angle_similarity_among_linked_text()
    analyze_distance_similarity_among_linked_text()

        