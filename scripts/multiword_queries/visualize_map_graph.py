from map_graph import *
from shapely.geometry import Point, LineString

def make_map_graph_geojson(mg, filename):
    # Create a list to store LineString features
    line_features = []

    # Iterate through pairs of consecutive points to create LineString features
    for node in mg.nodes:
        for neighbor in node.neighbors:
            point1 = Point(node.centroid)
            point2 = Point(neighbor.centroid)
            
            # Create a LineString feature
            line = LineString([point1.coords[0], point2.coords[0]])
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": list(line.coords)
                },
                "properties": {}
            }

            # Append the LineString feature to the list
            line_features.append(feature)

    # Create a FeatureCollection from the list of LineString features
    feature_collection = {
        "type": "FeatureCollection",
        "features": line_features
    }

    # Write the GeoJSON data to a file
    with open("graph_visualizations/" + filename + "_graph_visualization.geojson", 'w') as f:
        json.dump(feature_collection, f)
if __name__ == "__main__":
    filename = "0377051"
    mg = MapGraph("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/geojson_testr_syn/" + filename + ".geojson")
    prims_mst(mg.nodes, FeatureNode.distance_sin_angle_capitalization_penalty)
    make_map_graph_geojson(mg, "distance_sin_angle_capitalization_penalty" + filename)