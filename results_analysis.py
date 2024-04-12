import json
import os
import numpy as np
results_folder = "scripts/multiword_queries/multiword_query_results/most_populous_multiword_cities"
maps_per_city = []
timespans = []
variants_recognized = []
multiword_maps_per_city = []
for output_file in os.listdir(results_folder):
    print(output_file) 
    with open(results_folder + "/" + output_file) as fp:
        results_dict = json.load(fp)
        num_variants = 0
        earliest_map = float("inf")
        latest_map = - float("inf")
        map_ids = []
        multiword_ids = []
        for name_variant in results_dict[output_file[:output_file.index("_")]]:
            num_variants += 1
            if name_variant in ["largest_bounding_box", "geojson"]:
                continue
            for attestation in results_dict[output_file[:output_file.index("_")]][name_variant]:
                if attestation["map_id"] not in map_ids:
                    map_ids.append(attestation["map_id"])
                    if len(name_variant.split(" ")) > 1:
                        multiword_ids.append(attestation["map_id"])
                if attestation["year"] != None:
                    if attestation["year"] < earliest_map:
                        earliest_map = attestation["year"]
                    if attestation["year"] > latest_map:
                        latest_map = attestation["year"]
        timespans.append(max(0, latest_map - earliest_map))
        maps_per_city.append(len(map_ids))
        multiword_maps_per_city.append(len(multiword_ids))
        print(len(multiword_ids))
        variants_recognized.append(num_variants)
print(np.mean(maps_per_city))
print(np.mean(multiword_maps_per_city))
print(np.mean(timespans))
print(np.mean(variants_recognized))