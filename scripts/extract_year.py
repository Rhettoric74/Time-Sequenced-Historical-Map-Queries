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

def extract_years(attestations):
    """
    Purpose: link map ids to the year the map was made, based on luna_omo dataset
    Parameters: attestations, a json list of Attestation dictionaries
    Returns: none, updates the year field of each dict to include the date of the map
    """
    for attestation in attestations:
        year = maps_to_years_dict[attestation["map_id"]]
        if len(year) > 0:
            try:
                year = float(year)
                attestation["year"] = year
            except:
                print("error converting map date to float")
    

    