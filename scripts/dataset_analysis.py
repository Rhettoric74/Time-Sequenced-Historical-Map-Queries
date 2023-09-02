from extract_year import *
import numpy as np
import pandas as pd
import seaborn as sns
import csv
import matplotlib.pyplot as plt
import config
def plot_years():
    years_list = [float(year) for year in maps_to_years_dict.values() if year.replace(".", "").isnumeric()]
    dataframe = pd.DataFrame({"David Rumsey Collection":years_list})
    #print(dataframe)
    sns.boxplot(x = dataframe["David Rumsey Collection"])
    plt.title("Box Plot of Map Years from David Rumsey Collection")
    plt.xlabel("Year")
    plt.show()
def check_field_sparseness(field, file = config.METADATA_CSV):
    """
    Purpose: check what percentage of rows in a map metadata csv file 
    have a nonempty value in a field
    Parameters: field(string) the header field of the csv to check if it is empty
    """
    with open(file, errors="ignore") as f:
        reader = csv.DictReader(f)
        if field not in reader.fieldnames:
            print("Field does not exist")
            return -1
        rows = 0
        nonempty_rows = 0
        for row in reader:
            rows += 1
            if row[field] != "":
                nonempty_rows += 1
        return nonempty_rows / rows
