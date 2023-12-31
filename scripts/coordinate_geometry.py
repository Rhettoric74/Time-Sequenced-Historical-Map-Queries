import numpy as np
import math
def get_centroid(points):
    """
    Purpose: get the centroid of a list of point coordinates
    Parameters: points, a list of 2-d coordinates (represented as lists)
    Returns: the centroid of the polygon defined by the points, or if points is a single point, it returns that point
    """
    # check if the input list was just a single point, if so return it
    if not isinstance(points[0], list):
        return points
    # remove brackets from unnecessarily nested lists
    while isinstance(points[0][0], list):
        points = points[0]
    centroid = np.array([0.0, 0.0])
    for point in points:
        centroid += np.array(point)
    centroid /= len(points)
    return centroid.tolist()
def distance(point1, point2):
    """
    Purpose: get the distance between two points
    Parameters: point1, the first point
                point2, the second point
    Returns: the distance between the two points
    """
    return np.linalg.norm(np.array(point1) - np.array(point2))

def extract_bounds(points, fclass = "N"):
    """
    Purpose: Given a set of geocoordinates, give the minimum & maximum for lattitude and longitude
    of the coordinates
    Parameters: points, a list of coordinates, where each coordinate is an array-like of the format
    [longitude, lattitude],
    fclass, the fclass of the entity, which will pad the initial bounds of the entity's coordinates. If "N" (default)
    is passed, no padding will be added to the coordinates
    returns: A list of the form [[min_longitude, min_lattitude], [max_longitude, max_lattitude]]
    """
    # format points to be a singly-nested list of coorinates
    # e.g. [[x1,y1],[x2,y2],...[xn,yn]]

    if not isinstance(points[0], list):
        points = [points]
    while isinstance(points[0][0], list):
        # remove unnecessary nesting of lists
        points = points[0]
    fclass_margins = {"P":1, "S": 1, "T": 2, "A":1, "H":20, "L": 1, "N":0}
    distance = fclass_margins[fclass] / 2
    centroid = get_centroid(points)
    min_long = centroid[0] - distance
    max_long = centroid[0] + distance
    min_lat = centroid[1] - distance
    max_lat = centroid[1] + distance
    for point in points:
        if point[0] < min_long:
            min_long = point[0]
        elif point[0] > max_long:
            max_long = point[0]
        if point[1] < min_lat:
            min_lat = point[1]
        elif point[1] > max_lat:
            max_lat = point[1]
    return [[min_long, min_lat], [max_long, max_lat]]
def bounding_box_area(mins_maxes_list):
    """ give the rectangular area of a bounding box with the given coordinate extrema """
    return (mins_maxes_list[1][0] - mins_maxes_list[0][0]) * (mins_maxes_list[1][1] - mins_maxes_list[0][1])
def estimate_map_bounds(feature_collection):
    """
    Purpose: get the approximate rectangular bounding of a map geojson file
    Parameters: feature_collection, the geojson object to get the bounding coordinates of
    Returns: bounding coordinates in the format:
    [[southwest_longitude, southwest_latitude], [northeast_longitude, northeast_latitude]]
    """
    
    southwest_long = float("inf")
    southwest_lat = float("inf")
    northeast_long = -float("inf")
    northeast_lat = -float("inf")

    for feature in feature_collection["features"]:
        coords = feature["geometry"]["coordinates"]
        # format the coordinates as a list of 2-d coordinate lists
        if not isinstance(coords[0], list):
            coords = [coords]
        while isinstance(coords[0][0], list):
            coords = coords[0]
        for coord in coords:
            # ensure coordinates are between [-90, -180] and [90, 180], 
            # wrapping around if necessary
            coord = normalize_coordinate(coord)
            if coord[0] < southwest_long:
                southwest_long = coord[0]
            elif coord[0] > northeast_long:
                northeast_long = coord[0]
            if coord[1] < southwest_lat:
                southwest_lat = coord[1]
            elif coord[1] > northeast_lat:
                northeast_lat = coord[1]
    return [[southwest_long, southwest_lat], [northeast_long, northeast_lat]]

def normalize_coordinate(point):
    """
    Purpose: given a wgs84 coordinate, return the equivalent coordinate with values restricted between
    [(-90-90), (-180-180)].
    Parameters: point, (list) in the format [latitude, longitude]
    returns: an equivalent point with its values in the standard range"""
    normalized_latitude = positive_mod(point[1] + 90, 180) - 90
    normalized_longitude = positive_mod(point[0] + 180, 360) - 180
    return [normalized_longitude, normalized_latitude]

def positive_mod(x, y):
    return math.fmod((math.fmod(x, y) + y), y)

def overlaps_with_map_bbox(map_bounds, points):
    # check if a set of points overlaps with the bounding box of the map
    for point in points:
        if (point[0] >= map_bounds[0][0] and point[0] <= map_bounds[1][0] 
                        and point[1] >= map_bounds[0][1] and point[1] <= map_bounds[1][1]):
            return True
    return False



                                     