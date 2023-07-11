import feature_query
import extract_year
import whg_requests

def find_variations(place_name):
    """
    Purpose: Find the variations of a place name based on the WHGazetteer index endpoint that has the most variations.
    i.e if there are multiple places with the same name, take the one with the most variations.
    Parameters: place_name, the name of the place to find variations of.
    Returns: a tuple containing the fclass and a list of variations of the place name, 
    taken from the place entity with that name which has the most variants.
    example: ("p", ["Mexico City", ...])
    """
    variations = []
    fclasses = whg_requests.find_fclasses(place_name)
    most_variations_fclass = None
    for fclass in fclasses:
        high_variance = whg_requests.most_variants(whg_requests.place_request_index(place_name, fclass))
        if len(high_variance["properties"]["variants"]) > len(variations):
            most_variations_fclass = fclass
            variations = high_variance["properties"]["variants"]
    return (most_variations_fclass, variations)
def link_dates(variations_list):
    """
    Purpose: link a list of variations to the dates of the maps they appear in.
    Parameters: variations_list, a list of variations to link to dates.
    Returns: a dictionary mapping variations to dates.
    """
    variations_to_dates = {}
    for variation in variations_list:
        print(variation)
        results = feature_query.feature_query("random_hundred_geojson_testr_syn", variation)
        results_ids = [result.strip(".geojson") for result in results]
        dated_results = extract_year.extract_years(results_ids)
        variations_to_dates[variation] = dated_results
    return variations_to_dates
if __name__ == "__main__":
    istanbul_variations = find_variations("Paris")
    print(istanbul_variations)
    print(link_dates(istanbul_variations))