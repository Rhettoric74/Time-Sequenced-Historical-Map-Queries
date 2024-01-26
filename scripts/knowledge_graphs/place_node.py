import json
import sys
import os
sys.path.append(os.getcwd()  + "/knowledge_graphs")
sys.path.append(os.getcwd())
from name_variant_node import NameVariantNode
from geo_entity import GeoEntity
from variation_stats import NamedAccount
import coordinate_geometry
from fuzzywuzzy import fuzz

class PlaceNode(GeoEntity):
    def __init__(self, attestations_file):
        self.name_variant_nodes = []
        # store pointers to nearby place nodes here
        self.neighbors = []
        with open(attestations_file, "r") as fp:
            json_object = json.load(fp)
            # access the inner dict of attestations
            name = list(set(json_object.keys()).difference({"geojson", "largest_bounding"}))[0]
            print(name)
            attestations_dict = json_object[name]
            #print(attestations_dict)
            for name_variant in attestations_dict:
                if name_variant not in ["geojson", "largest_boundin"]:
                    node = NameVariantNode(name_variant)
                    node.from_json(attestations_dict[name_variant])
                    self.name_variant_nodes.append(node)
            if "geojson" not in json_object:
                super().__init__(name)
            else:
                # use geojson from attestations file to skip querying WHG every time
                super().__init__()
                self.from_geojson(json_object["geojson"])
            if "largest_bounding" in json_object:
                self.largest_bounding = json_object["largest_bounding"]
        
    def __str__(self):
        return super().__str__() + "\n".join([str(name_variant_node) for name_variant_node in self.name_variant_nodes])
    def distance(self, other):
        return coordinate_geometry.haversine_distance(coordinate_geometry.get_centroid(self.largest_bounding), coordinate_geometry.get_centroid(other.largest_bounding))
    def combine_similar_variants(self, similarity_threshold = 85):
        # sort the variants by number of attestations
        self.name_variant_nodes = [(variant, len(variant.attestations)) for variant in self.name_variant_nodes]
        self.name_variant_nodes = sorted(self.name_variant_nodes, key = lambda x : x[1], reverse=True)
        self.name_variant_nodes = [item[0] for item in self.name_variant_nodes]
        remaining_nodes = []
        # combine less common variant names into larger ones if they are similar
        while len(self.name_variant_nodes) > 0:
            # get the most common variant left in the list
            most_common = self.name_variant_nodes.pop(0)
            attestations = most_common.attestations
            # look through the rest of the list for similar variants
            i = 0
            remaining_nodes.append(most_common)
            while i < len(self.name_variant_nodes):
                variant = self.name_variant_nodes[i]
                ratio = fuzz.ratio(variant.name_variant, most_common.name_variant)
                if ratio > similarity_threshold:
                    for attestation in variant.attestations:
                        attestation.fuzzy_ratio *= (ratio / 100)
                    attestations += variant.attestations
                    self.name_variant_nodes.remove(variant)
                else:
                    i += 1
        self.name_variant_nodes = remaining_nodes
    def list_accounts_in_order(self, combine_similar_variants = False, similarity_threshold = 85):
        if combine_similar_variants:
            self.combine_similar_variants(similarity_threshold)
        accounts_list = []
        for name_variant_node in self.name_variant_nodes:
            for attestation in name_variant_node.attestations:
                accounts_list.append(NamedAccount(name_variant_node.name_variant, attestation.year, attestation.map_id, attestation.fuzzy_ratio))
        accounts_list.sort()
        return accounts_list

if __name__ == '__main__':
    pn = PlaceNode("C:/Users/rhett/UMN_Github/HistoricalMapsTemporalAnalysis/analyzed_features/input_queries/Berlin_dates.json")
    print(len(pn.name_variant_nodes))
    print(pn)
    for name_variant_node in pn.name_variant_nodes:
        print(name_variant_node.name_variant, name_variant_node.get_range(0.96))
    


        