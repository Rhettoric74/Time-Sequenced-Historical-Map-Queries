import json
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz

class NamedAccount:
    def __init__(self, variant_name, year, map_id, fuzzy_ratio = None, overlap_confidence = 1, img_coordinates = None):
        self.variant_name = variant_name
        self.year = year
        self.map_id = map_id
        self.fuzzy_ratio = fuzzy_ratio
        self.overlap_confidence = 1
        self.img_coordinates = img_coordinates
    def __repr__(self):
        return str(self.year) + ": " + str(self.variant_name)
    def __lt__(self, other):
        return self.year < other.year
def list_accounts_in_order(filename, combine_similar_variants = False, similarity_threshold = 85):
    """
    Purpose: create a list of all of the named, dated accounts of a geographic entity stored in a file, sorted by year.
    Parameters: filename, the name of the file containing the changes, based on the output of a dated_query
            combine_similar_variants (boolean) whether to count variant names that are very similar to others as the same
            variant.
            similarity_threshold (1 - 100) percent similarity needed to consider two variants the same
    returns: a sorted list of all NamedAccount objects sorted by year
    """
    with open(filename) as fp:
        accounts_list = []
        obj = json.load(fp)
        if combine_similar_variants == True:
            obj = combine_similar_variant_names(obj, similarity_threshold)
        for city in obj.keys():
            print(city)
            for variant in obj[city].keys():
                for account in obj[city][variant]:
                    print(account)
                    year = account["year"]
                    id = account["map_id"]
                    fuzzy_ratio = None
                    if "fuzzy_ratio" in account:
                        fuzzy_ratio = account["fuzzy_ratio"]
                    overlap_confidence = None
                    if "overlap_confidence" in account:
                        overlap_confidence = account["overlap_confidence"]
                    if "img_coordinates" in account:
                        img_coordinates = account["img_coordinates"]
                    accounts_list.append(NamedAccount(variant, year, id, fuzzy_ratio, overlap_confidence, img_coordinates))
        accounts_list.sort()
        return accounts_list
def combine_similar_variant_names(json_obj, similarity_threshold = 85):
    """
    Purpose: Correct variant names that are very similar to each other to be the most common similar name.
    Parameters: json_obj, a dictionary obtained from an analyzed city file
                similarity_threshold, the percent similarity two names must exceed in order for them to be 
                treated as the same.
    Returns: A new dictionary where all similar names are combined into the most common such similar name. 
    """
    combined_dict = {}
    for city in json_obj.keys():
        combined_dict[city] = {}
        # create a list sorting the variant names by how many accounts they have
        variants_by_popularity = [(variant, len(list(account.keys()))) for variant, account in json_obj[city].items()]
        variants_by_popularity = sorted(variants_by_popularity, key = lambda x : x[1], reverse=True)
        variants_by_popularity = [item[0] for item in variants_by_popularity]
        # combine less common variant names into larger ones if they are similar
        while len(variants_by_popularity) > 0:
            # get the most common variant left in the list
            most_common = variants_by_popularity.pop(0)
            accounts = json_obj[city][most_common]
            # look through the rest of the list for similar variants
            i = 0
            while i < len(variants_by_popularity):
                variant = variants_by_popularity[i]
                if fuzz.ratio(variant, most_common) > similarity_threshold:
                    accounts.update(json_obj[city][variant])
                    variants_by_popularity.remove(variant)
                else:
                    i += 1
            combined_dict[city][most_common] = accounts
    return combined_dict




def plot_named_accounts(accounts):
    """
    Purpose: Visualize a timeline of named accounts of a place, by generating a plot of years labeled with names
    Parameters: accounts, a list of NamedAccount objects to graph
    Returns: None, creates a pyplot showing dates on the x-axis, labeling variant names on the y axis.
    """
    variant_names = [account.variant_name for account in accounts]
    years = [account.year for account in accounts]
    # assign each variant name a numerical value to graph in the y axis
    variations_to_heights_dict = {}
    cur_highest = 1
    height_values = []
    for account in accounts:
        if account.variant_name not in variations_to_heights_dict:
            variations_to_heights_dict[account.variant_name] = cur_highest
            height_values.append(cur_highest)
            cur_highest += 1
        else:
            height_values.append(variations_to_heights_dict[account.variant_name])
    
    # Plotting
    plt.scatter(years, height_values)

    # Adding labels to each point
    left_edge = min(years)
    for variant in variations_to_heights_dict:
        plt.annotate(variant, (left_edge, variations_to_heights_dict[variant]))

    # Axes labels and title
    plt.xlabel('Map dates')
    plt.ylabel("Name Variations")
    plt.title('Plot of Named Accounts over the years')

    # Display the plot
    plt.show()




        