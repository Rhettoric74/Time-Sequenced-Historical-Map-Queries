from scripts.coordinate_geometry import *
from scripts.geo_entity import GeoEntity
import json
import os
import config

def match_countries_to_map_ids(country_names, map_dir):
    """
    Purpose: Match each country to the ids of maps that overlap with it.
    One map can contain (and be matched with) multiple countries
    Parameters: country_names, a list of countries to match with maps, map_dir, a directory
    containing geojson files of maps to match with countries.
    Returns: A json dictionary mapping each country with a list of map_ids that contain them
    """
    countries_to_map_ids = {}
    countries = []
    for country in country_names:
        # first try querying specifically for administrative feature of the country,
        # if that entry causes problems (i.e. has no coordinates), find other fclasses
        try:
            countries.append(GeoEntity(country, ["A"]))
        except:
            try:
                countries.append(GeoEntity(country))
            except:
                print(country, "not found in gazetteer")
    print("countries geocoded")
    files_searched = 0
    for file in os.listdir(map_dir):
        with open(map_dir + "/" + file) as json_file:
            feature_collection = json.load(json_file)
        bounds = estimate_map_bounds(feature_collection)
        for country in countries:
             
            if overlaps_with_map_bbox(bounds, country.largest_bounding) or overlaps_with_map_bbox(country.largest_bounding, bounds):
                if country.name in countries_to_map_ids:
                    countries_to_map_ids[country.name].append(file.strip(".geojson"))
                else:
                    countries_to_map_ids[country.name] = [file.strip(".geojson")]
        files_searched += 1
        if files_searched % 100 == 0:
            print(files_searched)
    return countries_to_map_ids
global countries_to_ids_dict
with open("countries_to_map_ids.json") as fp:
    countries_to_ids_dict = json.load(fp)
    # add Hong Kong maps to the list, use the same ones as China
    countries_to_ids_dict["Hong Kong"] = countries_to_ids_dict["China"]