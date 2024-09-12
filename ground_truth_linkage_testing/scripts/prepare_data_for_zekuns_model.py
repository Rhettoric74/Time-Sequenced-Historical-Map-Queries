from map_graph import MapGraph
import json
import os
import pickle
from multiword_name_extraction import list_phrases_from_map
def prepare_data_for_zekuns_model(output_dir, annotations_filepath):
    with open(annotations_filepath) as f:
        annotated_data = json.load(f)
        for map_annotation in annotated_data:
            words_list = []
            bboxes_list = []
            mg = MapGraph(map_annotation["image"], "annotations", annotations_filepath=annotations_filepath)
            for node in mg.nodes:
                words_list.append(node.text)
                x_center, y_center = node.minimum_bounding_box[0]
                width, height = node.minimum_bounding_box[1]
                bboxes_list.append([[x_center - (width / 2), y_center - (height / 2)], [x_center - (width / 2), y_center + (height / 2)], [x_center + (width / 2), y_center - (height / 2)], [x_center + (width / 2), y_center + (height / 2)]])
            word_list_path = output_dir + "/word_list/"
            if not os.path.exists(word_list_path):
                os.makedirs(word_list_path)
            coords_list_path = output_dir + "/word_coords_list/"
            if not os.path.exists(coords_list_path):
                os.makedirs(coords_list_path)
            phrases_list_path = output_dir + "/phrases_list/"
            if not os.path.exists(phrases_list_path):
                os.makedirs(phrases_list_path)
            with open(word_list_path  + map_annotation["image"][:-4] + ".pkl", 'wb') as words_outfile:
                pickle.dump(words_list, words_outfile)
            with open(coords_list_path  + map_annotation["image"][:-4] + ".pkl", 'wb') as centroids_outfile:
                pickle.dump(bboxes_list, centroids_outfile)
            with open(phrases_list_path  + map_annotation["image"][:-4] + ".pkl", 'wb') as phrases_outfile:
                phrases_list = list_phrases_from_map(map_annotation)
                print(phrases_list)
                pickle.dump(phrases_list, phrases_outfile)
            

if __name__ == "__main__":
    """ with open("icdar24-test-png-annotations.json", "r") as annotations_file:
        annotated_data = json.load(annotations_file)
        for map_annotation in annotated_data:
            map_annotation["image"] = map_annotation["image"].strip("rumsey/test/")
        with open("img-names-updated_icdar24-test-png-annotations.json", "w") as fw:
            json.dump(annotated_data, fw) """
    prepare_data_for_zekuns_model("test_data_for_zekuns_model", "img-names-updated_icdar24-test-png-annotations.json")

