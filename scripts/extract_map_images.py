import requests
import csv
from variation_stats import list_accounts_in_order
import json
from fuzzywuzzy import fuzz
import io
import os
import cv2
import config
import random
import sys
import math
import coordinate_geometry
from multiword_queries.map_graph import FeatureNode, MapGraph, prims_mst
sys.path.append(os.path.join(os.getcwd(), "scripts/knowledge_graphs"))
sys.path.append(os.path.join(os.getcwd(), "scripts/multiword_queries"))
from multiword_queries.multiword_query import search_from_node
from place_node import PlaceNode
from pixel_georefereferencing import transform_bbox
import list_text_from_geojson

def find_image_url_in_fields(field_values):
    link_indicator = "'Download 1': ['<a href="
    start_index = field_values.find(link_indicator) + len(link_indicator)
    cur_index = start_index
    while cur_index < len(field_values) and field_values[cur_index] != " ":
        cur_index += 1
    return field_values[start_index: cur_index]

def map_ids_to_image_urls(filename = config.METADATA_CSV):
    with open(filename, "r", errors="ignore") as f:
        reader = csv.DictReader(f)
        ids_to_urls = {}
        for row in reader:
            ids_to_urls[row["filename"]] = find_image_url_in_fields(row["fieldValues"])
        return ids_to_urls
def get_image(map_id, ids_to_urls):
    requests.urllib3.disable_warnings()
    url = ids_to_urls[map_id]
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to download the image. Status code: {response.status_code}")
def load_image(map_id, image_content, cropping = None):
    image_data = io.BytesIO(image_content)
    if not os.path.isdir("map_images"):
        os.mkdir("map_images")

    # Save the raw image bytes to a temporary file
    with open("map_images/" + map_id + '.jp2', 'wb') as temp_file:
        temp_file.write(image_data.getbuffer())

    # Decode the JP2 image using opencv
    image = cv2.imread("map_images/" +map_id + '.jp2')
    if cropping == None:
        return image
    # Check if the image was read successfully
    # make sure that image cropping does not go out of array bounds
    height, width, channels = image.shape
    cropping[1] = min(width, max(cropping[1], 0))
    cropping[3] = min(width, max(cropping[3], 0))
    cropping[0] = min(height, max(cropping[0], 0))
    cropping[2] = min(height, max(cropping[2], 0))
    print(cropping)

    if image is not None:
        # Display the image using OpenCV
        if cropping != None:
            image = image[min(cropping[1], cropping[3]):max(cropping[1], cropping[3]), min(cropping[0], cropping[2]): max(cropping[0], cropping[2])]
    return image
def make_tiles_from_image(image_filepath, num_tiles_across, num_tiles_down):
   
    # Decode the JP2 image using opencv
    image = cv2.imread(image_filepath)
    # Check if the image was read successfully
    # make sure that image cropping does not go out of array bounds
    height, width, channels = image.shape
    map_id = image_filepath.strip(".jp2")
    pixel_dimensions = (height // num_tiles_across, width // num_tiles_down)
    for i in range(num_tiles_across):
        for j in range(num_tiles_down):
            image_tile = image[i * pixel_dimensions[0]: (i + 1) * pixel_dimensions[0], j * pixel_dimensions[1]:(j + 1) * pixel_dimensions[1]]
            # image_tile = cv2.cvtColor(image_tile, cv2.COLOR_BGR2RGB)
            image_tile_filepath = map_id + "_tiles/" +  map_id.strip("map_images/") + "_h" + str(i) + "_w" + str(j) + ".png"
            pixel_bounding = [[j * pixel_dimensions[1], i * pixel_dimensions[0]], [(j + 1) * pixel_dimensions[1], (i + 1) * pixel_dimensions[0]]]
            label_list = list_text_from_geojson.list_text_from_geojson(map_id.strip("map_images/") + ".geojson", pixel_bounding)
            print(image_tile_filepath)
            print(pixel_bounding)
            cv2.imwrite(image_tile_filepath, image_tile)
            label_list_filepath = map_id + "_labels_lists/"
            if not os.path.exists(label_list_filepath):
                # Create the directory and all its parents if they don't exist
                os.makedirs(label_list_filepath)
            if not os.path.exists(image_tile_filepath):
                # Create the directory and all its parents if they don't exist
                os.makedirs(image_tile_filepath)
            label_list_filepath += "h" + str(i) + "_w" + str(j) + ".txt"
            with open(label_list_filepath, "w", encoding="utf-8") as fw:
                fw.write(str(label_list))



def get_cropping_bbox(img_coords, use_scale = True):
    """
    Purpose: Given a list of image coordinates, find a cropping that goes around the bounding box of those coordinates
    Params: img_coords, a list of 2-d integer pixel coordinates from the map image
    Returns: a 4 element tuple of the form (leftmost_coord, topmost_coord, rightmost_coord, bottommost_coord)
    """
    if img_coords == None:
        return None
    leftmost_coord = float("inf")
    topmost_coord = float("inf")
    bottommost_coord = - float("inf")
    rightmost_coord = - float("inf")
    for point in img_coords:
        if point[1] > bottommost_coord:
            bottommost_coord = point[1]
        if point[1] < topmost_coord:
            topmost_coord = point[1]
        if point[0] < leftmost_coord:
            leftmost_coord = point[0]
        if point[0] > rightmost_coord:
            rightmost_coord = point[0]     
    if not use_scale:
        return (max(0,leftmost_coord - 300), max(0, topmost_coord - 300), rightmost_coord + 300, bottommost_coord + 300)
    else:
        scaled_bbox = coordinate_geometry.scale_bbox([[leftmost_coord, topmost_coord], [rightmost_coord, bottommost_coord]], 5)      
        # convert height indices back into positive numbers
        print("scaling bbox")
        scaled_bbox = coordinate_geometry.convert_image_coords_to_indices(scaled_bbox)
        return scaled_bbox[0] + scaled_bbox[1]
def find_image_cropping(map_id, account):
    feature_name = account.variant_name
    with open(config.GEOJSON_FOLDER +  map_id + ".geojson") as json_file:
        map_data = json.load(json_file)
        for feature in map_data["features"]:
            if fuzz.ratio(feature_name.upper(), feature["properties"]["text"].upper()) >= account.fuzzy_ratio:
                image_coordinates = feature["properties"]["img_coordinates"]
                if config.COORD_SYSTEM == 'EPSG:3857':
                    image_coordinates = coordinate_geometry.convert_image_coords_to_indices(image_coordinates)
                return get_cropping_bbox(image_coordinates)

def find_multiword_image_cropping(map_id, account, largest_bounding):
    map_graph = MapGraph("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/" + config.GEOJSON_FOLDER + map_id + ".geojson")
    overlapping_nodes = [node for node in map_graph.nodes if coordinate_geometry.within_bounding(largest_bounding, node.coordinates)]
    feature_name = account.variant_name

    map_graph = MapGraph("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/" + config.GEOJSON_FOLDER + map_id + ".geojson")
    overlapping_nodes = [node for node in map_graph.nodes if coordinate_geometry.within_bounding(largest_bounding, node.coordinates)]
    prims_mst(overlapping_nodes, FeatureNode.distance_sin_angle_capitalization_penalty)
    frontier = [overlapping_nodes[0]]
    explored = []
    num_words = feature_name.count(" ")
    image_coordinates = None
    while frontier != []:
        cur_node = frontier.pop(0)
        explored.append(cur_node)
        node_sequences = search_from_node(cur_node, num_words)
        #print(node_sequences)
        for node_sequence in node_sequences:
            joined_text = " ".join([node.post_ocr for node in node_sequence])
            cur_ratio = fuzz.ratio(joined_text.upper(), feature_name.upper())
            if cur_ratio >= account.fuzzy_ratio: 
                image_coordinates = []
                for node in node_sequence:
                    image_coordinates += node.img_coordinates
    return get_cropping_bbox(image_coordinates)
def estimate_image_size(map_id):
    with open(config.GEOJSON_FOLDER + map_id + ".geojson") as json_file:
        map_data = json.load(json_file)
        rightmost = 0
        bottommost = 0
        topmost = float("inf")
        leftmost = float("inf")
        for feature in map_data["features"]:
            img_coordinates = feature["properties"]["img_coordinates"]
            if config.COORD_SYSTEM == 'EPSG:3857':
                img_coordinates = coordinate_geometry.convert_image_coords_to_indices(img_coordinates)
            for point in img_coordinates:
                if point[0] > rightmost:
                    rightmost = point[0]
                if point[1] > bottommost:
                    bottommost = point[1]
                if point[0] < leftmost:
                    leftmost = point[0]
                if point[1] < topmost:
                    topmost = point[1]
        return (leftmost, topmost, rightmost, bottommost)

def download_map_image(map_id):
    ids_to_urls = map_ids_to_image_urls()
    image = load_image(map_id, get_image(map_id, ids_to_urls))
    cv2.imwrite("map_images/" + map_id + ".jp2", image)
    
def extract_images_from_accounts_file(filename, max_sample = None, use_place_node = False):
    """
    Purpose: get an array of cropped images for each map in a named account file
    Parameters: filename (string), a path to the file containing the named accounts you want to extract cropped images of
    returns: a tuple containing the image array followed by the corresponding list of named accounts"""
    ids_to_urls = map_ids_to_image_urls()
    images = []
    with open(filename) as fp:
        obj = json.load(fp)
        keys_list = list(obj.keys())
        keys_list.remove("geojson")
        largest_bounding = obj[keys_list[0]]["largest_bounding_box"]
    
    if use_place_node:
        # use place node class to get ordered accounts list if the file is in the new format 
        accounts_list = PlaceNode(filename).list_accounts_in_order()
    else:
        accounts_list = list_accounts_in_order(filename)
    if max_sample != None and max_sample < len(accounts_list):
        # temporary change: retrieve maps that have smallest overlap confidence (big labels that changed the bounds)
        accounts_list = random.sample(accounts_list, max_sample)
        # accounts_list = sorted(accounts_list, key = lambda account : account.overlap_confidence)[:min(len(accounts_list), max_sample)]
        accounts_list.sort()
    print(len(accounts_list))
    counter = 1
    for account in accounts_list:
        print(counter)
        counter += 1
        try:
            """ # determine how to find cropping based on whether the name is a single word or multiple words
            if (len(account.variant_name.split(" ")) == 1):
                image = load_image(account.map_id, get_image(account.map_id, ids_to_urls), find_image_cropping(account.map_id, account))
            else:
                image = load_image(account.map_id, get_image(account.map_id, ids_to_urls), find_multiword_image_cropping(account.map_id, account, largest_bounding)) """
            if account.img_coordinates == None:
                image = load_image(account.map_id, get_image(account.map_id, ids_to_urls), transform_bbox(account.map_id, coordinate_geometry.scale_bbox(largest_bounding, 4)))
            else:
                image = load_image(account.map_id, get_image(account.map_id, ids_to_urls), get_cropping_bbox(account.img_coordinates))
            converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            images.append(converted_image)
        except Exception as e:
            print(e, "image failed to be appended")
    return images, accounts_list
        