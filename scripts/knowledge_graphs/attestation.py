import json

class Attestation(object):
    def __init__(self, map_id, fuzzy_ratio, overlap_confidence, year = None, img_coordinates = None):
        self.map_id = map_id
        self.fuzzy_ratio = fuzzy_ratio
        self.overlap_confidence = overlap_confidence
        self.year = year
        # remove extra nesting from list
        while isinstance(img_coordinates, list) and isinstance(img_coordinates[0][0], list):
            flattened_geometry = []
            for geometry in img_coordinates:
                flattened_geometry += geometry
            img_coordinates = flattened_geometry
        self.img_coordinates = img_coordinates
    def from_json(fields_dict):
        img_coordinates = None
        if "img_coordinates" in fields_dict:
            img_coordinates = fields_dict["img_coordinates"]
        return Attestation(fields_dict["map_id"], fields_dict["fuzzy_ratio"], fields_dict["overlap_confidence"], fields_dict["year"], img_coordinates)
    def get_score(self):
        #TODO: figure out how to evaluate the attestation based on the fuzzy ratio and overlap confidence
        return ((self.fuzzy_ratio / 100) + self.overlap_confidence) / 2
    def __str__(self):
        return ("map_id: " + str(self.map_id) + "\n"
                + "year: " + str(self.year) + "\n"
                + "fuzzy_ratio: " + str(self.fuzzy_ratio) + "\n"
                + "overlap_confidence: " + str(self.overlap_confidence))