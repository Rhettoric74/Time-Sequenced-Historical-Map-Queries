from map_graph import prims_mst, FeatureNode
from compare_linkages import *
from analyze_recall_data import random_forest_regressor, load_data_from_csv
import pickle
import json
import multiprocessing as mp
import random
import numpy as np
K = 5
def load_folds_from_folder(dirname = "cross_validation_images"):
    folds = []
    for i in range(K):
        with open(dirname + "/fold_" + str(i) + "/train_map_ids.pkl", "rb") as train_maps_file:
            with open(dirname + "/fold_" + str(i) + "/test_map_ids.pkl", "rb") as test_maps_file:
                cur_fold = {"train":pickle.load(train_maps_file), "test":pickle.load(test_maps_file)}
                print(len(cur_fold["train"]), len(cur_fold["test"]))
                folds.append(cur_fold)
    return folds
def get_random_weights_sample(sample_size = 100):
    return [[random.random() * 2, random.random() * 2, random.random() * 2] for i in range(sample_size)]
def collect_recall_data_weights(fold_name, fold_train_set, weights, annotations_filepath = "all_annotations.json"):
    name = "weights_" + format(weights[0], ".2f") + "_" + format(weights[1], ".2f") + "_" + format(weights[2], ".2f")
    lm = LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction(weights))
    map_list_compare_linkages(fold_train_set, name, annotations_filepath, lm, "cross_validation_results/" + fold_name + "/" + name + ".json")
    recall = get_stats_from_results_file("cross_validation_results/" + fold_name + "/" + name + ".json", annotations_filepath)
    # returns string giving the three weights and the correspondin recall on the train set
    # in the format "a,b,c,recall"
    return ",".join([str(weight) for weight in weights] + [str(recall)])
def collect_recall_data_weights_list(fold_name, fold_train_set, weights_list, annotations_filepath = "all_annotations.json"):
    inputs = [(fold_name, fold_train_set, weights, annotations_filepath) for weights in weights_list]
    with multiprocessing.Pool() as pool:
        results = pool.starmap(collect_recall_data_weights, inputs)
    csv_data = "a,b,c,recall\n"
    csv_data += "\n".join(results)
    with open("cross_validation_results/" + fold_name + "/recall_data.csv", "w") as f:
        f.write(csv_data)
def predict_on_test_set(fold_name, fold_test_set, weights, annotations_filepath = "all_annotations.json"):
    name = "predicted_best_weights_" + format(weights[0], ".2f") + "_" + format(weights[1], ".2f") + "_" + format(weights[2], ".2f")
    lm = LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction(weights))
    map_list_compare_linkages(fold_test_set, name, annotations_filepath, lm, "cross_validation_results/" + fold_name + "/" + name + ".json")
    recall = get_stats_from_results_file("cross_validation_results/" + fold_name + "/" + name + ".json", annotations_filepath)
    # returns string giving the three weights and the correspondin recall on the train set
    # in the format "fold_name,a,b,c,recall"
    return fold_name + "," + ",".join([str(weight) for weight in weights] + [str(recall)])
if __name__ == "__main__":
    folds = load_folds_from_folder()
    fold_counter = 0
    output_csv_stats = "fold_name,predicted_a,predicted_b,predicted_c,recall\n"
    for fold in folds:
        fold_name = "fold_" + str(fold_counter)
        os.makedirs("cross_validation_results/" + fold_name, exist_ok = True)
        collect_recall_data_weights_list(fold_name, fold["train"], get_random_weights_sample())
        predicted_optimal_weights = random_forest_regressor(load_data_from_csv("cross_validation_results/" + fold_name + "/recall_data.csv"))
        print(predicted_optimal_weights)
        stats_line = predict_on_test_set(fold_name, fold["test"], predicted_optimal_weights)
        output_csv_stats += stats_line + "\n"
        fold_counter += 1
