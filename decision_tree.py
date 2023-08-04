from feature_query import *
from variation_stats import NamedAccount
class VariantNode:
    """
    Purpose: Object representing a place name variant and the time interval associated with it
    Parameters: variant_name, a string containing the variant place name, dated_maps_dict, a dictionary mapping 
    map_ids containing the variant with their dates
    
    Returns: A new VariantNode representing the variant place name and the times it was used"""
    def __init__(self, feature_name = None, threshold = None, left = None, right = None, value = None):
        self.feature_name = feature_name
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
    def __repr__(self):
        """
        Purpose: Override __repr__ method for use in debugging
        Lists variant name, followed by earliest_reference and latest_reference, separated by newlines
        """
        return str(self.feature_name) + "\n" + str(self.threshold) + "\n"

class DecisionTreeRegressor:
    def __init__(self, min_samples_split = 2, max_depth = 5):
        self.root = None
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
    def build_tree(self, accounts_dataset, cur_depth = 0):
        """
        Purpose: Construct a decision tree based on a given dataset of named accounts
        Parameters: accounts_dataset, a dictionary mapping geo_entities to lists of NamedAccounts of that feature
        returns: None, builds a decision tree from the data
        """
        max_sample_length = max([len(accounts_list) for accounts_list in accounts_dataset.values()])
        num_features = len(accounts_dataset.keys())
        if max_sample_length >= self.min_samples_split and cur_depth < self.max_depth:
            best_split = self.get_best_split(accounts_dataset, max_sample_length, num_features)
            if best_split["var_red"] > 0:
                left_subtree = self.build_tree(best_split["remaining_features"], cur_depth+1)
                # recur right
                right_subtree = self.build_tree(best_split["remaining_features"], cur_depth+1)
                
if __name__ == "__main__":
    """
    Note: Searching the entire David Rumsey database takes roughly 1 hour
    """