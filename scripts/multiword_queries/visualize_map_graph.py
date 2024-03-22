from map_graph import *
from shapely.geometry import Point, LineString

def make_map_graph_geojson(mg, filename):
    # Create a list to store LineString features
    line_features = []

    # Iterate through pairs of consecutive points to create LineString features
    for node in mg.nodes:
        for neighbor in node.neighbors:
            rectangles = [node.minimum_bounding_box, neighbor.minimum_bounding_box]
            medians = [[], []]
            for i in range(len(rectangles)): 
                # Extract the rectangle properties
                center, size, angle = rectangles[i]
                cx, cy = center
                width, height = size

                # Calculate the medians with rotation consideration
                rotation_rad = np.radians(angle)  # Convert rotation angle to radians

                # Calculate the rotated medians
                medians[i].append([
                    cx - 0.5 * width * np.cos(rotation_rad),
                    cy - 0.5 * width * np.sin(rotation_rad)
                ])
                medians[i].append([
                    cx + 0.5 * width * np.cos(rotation_rad),
                    cy + 0.5 * width * np.sin(rotation_rad)
                ])
                medians[i].append([
                    cx - 0.5 * height * np.sin(rotation_rad),
                    cy + 0.5 * height * np.cos(rotation_rad)
                ])
                medians[i].append([
                    cx + 0.5 * height * np.sin(rotation_rad),
                    cy - 0.5 * height * np.cos(rotation_rad)
                ])
            best_pair = None
            smallest_distance = float("inf")
            for s in medians[0]:
                for o in medians[1]:
                    d = coordinate_geometry.haversine_distance(s, o)
                    if d < smallest_distance:
                        best_pair = (s, o)
                        smallest_distance = d
            point1 = best_pair[0]
            point2 = best_pair[1]
            
            # Create a LineString feature
            line = LineString([point1, point2])
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
    filename = "3449001"
    mg = MapGraph("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/geojson_testr_syn/" + filename + ".geojson")
    half_prims_mst(mg.nodes, FeatureNode.distance_sin_angle_capitalization_penalty)
    make_map_graph_geojson(mg, "half_mst_distance_sin_angle_capitalization_penalty" + filename)