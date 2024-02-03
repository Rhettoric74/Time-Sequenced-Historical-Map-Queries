import sys
import random
import os
sys.path.append(os.path.dirname("config.py"))
import config
import json
import csv
from osgeo import gdal, osr
global map_gcps_dict
map_gcps_dict = {}
with open(config.METADATA_CSV, "r", errors="ignore") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if (row["gcps"] != ""):
                gcps_dict = json.loads(row["gcps"].replace("'", '"'))
                gcp_list = []
                for item in gcps_dict:
                     gcp_list.append(gdal.GCP(item["location"][0], item["location"][1], 0, item["pixel"][0], item["pixel"][1]))
                map_gcps_dict[row["filename"]] = gcp_list
            else:
                print("no transform for map", row["filename"])

def geo_to_pixel(gcp_list, lon, lat):
    geotransform = gdal.GCPsToGeoTransform(gcp_list, len(gcp_list) - 1)
    print(geotransform)
    if (geotransform == None):
        print("No geotransform found")
        return None
    # Get the inverse geotransform
    inv_geotransform = gdal.InvGeoTransform(geotransform)
    # Use the inverse geotransform to convert geographic coordinates to pixel coordinates
    pixel_x, pixel_y = gdal.ApplyGeoTransform(inv_geotransform, lon, lat)

    return [int(pixel_x + 0.5), int(pixel_y + 0.5)]
def get_map_geotransform(map_id, coords):
    map_gcps = map_gcps_dict[map_id]
    #largest_pixels = max([max(element) for element in map_gcps])
    #print(largest_pixels)
    pixels = geo_to_pixel(map_gcps, coords[0], coords[1])
    print(pixels)
    return pixels
def transform_bbox(map_id, bbox):
    northeast = get_map_geotransform(map_id, bbox[1])
    southwest = get_map_geotransform(map_id, bbox[0])
    pixel_bounds = ([min(southwest[0], northeast[0]), min(southwest[1], northeast[1]), 
            max(southwest[0], northeast[0]), max(southwest[1], northeast[1])]) 
    if pixel_bounds[0] >= pixel_bounds[2] or pixel_bounds[1] >= pixel_bounds[3]:
        print("Bounds not in a valid range")
        return None
    return pixel_bounds
if __name__ == "__main__":
    get_map_geotransform("0026201", [-93.258133, 44.5])