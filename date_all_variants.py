import json
import geo_entity
import coordinate_geometry
from extract_year import maps_to_years_dict
import os

def date_all_variants(dir_name):
    """Purpose: Looks through a dataset of historical map geojson files, mapping each name variant with the dates of maps
    on which it appears. This is similar to feature query, except it records every feature appearing in the map dataset,
    not just one specific feature
    Parameters: dir_name, the name of the directory to search
    Returns: a json object of the format:
        {place_id:
            {
            variant_name:
                {map_id: date
                .
                .
                }
            .
            . 
            }
        .
        .
        }"""

    features_to_variant_dates = {}
    fclass_margins = {"P":5, "S": 1, "T": 5, "A":20, "H":30, "L": 1}
    file_num = 1
    for file in os.listdir(os.getcwd() + "\\" + dir_name):
        print(file_num)
        file_num +=1
        # open the file
        with open(os.getcwd() + "\\" + dir_name + "\\" + file) as json_file:
            # read the file's contents
            data = json.load(json_file)
        # iterate over all features in the file
        for feature in data["features"]:
            # query whg to represent the feature as a geoentity
            label = feature["properties"]["text"]
            try:
                entity = geo_entity.GeoEntity(label)
                if entity.place_id not in features_to_variant_dates:
                    features_to_variant_dates[entity.place_id] = {variant:[] for variant in entity.variations}
                centroid = coordinate_geometry.get_centroid(feature["geometry"]["coordinates"])
                distance_margin = fclass_margins[entity.fclass]
                if coordinate_geometry.distance(centroid, entity.geolocation) < distance_margin:
                    # found a label that matches place found from gazetteer
                    map_id = file.strip(".geojson")
                    features_to_variant_dates[entity.place_id][label][map_id] = maps_to_years_dict[map_id]
            except:
                pass
    return features_to_variant_dates
if __name__ == "__main__":
    resulting_json = date_all_variants("random_hundred_geojson_testr_syn")
    with open("features_to_variant_dates.json", "w") as f:
        json.dump(resulting_json, f, ensure_ascii=False)



