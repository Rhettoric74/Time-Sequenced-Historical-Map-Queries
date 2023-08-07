import requests
import csv
from PIL import Image
import glymur
import json
from fuzzywuzzy import fuzz
import io
import cv2

def find_image_url_in_fields(field_values):
    link_indicator = "'Download 1': ['<a href="
    start_index = field_values.find(link_indicator) + len(link_indicator)
    cur_index = start_index
    while cur_index < len(field_values) and field_values[cur_index] != " ":
        cur_index += 1
    return field_values[start_index: cur_index]

def map_ids_to_image_urls(filename = "luna_omo_metadata_56628_20220724.csv"):
    with open(filename, "r", errors="ignore") as f:
        reader = csv.DictReader(f)
        ids_to_urls = {}
        for row in reader:
            ids_to_urls[row["filename"]] = find_image_url_in_fields(row["fieldValues"])
        return ids_to_urls
def get_image(map_id, ids_to_urls):
    url = ids_to_urls[map_id]
    print(url)
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to download the image. Status code: {response.status_code}")
def display_image(image_content, cropping = None):
    image_data = io.BytesIO(image_content)

    # Save the raw image bytes to a temporary file
    with open('temp.jp2', 'wb') as temp_file:
        temp_file.write(image_data.getbuffer())

    # Decode the JP2 image using opencv
    image = cv2.imread('temp.jp2')
    print(image.shape)

    # Check if the image was read successfully
    if image is not None:
        # Display the image using OpenCV
        if cropping != None:
            print(cropping)
            image = image[cropping[1]:cropping[3], cropping[0]:cropping[2]]
        cv2.imshow('JP2 Image', image)

        # Wait until a key is pressed and then close the window
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def get_cropping_bbox(img_coords):
    """
    Purpose: Given a list of image coordinates, find a cropping that goes around the bounding box of those coordinates
    Params: img_coords, a list of 2-d integer pixel coordinates from the map image
    Returns: a 4 element tuple of the form (leftmost_coord, topmost_coord, rightmost_coord, bottommost_coord)
    """
    leftmost_coord = float("inf")
    topmost_coord = float("inf")
    bottommost_coord = -float("inf")
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
    return (max(0,leftmost_coord - 300), max(0, topmost_coord - 300), rightmost_coord + 300, bottommost_coord + 300)
def find_image_cropping(map_id, feature_name, ratio_threshold = 90):
    with open("geojson_testr_syn/" + map_id + ".geojson") as json_file:
        map_data = json.load(json_file)
        for feature in map_data["features"]:
            if fuzz.ratio(feature_name.upper(), feature["properties"]["text"].upper()) > ratio_threshold:
                print(feature["properties"]["text"])
                image_coordinates = feature["properties"]["img_coordinates"]
                print(image_coordinates)
                return get_cropping_bbox(image_coordinates)
def estimate_image_size(map_id):
    with open("geojson_testr_syn/" + map_id + ".geojson") as json_file:
        map_data = json.load(json_file)
        rightmost = 0
        bottommost = 0
        topmost = float("inf")
        leftmost = float("inf")
        for feature in map_data["features"]:
            for point in feature["properties"]["img_coordinates"]:
                if point[0] > rightmost:
                    rightmost = point[0]
                if point[1] > bottommost:
                    bottommost = point[1]
                if point[0] < leftmost:
                    leftmost = point[0]
                if point[1] < topmost:
                    topmost = point[1]
        return (leftmost, topmost, rightmost, bottommost)
            


if __name__ == "__main__":
    ids_to_urls = map_ids_to_image_urls()
    map_id = "9110002"
    print(estimate_image_size(map_id))
    display_image(get_image(map_id, ids_to_urls), find_image_cropping(map_id, "OSLO"))