from match_countries_to_map_ids import *
import random
import matplotlib.pyplot as plt
def get_random_map_sample(sample_size):
    chosen_feature = random.choice(list(countries_to_ids_dict.keys()))
    ids_sample = random.sample(countries_to_ids_dict[chosen_feature], sample_size)
    return chosen_feature, ids_sample
def plot_country_map_lists():
    countries, lengths = zip(*[(country_to_ids[0], len(country_to_ids[1])) for country_to_ids in countries_to_ids_dict.items()])
    
    plt.bar(countries, lengths, color ='maroon')
 
    plt.xlabel("country names")
    plt.ylabel("No. of maps matched with that country")
    plt.title("Students enrolled in different courses")
    plt.show()
if __name__ == "__main__":
    print(get_random_map_sample(10))
    plot_country_map_lists()

