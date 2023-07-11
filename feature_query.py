import os
import json
import geo_entity
import coordinate_geometry
from extract_year import extract_years
def feature_query(dir_name, feature_name):
    """
    Purpose: query a directory of geojson files for files containing a specific named feature
    Parameters: dir_name, the name of the directory to query
                feature_name, the name of the feature to search for
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
            text = str(feature["properties"]["text"])
            post_ocr = str(feature["properties"]["postocr_label"])
            if (text in entity.variations or text.lower() in entity.variations or text.upper() in entity.variations
                            or post_ocr in entity.variations or post_ocr.lower() in entity.variations or post_ocr.upper() in entity.variations):
                #if the feature is found, and close to the coordinates of the entity found by whg, add the file to the list
                if entity.within_bounding(feature["geometry"]["coordinates"]):
                    print(feature["properties"]["text"])
                    print(entity.largest_bounding)
                    # add the file to the dictionary mapped with the variant found
                    if post_ocr.upper() in files:
                        files[post_ocr.upper()].append(file.strip(".geojson"))
                    else:
                        files[post_ocr.upper()] = [file.strip(".geojson")]
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
    cities = ["mexico", "brasilia", "sucre"]
    for city in cities:
        results = dated_query("geojson_testr_syn", city)
        print(results)
        matched_with_city = {city:results}
        with open("analyzed_cities/" + city + "_dates.json", "w") as fp:
            json.dump(matched_with_city, fp)