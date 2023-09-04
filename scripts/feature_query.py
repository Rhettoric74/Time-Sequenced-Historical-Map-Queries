import os
import json
from geo_entity import *
from fuzzywuzzy import fuzz
from extract_year import extract_years
from coordinate_geometry import *
from match_countries_to_map_ids import countries_to_ids_dict
import random
import time
import config
def feature_query(feature_name, fclasses = None, ratio_threshold = 90):
    """
    Purpose: query a directory of geojson files for files containing a specific named feature
    Parameters: dir_name, the name of the directory to query
                feature_name, the name of the feature to search for
                ratio_threshold (> 0, <= 100), the threshold for comparing map text to variant names required to consider
                them to match.
                That is, if fuzz.ratio(text, variant) is greater than this threshold, we will consider them to match. 
    returns: a dictionary of each variant of the feature name matched with the map ids of maps that contain that variant.
    """
    entity = GeoEntity(feature_name, fclasses)
    print(entity)
    # initialize list of files containing the feature
    files = {}
    # iterate over all files in the directory
    files_iterated = 0
    # extract relevant maps based on the entries in the countries_to_ids_dict
    # for the country(ies) the feature is in
    relevant_maps = set()
    if isinstance(entity.country, list):
        print(entity.country)
        for country in entity.country:
            relevant_maps = relevant_maps.union(countries_to_ids_dict[country])
    else:
        relevant_maps = set(countries_to_ids_dict[entity.country])
    # cap the relevant maps to search at 10000 if there are more
    if len(list(relevant_maps)) > 10000:
        relevant_maps = random.sample(list(relevant_maps), 10000)
    for file in list(relevant_maps):
        if files_iterated % 100 == 0:
            print(files_iterated, "geojson files searched")
        files_iterated += 1
        # open the file
        try:
            with open(config.GEOJSON_FOLDER + file + ".geojson") as json_file:
                # read the file's contents
                data = json.load(json_file)
        except FileNotFoundError:
            # skip files mentioned in csv file but not in the processed geojson dataset
            continue
        # first check if the entity overlaps with the map's bounds
        if overlaps_with_map_bbox(estimate_map_bounds(data), entity.largest_bounding) == True:
            # iterate over all features in the file
            for feature in data["features"]:
                text = str(feature["properties"]["text"]).upper()
                post_ocr = str(feature["properties"]["postocr_label"]).upper()
                # use fuzzy string comparison to detect a match with known name variants
                coords = feature["geometry"]["coordinates"]
                # check if the point is within the entity being queried
                if entity.within_bounding(coords):
                    # check if features in the neighborhood match a known name
                    for variant in entity.variations:
                        if fuzz.ratio(post_ocr, variant) > ratio_threshold or fuzz.ratio(text, variant) > ratio_threshold:
                            # the text is considered to match the variant
                            # if the feature is found, and close to the coordinates of the entity found by whg, add the file to the list
                            print(post_ocr + ": " + variant)
                            print(entity.largest_bounding)
                            entity.update_bounds(coords)
                            # add the file to the dictionary mapped with the variant found
                            if variant in files:
                                files[variant].append(file.strip(".geojson"))
                            else:
                                files[variant] = [file.strip(".geojson")]
                            break
    # return the list of files
    return files
def dated_query(feature_name, fclasses = None):
    """
    Purpose: wrapper around feature_query which matches the resulting maps with their years
    Parameters: See feature_query
    Returns: Dictionary of name variants, each mapped to another dictionary matching map_ids to their years"""

    feature_results = feature_query(feature_name, fclasses)
    dated_results = {}
    for variant in feature_results.keys():
        dated_results[variant] = extract_years(feature_results[variant])
    return dated_results
    


