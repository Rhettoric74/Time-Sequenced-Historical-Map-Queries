import json
import random
import geo_entity
from coordinate_geometry import get_centroid, distance
import extract_year
import copy
import numpy as np
import csv

def add_coordinates(filename):
    """
    Purpose: Automatically georefrence places provided in a list of name changes using the WHG API
    Parameters: filename, the name of a json file describing name changes to add coordinates to
    Returns: None, modifies the json file to include the names"""
    with open(filename) as fp:
        json_list = json.load(fp)
        for change in json_list:
            referenced = False
            if change["coords"] == [[],[]]:
                if not isinstance(change["new_name"], list):
                    try:
                        entity = geo_entity.GeoEntity(change["new_name"])
                        change["coords"] = entity.geolocation
                        referenced = True
                    except Exception as e:
                        print(e)
                        print(change["new_name"], "not in whg dataset")
                if not referenced:
                    try:
                        entity = geo_entity.GeoEntity(change["old_name"])
                        change["coords"] = entity.geolocation
                        referenced = True
                    except:
                        print(change["old_name"], "not in whg dataset")
    with open(filename, "w") as fw:
        json.dump(json_list, fw, indent=2)

        



            
class NameChange:
    """
    Purpose: Class for representing name changes as nodes in Binary search trees
    """
    def __init__(self, coords, old_name, new_name, date):
        self.coords = coords
        self.old_name = old_name
        self.new_name = new_name
        self.date = int(date)
        self.left = None
        self.right = None
    def remove_neighbors(self):
        self.right = None
        self.left = None
    def __lt__(self, other):
        return self.date < other.date
    def __repr__(self):
        return str(self.date) + ": " + str(self.old_name) + " -> " + str(self.new_name)
    def insert(self, new_decision):
        if self.date <= new_decision.date:
            if self.right == None:
                self.right = new_decision
            else:
                self.right.insert(new_decision)
        else: 
            if self.left == None:
                self.left = new_decision
            else:
                self.left.insert(new_decision)
    def in_order_print(self):
        if self.left != None:
            self.left.in_order_print()
        print(self)
        if self.right != None:
            self.right.in_order_print()
def read_changes_list_from_json(filename):
    """
    Purpose: Read the place name changes from a json file and turn them into NameChange objects
    Parameters: filename (string) file to read from
    Returns: List of Name changes with all the changes in the file
    """
    with open(filename) as fp:
        json_list = json.load(fp)
        changes_list = [NameChange(change["coords"], change["old_name"], 
                                   change["new_name"], change["change_date"]) for change in json_list]
        return changes_list
def read_changes_list_from_csv(filename):
    """
    Purpose: Read the place name changes from a csv file and turn them into NameChange objects
    Parameters: filename (string): file to read from, 
    must be formatted with fieldnames
    old_name, new_name, change_date
    ...
    All coordinates are automatically matched using WHG dataset
    Returns: List of Name changes with all the changes in the file
    """
    with open(filename) as fp:
        reader = csv.DictReader(fp)
        changes_list = []
        for row in reader:
            # get coordinates of the location
            coords = [float(row["longitude"]), float(row["latitude"])]
            changes_list.append(NameChange(coords, row["old_name"], row["new_name"], int(row["change_date"])))
    return changes_list

def create_csv_name_changes_from_json(json_filename, csv_filename):
    """
    Purpose: Create a csv file representing a list of name changes given by a json file
    Parameters: json_filename, source file of the name changes, csv_filename, the name of the csv file to output."""
    with open(json_filename) as fp:
        with open(csv_filename, "w") as fw:
            data = json.load(fp)
            fw.write("old_name,new_name,change_date,longitude,latitude\n")
            for change in data:
                line = ",".join([str(change["old_name"]), str(change["new_name"]), str(change["change_date"]), str(change["coords"][0]), str(change["coords"][1])])
                fw.write(line + "\n")

def find_changes_on_map(changes_list, map_id):
    """
    Purpose: Given a list of changes and a map, identify which named places appear on the map
    Parameters: changes_list, a list of NameChange objects; map_id, the id of the map file
    Returns: list containing all of the changes in changes_list that are on the map
    """
    changes_on_map = []
    with open("geojson_testr_syn/" + str(map_id) + ".geojson", "r") as f:
        map_data = json.load(f)
        for change in changes_list:
            for entity in map_data["features"]:
                if distance(get_centroid(entity["geometry"]["coordinates"]), change.coords) < 20:
                    # try to match name of change with name on the map
                    name = entity["properties"]["text"].upper()
                    if name == str(change.old_name).upper() or name == str(change.new_name).upper():
                        changes_on_map.append(change)
                        break
    return changes_on_map
                    

class DecisionTree:
    def __init__(self, changes_list):
        """Purpose: Class for generating decision trees from a json list of NameChange objects"""
        random.shuffle(changes_list)
        self.head = changes_list[0]
        for change in changes_list[1:]:
            try:
                self.head.insert(change)
            except:
                print(change)
                break
    def predict(self, map_id):
        """
        Purpose: Use decision tree to predict the date of a map with the given id
        Parameters: map_id, the id of the map file to date
        Returns: a tuple representing the range of possible dates, of the form:
            (earliest_date, latest_date)
        """
        earliest = - float("inf")
        latest = float("inf")
        current_node = self.head
        with open("geojson_testr_syn/" + str(map_id) + ".geojson", "r") as f:
            map_data = json.load(f)
        
        while current_node != None:
            # search for the new name in the map
            name_version_found = False
            for entity in map_data["features"]:
                name = entity["properties"]["text"].upper()
                if name == str(current_node.old_name).upper():
                    latest = current_node.date
                    current_node = current_node.left
                    name_version_found = True
                    break
                elif name == str(current_node.new_name).upper():
                    earliest = current_node.date
                    current_node = current_node.right
                    name_version_found = True
                    break
            if not name_version_found:
                # move right if neither version of the name was found, this should never happen
                print(current_node, "not found")
                earliest = current_node.date
                current_node = current_node.right

                
            

        return (earliest, latest)

class RandomForest:
    def __init__(self, changes_list, forest_size = 100):
        self.decision_trees = []
        for _ in range(forest_size):
            self.decision_trees.append(DecisionTree(copy.deepcopy(changes_list)))
    def predict(self, map_id):
        earliest_predictions =  []
        latest_predictions = []
        for tree in self.decision_trees:
            prediction = tree.predict(map_id)
            earliest_predictions.append(prediction[0])
            latest_predictions.append(prediction[1])
        return (np.median(earliest_predictions), np.median(latest_predictions))



    
        
    
    
if __name__ == "__main__":
    create_csv_name_changes_from_json("world_globes_data.json", "world_globes_data.csv")
    with open("very_dateable_map_ids.csv") as f:
        map_ids_list = f.read().split(", ")
        map_ids_list = [id[1:-1] for id in map_ids_list]
    map_ids_dict = extract_year.extract_years(map_ids_list)
    all_changes_list = read_changes_list_from_csv("world_globes_data.csv")
    print(len(all_changes_list))
    changes_list = []
    # remove changes that contain multiple words in their names
    for change in all_changes_list:
        if change.new_name.count(" ") == 0 and change.old_name.count(" ") == 0:
            changes_list.append(change)
    print(len(changes_list))
    date_predictions = {}
    within_range = 0
    dating_attempts = 0
    ranges_list = []
    for id in map_ids_dict.keys():
        print(id)
        # clear the neighbor nodes added to each decision in the previous tree
        for change in changes_list:
            change.remove_neighbors()
        on_map = find_changes_on_map(changes_list, id)
        if len(on_map) > 3:
            dating_attempts += 1
            rf = RandomForest(on_map)
            prediction = rf.predict(id)
            true_year = float(map_ids_dict[id])
            if true_year <= prediction[1] and true_year >= prediction[0]:
                within_range += 1
            ranges_list.append(prediction[1] - prediction[0])
            print(prediction, true_year)
            date_predictions[id] = prediction
    print(within_range / dating_attempts)
    print(np.median(ranges_list))