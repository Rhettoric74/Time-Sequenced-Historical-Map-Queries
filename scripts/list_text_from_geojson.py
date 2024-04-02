import os
import sys
sys.path.append(os.getcwd())
import json
import config
import coordinate_geometry

def list_text_from_geojson(map_filename, pixel_bounds = None):
    words_list = []
    with open(config.GEOJSON_FOLDER + map_filename, "r", encoding="utf-8") as f:
        map_data = json.load(f)
        for feature in map_data["features"]:
            if pixel_bounds == None or coordinate_geometry.within_bounding(
                pixel_bounds, coordinate_geometry.convert_image_coords_to_indices(feature["properties"]["img_coordinates"])):
                words_list.append(feature["properties"]["postocr_label"])
    return words_list
def filter_labels_by_length(map_text_list, length_threshold = 1):
    return [label for label in map_text_list if len(label) <= length_threshold]

if __name__ == "__main__":
    print(filter_labels_by_length(list_text_from_geojson("5820590.geojson")))
