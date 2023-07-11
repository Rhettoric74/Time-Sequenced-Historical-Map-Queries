from extract_year import *
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
years_list = [float(year) for year in maps_to_years_dict.values() if year.replace(".", "").isnumeric()]
dataframe = pd.DataFrame({"David Rumsey Collection":years_list})
#print(dataframe)
sns.boxplot(x = dataframe["David Rumsey Collection"])
plt.title("Box Plot of Map Years from David Rumsey Collection")
plt.xlabel("Year")
plt.show()