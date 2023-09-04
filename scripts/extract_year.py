import csv
import os
import numpy as np
import config

global maps_to_years_dict
maps_to_years_dict = {}
with open(config.METADATA_CSV, "r", errors="ignore") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        maps_to_years_dict[row["filename"]] = row["date"]

def extract_years(map_ids):
    """
    Purpose: link map ids to the year the map was made, based on luna_omo dataset
    Parameters: map_ids, a list of map ids to link
    Returns: a dictionary mapping map ids to years
    """
    return {id:float(maps_to_years_dict[id]) for id in map_ids if len(maps_to_years_dict[id]) > 0}

    