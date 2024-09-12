from map_graph import prims_mst, FeatureNode, LogisticRegressionEdgeCost
from compare_linkages import *
from collect_map_data import load_all_maps_into_df
from analyze_recall_data import label_linking_logistic_regression, load_pairwise_label_data, preprosses_dataframe
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
def train_lr_model_for_fold(fold_train_set, annotations_filepath = "all_annotations.json"):
    df = load_all_maps_into_df(annotations_filepath, fold_train_set)
    return label_linking_logistic_regression(df)
def predict_on_test_set(fold_name, fold_test_set, lr_model, annotations_filepath = "all_annotations.json"):

    name = "coef_" + "_".join([str(coef) for coef in lr_model.coef_[0]])
    print(name)
    lm = LinkageMethod(prims_mst, LogisticRegressionEdgeCost(lr_model))
    map_list_compare_linkages(fold_test_set, name, annotations_filepath, lm, "cross_validation_lr_results/" + fold_name + "/" + name + ".json")
    recall = get_stats_from_results_file("cross_validation_lr_results/" + fold_name + "/" + name + ".json", annotations_filepath)
    # returns string giving the three weights and the correspondin recall on the train set
    # in the format "fold_name,a,b,c,recall"
    return fold_name + "," + name + "," + str(recall)
if __name__ == "__main__":
    folds = load_folds_from_folder()
    fold_counter = 0
    output_csv_stats = "fold_name,coefficients,recall\n"
    for fold in folds:
        fold_name = "fold_" + str(fold_counter)
        os.makedirs("cross_validation_lr_results/" + fold_name, exist_ok = True)
        lr = train_lr_model_for_fold(fold["train"])
        stats_line = predict_on_test_set(fold_name, fold["test"], lr)
        output_csv_stats += stats_line + "\n"
        fold_counter += 1
