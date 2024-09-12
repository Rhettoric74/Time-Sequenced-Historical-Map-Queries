from map_graph import prims_mst, FeatureNode, MahalanobisMetric
from compare_linkages import *
from collect_map_data import load_all_maps_into_df
from analyze_recall_data import find_mahalanobis_metric
import json
import multiprocessing as mp
import random
import numpy as np
import pickle
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
def train_malanahobis_metric_for_fold(fold_train_set, fold_name, annotations_filepath = "all_annotations.json"):
    df = load_all_maps_into_df(annotations_filepath, fold_train_set)
    df.to_csv("cross_validation_malanahobis_results/" + fold_name + "/" + "train_pairs_data.csv", index=False)
    return find_mahalanobis_metric("cross_validation_malanahobis_results/" + fold_name + "/" + "train_pairs_data.csv")
def predict_on_test_set(fold_name, fold_test_set, malanahobis_metric, annotations_filepath = "all_annotations.json"):

    name = "malanahobis_metric"
    print(name)
    linkage_method = LinkageMethod(prims_mst, MahalanobisMetric(malanahobis_metric))
    map_list_compare_linkages(fold_test_set, name, annotations_filepath, linkage_method, "cross_validation_malanahobis_results/" + fold_name + "/" + name + ".json")
    recall = get_stats_from_results_file("cross_validation_malanahobis_results/" + fold_name + "/" + name + ".json", annotations_filepath)
    # returns string giving the three weights and the correspondin recall on the train set
    # in the format "fold_name,a,b,c,recall"
    return fold_name + "," + name + "," + str(recall)
if __name__ == "__main__":
    folds = load_folds_from_folder()
    fold_counter = 0
    output_csv_stats = "fold_name,coefficients,recall\n"
    for fold in folds:
        fold_name = "fold_" + str(fold_counter)
        os.makedirs("cross_validation_malanahobis_results/" + fold_name, exist_ok = True)
        malanahobis_metric = train_malanahobis_metric_for_fold(fold["train"], fold_name)
        stats_line = predict_on_test_set(fold_name, fold["test"], malanahobis_metric)
        output_csv_stats += stats_line + "\n"
        fold_counter += 1
