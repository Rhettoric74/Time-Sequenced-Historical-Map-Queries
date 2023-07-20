import csv
import numpy as np
import os
import geo_entity
import geopandas as gpd
from shapely.geometry import Point
import json

def sample_map_region(region_name, scale_range = None, filename = "luna_omo_metadata_56628_20220724.csv"):
    """
    Purpose: get a collection of map ids that depict the same region, at similar scales
    Parameters: region name (string), the name of the region to query, 
        scale_range (optional), an array-like containing the minimum
        and maximum scale for the scale of the maps
        filename (string) the name of the folder conatining the entire geojson collection
    Returns: A list of map ids whose points are within the bounding box of the entity, and within the scale range, 
    if specified
    """
    map_ids = []
    dirname = "geojson_testr_syn"
    # ignore casing
    region_name = region_name.upper()
    try:
        entity = geo_entity.GeoEntity(region_name)
    except:
        print("entity not found in WHG")
        return
    
    with open(filename, errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            descriptors_list = [word.upper() for word in row["description"].split()]
            title_words_list = [word.upper() for word in row["title"].split()]
            if region_name in descriptors_list or region_name in title_words_list:
                file = row["filename"]
                if scale_range != None:
                    if row["scale"] != "" and float(row["scale"]) >= scale_range[0] and float(row["scale"]) <= scale_range[1]:
                        map_ids.append(file)
                else:
                    try:               
                        # try to open the file
                        with open(os.getcwd() + "\\" + dirname + "\\" + file + ".geojson") as json_file:
                            # read the file's contents
                            data = json.load(json_file)
                        # iterate over all features in the file
                        within_bounds = 0
                        total_features = 0
                        for feature in data["features"]:
                            total_features += 1
                            if entity.within_bounding(feature["geometry"]["coordinates"]):
                                within_bounds += 1
                        if within_bounds / total_features > 0.1:
                            map_ids.append(file)
                    except:
                        pass
    return map_ids

def create_region_maps_folder(region_name, scale_threshold = None, filename = "luna_omo_metadata_56628_20220724.csv", dir_name = "geojson_testr_syn"):
    ids_list = sample_map_region(region_name, scale_threshold, filename)
    if region_name not in os.listdir():
        os.mkdir(region_name)
    for id in ids_list:
        try:
            with open(dir_name + "/" + id + ".geojson") as fr:
                with open(region_name + "/" + id + ".geojson", "w") as fw:
                    fw.write(fr.read())
        except Exception as e:
            print(e)

if __name__ == "__main__":
    """ cities_to_sample = ["beijing", "marseille", "barcelona", "havanna", "quito"]
    for city in cities_to_sample:
        create_region_maps_folder(city) """
    create_region_maps_folder("japan")