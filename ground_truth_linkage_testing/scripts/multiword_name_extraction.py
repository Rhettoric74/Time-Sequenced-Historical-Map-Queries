import os
import sys
sys.path.append(os.pardir)
import json
import random
class AnnotationsSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if not hasattr(self, 'annotations_dict'):
            print("initializing dict")
            self.annotations_dict = {}
    def get_annotations(self, annotations_filepath):
        if annotations_filepath in self.annotations_dict:
            return self.annotations_dict[annotations_filepath]
        else:
            print("loading annotations")
            with open(annotations_filepath, "r") as f:
                self.annotations_dict[annotations_filepath] = json.load(f)
                return self.annotations_dict[annotations_filepath]


def extract_map_data_from_all_annotations(map_filename, annotations_filepath = "icdar24-train-png/annotations.json"):
    map_data = None
    for map in AnnotationsSingleton().get_annotations(annotations_filepath):
        if map["image"] == map_filename:
            return map
    if (map_data == None):
        print(map_filename + " not found")
        return None
def find_multiword_phrases_in_map(map_data):
    names = []
    for group in map_data["groups"]:
        # print(group)
        cur_name = ""
        for label in group:
            cur_name += label["text"] + " "
        if (cur_name.count(" ") >= 2):
            names.append(cur_name[:-1])
    return names
def list_phrases_from_map(map_data):
    """
    This function is different from find_multiword_phrases_in_map in the fact that it includes single word phrases as well
    as multiword phrases. The output format is also a nested list, where each inner list is a list of individual words in 
    a phrase, rather than a list of complete phrases."""
    phrases = []
    for group in map_data["groups"]:
        # print(group)
        cur_phrase = []
        for label in group:
            cur_phrase.append(label["text"])
        phrases.append(cur_phrase)
    return phrases
def remove_groupings_from_annotations(map_annotations_dict):
    removed_dict_annotations = {"image":map_annotations_dict["image"], "groups":[]}
    for group in map_annotations_dict["groups"]:
        for label in group:
            removed_dict_annotations["groups"].append(label)
    return removed_dict_annotations
def list_all_word_labels(annotations_dict):
    word_labels = []
    for group in annotations_dict["groups"]:
        for label in group:
            word_labels.append(label["text"])
    return word_labels

def multiword_name_extraction_from_map(map_filename, data_filepath = "icdar24-train-png/annotations.json"):
    map_data = extract_map_data_from_all_annotations(map_filename, data_filepath)
    return find_multiword_phrases_in_map(map_data)
if __name__ == "__main__":
    """ maps_sampled = ["5797073_h2_w9.png", "8817002_h4_w4.png","0068010_h2_w7.png","0071008_h3_w7.png","7807309_h6_w7.png","7911000_h2_w2.png","7810246_h7_w2.png","8387002_h14_w19.png","6855137_h9_w11.png","7834013_h5_w5.png"]
    random_map_sample = ['0065011_h4_w2.png', '5797073_h2_w9.png', '6777000_h7_w4.png', '7809060_h3_w12.png', '6917077_h11_w2.png', '0073018_h2_w7.png', '8105000_h3_w4.png', '6350035_h6_w2.png', '6855036_h5_w13.png', '0103002_h3_w4.png']
    for map_name in random_map_sample:
        print(multiword_name_extraction_from_map(map_name)) #,"C:/Users/rhett/Downloads/icdar24-val-png/icdar24-val-png/annotations.json"))
    print(multiword_name_extraction_from_map('5175001_h2_w4.png'))
    print(extract_map_data_from_all_annotations('5175001_h2_w4.png')) """
    """ enough_multiword_phrases = []
    counter = 0
    for file in os.listdir("icdar24-train-png/train_images"):
        counter += 1
        print(counter)
        THRESHOLD = 20
        names_list = multiword_name_extraction_from_map(file)
        if len(names_list) >= THRESHOLD:
            enough_multiword_phrases.append(file)
    print(len(enough_multiword_phrases))
    print(random.sample(enough_multiword_phrases, 10)) """
    words_list = list_all_word_labels(extract_map_data_from_all_annotations("7058000_h12_w23.png"))
    random.shuffle(words_list)
    print(words_list)

