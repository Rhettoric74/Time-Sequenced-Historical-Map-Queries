import coordinate_geometry
import json
import os
from extract_year import *
import random

def get_dated_place_names(sample_dir):
    """
    Purpose: extract dated place names data from a sample directory of geojson files
    Paramters: sample_dir (string), the name of the directory to extract data from
    Returns: A dict mapping place names to their coordinates and year
    """ 
    dated_place_names = {}
    for map_file in os.listdir(sample_dir):
        with open(sample_dir + "/" + map_file) as json_file:
            feature_collection = json.load(json_file)
            for feature in feature_collection["features"]:
                post_ocr = feature["properties"]["postocr_label"]
                if post_ocr not in dated_place_names:
                    dated_place_names[post_ocr] = [(coordinate_geometry.get_centroid(feature["geometry"]["coordinates"]),
                                                        float(maps_to_years_dict[map_file.strip(".geojson")]))]
                else:
                    dated_place_names[post_ocr].append((coordinate_geometry.get_centroid(feature["geometry"]["coordinates"]),
                                                        float(maps_to_years_dict[map_file.strip(".geojson")])))
    return dated_place_names
def penetrate_though_maps(dated_place_name_data, coordinates, distance_margin = 0.0001):
    names_to_dates_dict = {}
    for place_name in dated_place_name_data.keys():
        for account in dated_place_name_data[place_name]:
            account_coords = account[0]
            if coordinate_geometry.distance(account_coords, coordinates) < distance_margin:
                if place_name not in names_to_dates_dict:
                    names_to_dates_dict[place_name] = [account[1]]
                else:
                    names_to_dates_dict[place_name].append(account[1])
    return names_to_dates_dict
                    

if __name__ == "__main__":
    data = get_dated_place_names("minnesota")
    print(len(os.listdir("minnesota")))
    random_name, accounts_list= random.choice(list(data.items()))
    print(random_name, accounts_list[0][0])
    print(penetrate_though_maps(data, accounts_list[0][0], 0.1))