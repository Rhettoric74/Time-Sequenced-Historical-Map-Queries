import requests
import json

def place_request_index(place_name, fclass = "P"):
    """
    Purpose: function to query the whgazetteer index endpoint for a place name.

    Parameters: place_name, the name of the place to query for, fclass, the feature class of the place to query for.
    fclass can be one of the following: A (administative), H (hydrological), L (landscape), P (settlements), 
    S (sites), T (topographical). Default value is P, as settlements will likely be most common/useful.
    
    Returns: a json object containing the results of the query."""

    url = "https://whgazetteer.org/api/index/?name=" + place_name + "&fclass=" + fclass
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print("status code", response.status_code)
        raise Exception("Api request failed")

def most_variants(geojson_obj):
    """Purpose: from a geojson object, find the feature with the most name variants.
    Parameters: geojson_obj, a geojson object.
    Returns: the feature with the most name variants."""
    most_variants_found = -1
    higest_variants = None
    for feature in geojson_obj["features"]:
        if len(feature["properties"]["variants"]) > most_variants_found:
            # only include geojson objects that have usable geometries
            if type(feature["geometry"]) == dict:
                higest_variants = feature
                most_variants_found = len(feature["properties"]["variants"])
    return higest_variants
def find_fclasses(place_name):
    """Purpose: find the feature class of a place name based on what type it appears in WHGazetteer.
    Parameters: place_name, the name of the place to query for.
    Returns: the feature class of the place name, can be A (administative), H (hydrological), L (landscape), P (settlements), 
    S (sites), T (topographical)."""
    possibilities = ["P", "S", "T", "A", "H", "L"]
    fclasses = []
    for possibility in possibilities:
        if place_request_index(place_name, possibility)["count"] > 0:
            fclasses.append(possibility)
    return fclasses
def find_most_variants_feature(place_name, fclasses = None):
    """
    Purpose: find the feature with a given name that has the most place name variants
    Parameters: place_name, (string) name of the place to query
                fclass, list of fclasses (characters) to include. If not passed, will automatically 
                get all fclasses for the place name
    Returns: geojson object representing entity with the most variants.
    """
    if fclasses == None:
        fclasses = find_fclasses(place_name)
        if fclasses == []:
            return None
    most_variants_found = -1
    most_variants_geojson = None
    for fclass in fclasses:
        feature_collection = place_request_index(place_name, fclass)
        most_variants_in_fclass = most_variants(feature_collection)
        if len(most_variants_in_fclass["properties"]["variants"]) > most_variants_found:
            most_variants_found = len(most_variants_in_fclass["properties"]["variants"])
            most_variants_geojson = most_variants_in_fclass
    return most_variants_geojson

def bbox_request(sw, ne, fclasses = ["P", "S", "T", "A", "H", "L"]):
    """
    Purpose: make spatial requests for whg API, giving all places whose coordinates are within a bounding box
    Parameters: sw, ne (list of 2-D coordinates) the coordinates of the southwest and northeast corners of the bounding box to be searched,
    fclasses (list), a list of all fclasses to search for
    Returns: a geojson object (feature collection) containing all of the features of the given fclasses that
    are within the given box
    """
    # coordinates must be converted to strings to allow for the .join method to be used
    sw = [str(coord) for coord in sw]
    ne = [str(coord) for coord in ne]
    url = "https://whgazetteer.org/api/spatial/?type=bbox&sw=" + ",".join(sw) + "&ne=" 
    url += ",".join(ne) + "&fc=" + ",".join(fclasses)
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content)


if __name__ == "__main__":
    resulting_json = find_most_variants_feature("oslo")
    