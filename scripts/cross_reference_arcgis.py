from arcgis.gis import GIS
from arcgis.geometry import Point, Geometry
from arcgis.features import FeatureLayer
from geo_entity import GeoEntity

global gis
gis = GIS()

def obtain_entity_polygonal_coords(entity):
    entity_center_point = Geometry(Point({"x":entity.geolocation[0], "y":entity.geolocation[1], "spatialReference": {"wkid": 4326}}))
    print(entity_center_point)
    print(entity_center_point.is_valid())
    place_name = entity.name
    search_result = gis.content.search(query=f"{place_name} boundaries", item_type="Feature Layer", max_items=5)
    print(search_result)
    if search_result:
        feature_layer_item = search_result[0]
        feature_layer = feature_layer_item.layers[0]

        # Perform a spatial query
        query_result = feature_layer.query(geometry=entity_center_point, spatial_relationship='contains', out_sr='4326')

        # Check if any features are found
        if query_result.features:
            polygons = [feature.geometry for feature in query_result.features]
            for polygon in polygons:
                print(polygon)

        else:
            print("No overlapping polygons found")
    else:
        print("No feature layer found for the place")

if __name__ == "__main__":
    entity = GeoEntity("New York")
    obtain_entity_polygonal_coords(entity)
