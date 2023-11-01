import coordinate_geometry
import whg_requests
import country_converter as coco
import os
import json

class GeoEntity:
    def __init__(self, name = None, fclasses = None):
        """
        Purpose: initialize a GeoEntity object
        Parameters: name, the name of the GeoEntity
                    fclasses, the possible fclasses to search, all fclasses if None is passed
        Returns: A geoentity object containing information about it extracted from WHG
        """
        if name == None:
            return
        self.name = name
        resulting_geojson = whg_requests.find_most_variants_feature(name, fclasses)
        if resulting_geojson == None:
            raise Exception("feature not in whg database")
        if "coordinates" in resulting_geojson["geometry"].keys():
            coordinates = resulting_geojson["geometry"]["coordinates"]
        else:
            coordinates = resulting_geojson["geometry"]["geometries"][0]["coordinates"]
        self.geojson = resulting_geojson
        self.geolocation = coordinate_geometry.get_centroid(coordinates)
        self.variations = [variant.upper() for variant in resulting_geojson["properties"]["variants"] if variant.upper() != "THE"]
        self.place_id = resulting_geojson["properties"]["place_id"]
        if name.upper() not in self.variations:
            self.variations.append(name.upper())
        self.fclass = resulting_geojson["properties"]["fclasses"][0]
        self.largest_bounding = coordinate_geometry.extract_bounds(coordinates, self.fclass)
        # add the country the geoentity is in by converting the ccode from the geojson object
        cc = coco.CountryConverter()
        self.country = cc.convert(resulting_geojson["properties"]["ccodes"], "ISO2", "name_short")
    def from_geojson(self, geojson_obj):
        self.geojson = geojson_obj
        if "coordinates" in geojson_obj["geometry"].keys():
            coordinates = geojson_obj["geometry"]["coordinates"]
        else:
            coordinates = geojson_obj["geometry"]["geometries"][0]["coordinates"]
        self.geojson = geojson_obj
        self.geolocation = coordinate_geometry.get_centroid(coordinates)
        self.variations = [variant.upper() for variant in geojson_obj["properties"]["variants"] if variant.upper() != "THE"]
        self.place_id = geojson_obj["properties"]["place_id"]
        name = geojson_obj["properties"]["title"]
        self.name = name
        if name.upper() not in self.variations:
            self.variations.append(name.upper())
        self.fclass = geojson_obj["properties"]["fclasses"][0]
        self.largest_bounding = coordinate_geometry.extract_bounds(coordinates, self.fclass)
        # add the country the geoentity is in by converting the ccode from the geojson object
        cc = coco.CountryConverter()
        self.country = cc.convert(geojson_obj["properties"]["ccodes"], "ISO2", "name_short")
    def within_bounding(self, points):
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
        
        bounding = self.largest_bounding
        for point in points:
            if point[0] >= bounding[0][0] and point[0] <= bounding[1][0] and point[1] >= bounding[0][1] and point[1] <= bounding[1][1]:
                return True
        points_bbox = coordinate_geometry.extract_bounds(points)
        for bounding_point in bounding:
            if bounding_point[0] >= points_bbox[0][0] and bounding_point[0] <= points_bbox[1][0] and bounding_point[1] >= points_bbox[0][1] and bounding_point[1] <= points_bbox[1][1]:
                return True
        return False
    def update_bounds(self, points):
        # check if the points should be the new bounding box
        new_bounding = coordinate_geometry.extract_bounds(points, self.fclass)
        if coordinate_geometry.bounding_box_area(new_bounding) > coordinate_geometry.bounding_box_area(new_bounding):
            self.largest_bounding = new_bounding

    def overlap_confidence(self, coords):
        #TODO
        """
        Purpose: evaluate the confidence of the geographic match based on how much coords overlap with 
        the entity's bounding.
        Parameters: coords, a nested list of geographic coordinates
        Returns: a score form 0 to 1 of how confident the overlap is.
            Calculated as the ratio of the intersection area and the area of coords"""
        coord_bounds = coordinate_geometry.extract_bounds(coords)
        bbox = self.largest_bounding
        intersection = [[max(coord_bounds[0][0], bbox[0][0]), max(coord_bounds[0][1], bbox[0][1])], [min(coord_bounds[1][0], bbox[1][0]), min(coord_bounds[1][1], bbox[1][1])]]
        return coordinate_geometry.bounding_box_area(intersection) / coordinate_geometry.bounding_box_area(coord_bounds)

    def __repr__(self):
        return str(self.name) + "\n" + str(self.variations) + "\n" + str(self.geolocation)
if __name__ == "__main__":
    for file in os.listdir("analyzed_features/input_queries"):
        with open("analyzed_features/input_queries/" + file) as fp:
            json_object = json.load(fp)
            if "geojson" not in json_object:
                name = list(json_object.keys())[0]
                if name == "geojson":
                    name = list(json_object.keys())[1]
                json_object["geojson"] = GeoEntity(name).geojson
        with open("analyzed_features/input_queries/" + file, "w") as fw:
            json.dump(json_object, fw)