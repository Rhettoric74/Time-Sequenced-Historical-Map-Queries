import sys
import os
sys.path.append(os.path.dirname("config.py"))
sys.path.append("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/scripts/knowledge_graphs")
from scripts.variation_stats import *
from place_node import PlaceNode

class NameSplit:
    def __init__(self, purity_gain, split_index, split_threshold = None, name_variant = ""):
        self.purity_gain = purity_gain
        self.split_index = split_index
        self.split_threshold = split_threshold
        self.name_variant = name_variant
    def __repr__(self):
        return self.name_variant + ": less than " + str(self.split_threshold)
def get_split_threshold(accounts):
    # try different numbers of n splits
    # for each, try splitting thresholds between n pairs of points. 
    # for each, evaluate the impurities of the split and try to maximize the purity
    best_splits = NameSplit(0,0)
    # try different numbers of n splits
    parent_purity = check_accounts_purity(accounts)
    
    for i in range(1, len(accounts) -1):
        before_split = accounts[:i]
        after_split = accounts[i:]
        before_purity = check_accounts_purity(before_split)
        after_purity = check_accounts_purity(after_split)
        purity_gain = (before_purity[1] * i / len(accounts)) + (after_purity[1] * (len(accounts) - i) / len(accounts)) - parent_purity[1]
        if purity_gain >  best_splits.purity_gain:
            best_splits.purity_gain = purity_gain
            best_splits.split_index = i
            best_splits.name_variant = before_purity[0]
    if best_splits.split_index == 0:
        best_splits.split_threshold = accounts[0].year
    else:
        best_splits.split_threshold = (accounts[best_splits.split_index - 1].year + accounts[best_splits.split_index].year) / 2
    return best_splits

            

def check_accounts_purity(accounts_list):
    """
    Purpose: given a list of named accounts, return the most common name and the ratio of accounts with that name
    parameters: accounts_list, a list of NamedAccount objects
    returns: a tuple containing first the name of the most common account in the list, and then the purity
    of that name appearing in the list (percentage of accounts in the list with that name)"""
    variant_name_frequencies = {}
    for account in accounts_list:
        if account.variant_name not in variant_name_frequencies:
            variant_name_frequencies[account.variant_name] = 1
        else:
            variant_name_frequencies[account.variant_name] += 1
    frequency_tuples = variant_name_frequencies.items()
    highest_frequency_variant_name = ("", - float("inf"))
    for frequency_tuple in frequency_tuples:
        if frequency_tuple[1] > highest_frequency_variant_name[1]:
            highest_frequency_variant_name = frequency_tuple
    # turn frequency into its percentage of the whole accounts list
    return (highest_frequency_variant_name[0], highest_frequency_variant_name[1] / len(accounts_list))
def check_accounts_impurity(accounts_list, variant_name):
    """
    Purpose: determine the impurity of an accounts list, meaning the ratio of accounts
    that do not match the provided name
    Parameters: accounts_list, a list of NamedAccount objects,
    variant_name, (string), the name of the variant you want to check the percentage of accounts that
    do not match
    returns: float, # of accounts with a different variant name / length of accounts_list

    """
    non_matches = 0
    for account in accounts_list:
        if account.variant_name != variant_name:
            non_matches += 1
    return non_matches / len(accounts_list)
if __name__ == "__main__":
    dirname = "french_cities"
    with open("analyzed_features/french_cities.txt", "r", encoding="utf-8") as fp:
        french_cities_list = fp.readlines()
    french_cities_list = [city_name.strip("\n") + "_dates.json" for city_name in french_cities_list]
    for accounts_filename in french_cities_list:
        pn = PlaceNode("analyzed_features/" + dirname + "/" + accounts_filename)
        accounts_list = pn.list_accounts_in_order(True, 60)
        if len(accounts_list) > 5 or (len(accounts_list) > 0 and check_accounts_purity(accounts_list)[1] < 0.9):
            plot_named_accounts(accounts_list)
            print(accounts_filename)
            print(get_split_threshold(accounts_list))