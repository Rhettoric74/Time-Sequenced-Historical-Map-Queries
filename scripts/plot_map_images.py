import sys
import os
sys.path.append(os.path.dirname("config.py"))
import extract_map_images
from matplotlib import pyplot as plt
import mplcursors
import math

def divide_by_decade(named_accounts):
    """Purpose: divide a list of named accounts by decade, so that  maps in the same decade can be plotted in the same column
    Parameters: named_accounts, a list (nonempty) of NamedAccount objects, sorted by year.
    Returns: a tuple formatted as (max_number_in_one_decade, decade_indices_to_named_accounts_dict)
    """
    oldest_decade = int(named_accounts[0].year) // 10
    decade_indices_to_named_accounts = {}
    most_in_decade = 0
    for account in named_accounts:
        decade_index = int(account.year) // 10 - oldest_decade
        if decade_index not in decade_indices_to_named_accounts:
            decade_indices_to_named_accounts[decade_index] = [account]
        else:
            decade_indices_to_named_accounts[decade_index].append(account)
        if len(decade_indices_to_named_accounts[decade_index]) > most_in_decade:
            most_in_decade = len(decade_indices_to_named_accounts[decade_index])
    return most_in_decade, decade_indices_to_named_accounts



def plot_image_accounts_list(images, named_accounts):
    """
    Purpose: Plot cropped map images in a timeline
    Parameters: images, an array of openCV images to display, named_accounts, the corresponding named_accounts list.
    Returns: none, plots the images. 
    """
    num_decades = math.ceil((named_accounts[-1].year - named_accounts[0].year) / 10) + 1
    print(num_decades)
    rows, decades_indices_to_accounts = divide_by_decade(named_accounts)
    print(decades_indices_to_accounts)
    fig, axes = plt.subplots(nrows=rows, ncols=num_decades, figsize=(12, 8))  # Adjust figsize as needed

    # Plot the images on the subplots
    i = 0
    for index, accounts in decades_indices_to_accounts.items():
        for row in range(len(accounts)):
            if i < len(images):
                axes[row, index].imshow(images[i], cmap='gray')
                axes[row, index].set_title(str(int(named_accounts[i].year)))
                axes[row, index].text(0.5, -0.1, named_accounts[i].variant_name, ha='center', va='center', transform=axes[row, index].transAxes)
                i += 1
            else:
                print("unexpected index i")

    for i in range(num_decades):
        for j in range(rows):
            axes[j, i].axis('off')
    # Create a cursor
    cursors = mplcursors.cursor()

    # Function to handle the click event
    def on_click(sel):
        # Get the coordinates of the click
        image = sel.artist
        image = image.get_array()
        
        
        

        plt.figure()
        plt.imshow(image)
        plt.axis('off')
        plt.show()

        # Connect the click event to the function
    cursors.connect("add", on_click)
    plt.show()
if __name__ == "__main__":
    """
    To visualize query outputs, run this file while passing in the name of the query a command line argument.
    Examples:  
        python3 scripts/plot_map_images.py "Oslo"
        python3 scripts/plot_map_images.py "world_capitals" "Oslo"
    """
    file_path = ""
    if len(sys.argv) < 2:
        print("Usage: Please specify the name of the place query that you want to plot")
    if len(sys.argv) == 2:
        file_path = "input_queries/" + sys.argv[1] + "_dates.json"
    if len(sys.argv) == 3:
        file_path = sys.argv[1] + "/" + sys.argv[2] + "_dates.json"
    
    # If you only want to see a limited number of maps, specify here the maximum number of maps to display
    # and a random sample of that number of maps will be plotted
    # Leave this as none to see all resulting maps
    max_sample = 20

    # to instead see a plotted output for a previous query for "Oslo", uncomment the next line
    # query_results_path = "world_capitals/" + "Oslo" + "_dates.json"
    images, named_accounts = extract_map_images.extract_images_from_accounts_file("C:/Users/rhett/code_repos/Time-Sequenced-Historical-Map-Queries/analyzed_features/" + file_path, max_sample, True)
    plot_image_accounts_list(images, named_accounts)
    
    
