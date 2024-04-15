import numpy as np
import math
import numpy as np
from scipy.spatial import ConvexHull
import cv2
import sys
import os
sys.path.append(os.path.dirname("config.py"))
import config
from pyproj import Transformer



global CRS_TRANSFORMER
CRS_TRANSFORMER = Transformer.from_crs(config.COORD_SYSTEM, 'EPSG:4326')

def transform_coords_point(coords):
    lat_long = list(CRS_TRANSFORMER.transform(coords[0], coords[1]))
    
    return [lat_long[1], lat_long[0]]
def transform_coords_list(coords_list):
    transformed_coords = []
    for coords in coords_list:
        if isinstance(coords[0], list):
            transformed_coords.append(transform_coords_list(coords))
        else:
            if coords == None:
                print("coords is none")
            lat_long = list(CRS_TRANSFORMER.transform(coords[0], coords[1]))
            
            transformed_coords.append([lat_long[1], lat_long[0]])
    return transformed_coords

def convert_image_coords_to_indices(img_coords):
    """Purpose: in some datasets for the geojson labels, the image coordinates are 
    formatted as having negative y values. This function converts such coordinates into
    non-negative integer format that can be used as indices for the image
    Parameters: img_coords, a list of coordinates of the format
        [[x1, y1], ... [xn, yn]]
    Returns: a list that converts the y_coordinates to be non-negative and all coordinates to be integers"""
    return [[int(x), int(math.fabs(y))] for x, y in img_coords]
    


def euclidean_distance(point1, point2):
    return np.linalg.norm(np.array(point2) - np.array(point1))

def convex_hull_min_area_rect(points):
    # Example set of points
    try:
        if len(points) == 1:
            # if polygon is a 3-d list, remove one level of nesting to get proper dimensions
            points = points[0]
        converted_points = np.float32(np.array(points))
        # Compute convex hull
        hull = ConvexHull(converted_points)

        # Extract convex hull vertices
        hull_vertices = converted_points[hull.vertices]

        # Compute minimum bounding rectangle
        rect = cv2.minAreaRect(hull_vertices)
    except Exception as e:
        print(e)
        rect = ((0, 0), (0.001, 0.001), 0)
    return rect
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
    fclass_margins = {"P":1, "S": 1, "T": 2, "A":5, "H":20, "L": 1, "N":0}
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
        
        if feature["geometry"] == None:
            continue

        coords = feature["geometry"]["coordinates"]
        if config.COORD_SYSTEM != "EPSG:4326":
            coords = transform_coords_list(coords)
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
def haversine_distance(coord1, coord2):
    """
    Gives the distance between two geographic coordinates in meters, based on the haversine formula
    """
    # Radius of the Earth in meters
    earth_radius = 6371000  # approximately 6,371 kilometers

    # Extract latitude and longitude from coordinates
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c / 1000

    return distance

def within_bounding(bounding, points):
    """
    Purpose: determine if a set of points overlaps with the largest bounding box found in the entity
    Parameters: points, a list of coordinates
    Returns: Boolean, whether the at least one of the points is within the bounding of the box
    """
    # format points to be a singly-nested list of coorinates
    # e.g. [[x1,y1],[x2,y2],...[xn,yn]]

    if not isinstance(points[0], list):
        points = [points]
    while isinstance(points[0][0], list):
        # remove unnecessary nesting of lists
        points = points[0]
    
    for point in points:
        if point[0] >= bounding[0][0] and point[0] <= bounding[1][0] and point[1] >= bounding[0][1] and point[1] <= bounding[1][1]:
            return True
    points_bbox = extract_bounds(points)
    for bounding_point in bounding:
        if bounding_point[0] >= points_bbox[0][0] and bounding_point[0] <= points_bbox[1][0] and bounding_point[1] >= points_bbox[0][1] and bounding_point[1] <= points_bbox[1][1]:
            return True
    return False

def scale_bbox(bounding_box, scale_coeff):
    """
    Puropse: scale up the size of a coordinate bounding box by a given coefficient
    parameters: bounding_box, a list of 2 coordinates representing the bounding box to scale up,
        scale_coefficient: a positive number to multiply the height and width of the bounding box by, using the same center
    Returns: a list of 2 coordinats of the format [[min_long, min_lat], [max_long, max_lat]]
    """
    width = bounding_box[1][0] - bounding_box[0][0]
    height = bounding_box[1][1] - bounding_box[0][1]
    center = [bounding_box[0][0] + (width / 2), bounding_box[0][1] + (height / 2)]
    print("center:", center)
    new_bbox = [[center[0] - (width * scale_coeff / 2), center[1] - (height * scale_coeff / 2)], 
                [center[0] + (width * scale_coeff / 2), center[1] + (height * scale_coeff / 2)]]
    print(new_bbox)
    return new_bbox

if __name__ == "__main__":
    coords_list = [[[1813418.319177, 839016.238411], [1757624.623408, 839825.706277], [1702380.58673, 838496.901145], [1646496.222923, 839987.198394], [1590373.565034, 840535.85648], [1537304.629523, 839828.119325], [1482543.942202, 837455.861646], [1425461.066592, 834722.0401], [1452434.728455, 671531.638889], [1501642.641003, 673989.471197], [1558686.08584, 675565.490563], [1614683.651321, 675507.203661], [1669297.72304, 675575.701055], [1725021.591673, 676629.75765], [1780295.763063, 676600.533517], [1836215.154903, 676289.311291], [1813418.319177, 839016.238411]]]
    print(transform_coords_point([1813418.319177, 839016.238411]))
    print(transform_coords_list(coords_list))
    