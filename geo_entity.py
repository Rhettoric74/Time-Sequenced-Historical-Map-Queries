import coordinate_geometry
import whg_requests
import country_converter as coco


class GeoEntity:
    def __init__(self, name):
        """
        Purpose: initialize a GeoEntity object
        Parameters: name, the name of the GeoEntity
        Returns: A geoentity object containing information about it extracted from WHG
        """
        self.name = name
        resulting_geojson = whg_requests.find_most_variants_feature(name)
        if resulting_geojson == None:
            raise Exception("feature not in whg database")
        self.geolocation = coordinate_geometry.get_centroid(resulting_geojson["geometry"]["coordinates"])
        self.variations = [variant.upper() for variant in resulting_geojson["properties"]["variants"]]
        self.place_id = resulting_geojson["properties"]["place_id"]
        if name.upper() not in self.variations:
            self.variations.append(name.upper())
        self.fclass = resulting_geojson["properties"]["fclasses"][0]
        self.largest_bounding = coordinate_geometry.extract_bounds(resulting_geojson["geometry"]["coordinates"], self.fclass)
        # add the country the geoentity is in by converting the ccode from the geojson object
        cc = coco.CountryConverter()
        self.country = cc.convert(resulting_geojson["properties"]["ccodes"], "ISO2", "name_short")
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
        new_bounding = coordinate_geometry.extract_bounds(points, self.fclass)
        for point in points:
            if point[0] >= bounding[0][0] and point[0] <= bounding[1][0] and point[1] >= bounding[0][1] and point[1] <= bounding[1][1]:
                # check if the points should be the new bounding box
                if coordinate_geometry.bounding_box_area(new_bounding) > coordinate_geometry.bounding_box_area(bounding):
                    self.largest_bounding = new_bounding
                return True
        return False
    def __repr__(self):
        return str(self.name) + "\n" + str(self.variations) + "\n" + str(self.geolocation)

if __name__ == "__main__":
    tokyo = GeoEntity("tokyo")
    oslo = GeoEntity("oslo")
    print(tokyo.country)
    print(oslo.country)
    