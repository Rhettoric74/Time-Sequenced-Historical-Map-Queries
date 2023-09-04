# Time-Sequenced Map Queries 
A visualization tool that retrieves time-sequenced maps of a given place. These maps display the different names used by the place across history, 
and how geographic names change over time. Map images provided by the David Rumsey Historical Map Collection, Stanford Libraries
[https://www.davidrumsey.com]
# Overview:
Given a query for the name of a geographic place (e.g. "Istanbul"), this system uses the World Historical Gazetteer [https://whgazetteer.org/] to match that name with
other name variants used for the same place (e.g. "Istambul", "Constantinople", "Byzantium"), and the geographic coordinates of that place. It then retrieves maps that contain accounts of 
those names at those coordinates by searching text labels from maps processed by the **mapKurator** system [https://github.com/machines-reading-maps/map-kurator], which recognizes text labels on scanned maps
and georeferences each label by giving the geocoordinates of the label's bounding box on the map.
# Example output for a query for "Volgograd":
![Example output for a query for "Volgograd"](https://github.com/Rhettoric74/Historical-Maps-Temporal-Analysis/raw/master/assets/StalingradPlottedAndEnlarged.png)



## 0: Prerequisites
- In order to use this system, you must first have a folder of processed map data from the **mapKurator** system on your computer. The **mapKurator** output from the David Rumsey map collection
can be downloaded at [https://s3.msi.umn.edu/rumsey_output/geojson_testr_syn_54119.zip]. More information about this data can be found at [https://github.com/machines-reading-maps/mapkurator-system].
- You must also have downloaded the **luna_omo_metadata_56628_20220724.csv** metadata file for maps from the David Rumsey Collection [https://searchworks.stanford.edu/view/ss311gz1992]. This data is used to get the dates and download URLs of the retrieved maps.
## 1: Creating A Config File
Create a copy of the file `config.py.example` and configure the paths to your data (CSV metadata and
folder of **mapKurator** output files) according to where they are located on your machine. Name this copy 'config.py'.
## 2: Run the Python Notebook Example
- To run 'time_sequenced_map_queries.ipynb' locally, you need to have python 3 installed (I used python 3.8), as well as jupyter.
- Alternatively, you can run this project in google colab [https://colab.research.google.com/].
- Follow the steps in the notebook, and visualize how places change over time.
