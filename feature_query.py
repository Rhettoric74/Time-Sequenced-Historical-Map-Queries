import os
import json
import geo_entity
from fuzzywuzzy import fuzz
from extract_year import extract_years
import sample_map_region
def feature_query(dir_name, feature_name, ratio_threshold = 85):
    """
    Purpose: query a directory of geojson files for files containing a specific named feature
    Parameters: dir_name, the name of the directory to query
                feature_name, the name of the feature to search for
                ratio_threshold (> 0, <= 100), the threshold for comparing map text to variant names required to consider
                them to match.
                That is, if fuzz.ratio(text, variant) is greater than this threshold, we will consider them to match. 
    returns: a dictionary of each variant of the feature name matched with the map ids of maps that contain that variant.
    """
    entity = geo_entity.GeoEntity(feature_name)
    print(entity)
    # initialize list of files containing the feature
    files = {}
    # iterate over all files in the directory
    files_iterated = 0
    for file in os.listdir(os.getcwd() + "\\" + dir_name):
        if files_iterated % 100 == 0:
            print(files_iterated, "geojson files searched")
        files_iterated += 1
        # open the file
        with open(os.getcwd() + "\\" + dir_name + "\\" + file) as json_file:
            # read the file's contents
            data = json.load(json_file)
        # iterate over all features in the file
        for feature in data["features"]:
            text = str(feature["properties"]["text"]).upper()
            post_ocr = str(feature["properties"]["postocr_label"]).upper()
            # use fuzzy string comparison to detect a match with known name variants
            for variant in entity.variations:
                if fuzz.ratio(post_ocr, variant) > ratio_threshold or fuzz.ratio(text, variant) > ratio_threshold:
                    # the text is considered to match the variant
                    # if the feature is found, and close to the coordinates of the entity found by whg, add the file to the list
                    if entity.within_bounding(feature["geometry"]["coordinates"]):
                        print(post_ocr + ": " + variant)
                        print(entity.largest_bounding)
                        # add the file to the dictionary mapped with the variant found
                        if variant in files:
                            files[variant].append(file.strip(".geojson"))
                        else:
                            files[variant] = [file.strip(".geojson")]
    # return the list of files
    return files
def dated_query(dir_name, feature_name):
    """
    Purpose: wrapper around feature_query which matches the resulting maps with their years
    Parameters: See feature_query
    Returns: Dictionary of name variants, each mapped to another dictionary matching map_ids to their years"""

    feature_results = feature_query(dir_name, feature_name)
    dated_results = {}
    for variant in feature_results.keys():
        dated_results[variant] = extract_years(feature_results[variant])
    return dated_results
    


if __name__ == "__main__":
    regions_and_cities = {"norway":["oslo"], "estonia":["tallinn"]}
    for region, cities in regions_and_cities.items():
        sample_map_region.create_region_maps_folder(region)
        for city in cities:
            results = dated_query(region, city)
            print(results)
            matched_with_city = {city:results}
            """ with open("analyzed_cities/" + city + "_dates.json", "w") as fp:
                json.dump(matched_with_city, fp) """