from feature_query import *

class VariantNode:
    """
    Purpose: Object representing a place name variant and the time interval associated with it
    Parameters: variant_name, a string containing the variant place name, dated_maps_dict, a dictionary mapping 
    map_ids containing the variant with their dates
    
    Returns: A new VariantNode representing the variant place name and the times it was used"""
    def __init__(self, variant_name, dated_maps_dict):
        self.variant_name = variant_name
        self.dates_list = [float(date) for date in dated_maps_dict.values() if date != ""]
        self.dates_list.sort()
        self.earliest_reference = self.dates_list[0]
        self.latest_reference = self.dates_list[-1]
    def __repr__(self):
        """
        Purpose: Override __repr__ method for use in debugging
        Lists variant name, followed by earliest_reference and latest_reference, separated by newlines
        """
        return str(self.variant_name) + "\n" + str(self.earliest_reference) + "\n" + str(self.latest_reference)

class DecisionTree:
    def __init__(self, features_list, dirname = "random_hundred_geojson_testr_syn"):
        self.features_list = features_list
        self.variant_nodes = []
        for feature in self.features_list:
            query_result = dated_query(dirname, feature)
            print(query_result)
            for variant in query_result.keys():
                self.variant_nodes.append(VariantNode(variant, query_result[variant]))
if __name__ == "__main__":
    """
    Note: Searching the entire David Rumsey database takes roughly 1 hour
    """
    decision_tree = DecisionTree(["Democratic Republic of the Congo"], "geojson_testr_syn")
    for node in decision_tree.variant_nodes:
        print(node)