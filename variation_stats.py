import json
import matplotlib.pyplot as plt

class NamedAccount:
    def __init__(self, variant_name, year, map_id):
        self.variant_name = variant_name
        self.year = year
        self.map_id = map_id
    def __repr__(self):
        return str(self.year) + ": " + str(self.variant_name)
    def __lt__(self, other):
        return self.year < other.year
def list_accounts_in_order(filename):
    """
    Purpose: create a list of all of the named, dated accounts of a geographic entity stored in a file
    Parameters: filename, the name of the file containing the changes, based on the output of a dated_query
    returns: a sorted list of all NamedAccount objects sorted by year
    """
    with open(filename) as fp:
        accounts_list = []
        obj = json.load(fp)
        for city in obj.keys():
            for variant in obj[city].keys():
                for id, year in obj[city][variant].items():
                    accounts_list.append(NamedAccount(variant, year, id))
        accounts_list.sort()
        return accounts_list
def plot_named_accounts(filename):
    accounts = list_accounts_in_order(filename)
    years , height_vals = [(account.year, 1) for account in accounts]

    # Labels and colors
    labels = ['A', 'B', 'C', 'D', 'E']
    colors = ['red', 'green', 'blue', 'orange', 'purple']

    # Plotting
    plt.scatter(years, height_vals, c=colors)

    # Adding labels to each point
    for i, label in enumerate(labels):
        plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

    # Axes labels and title
    plt.xlabel('Map dates')
    plt.title('Plot of Points in a Line with Labels and Colors')

    # Display the plot
    plt.show()




if __name__ == "__main__":
    cities = ["tokyo", "mumbai", "oslo", "kinshasa", "tallinn", "dushanbe", "ottawa", "istanbul", "volgograd", "leningrad", "nashville", "saigon", "yekaterinburg"]
    for city in cities:
        accounts = list_accounts_in_order("analyzed_cities/" + city + "_dates.json")
        print(accounts)
        print(len(accounts))
        