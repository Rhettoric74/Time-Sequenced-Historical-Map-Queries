from compare_linkages import LinkageMethod, map_list_compare_linkages, get_stats_from_results_file
from cross_validation_experiment import load_folds_from_folder
from map_graph import FeatureNode, prims_mst

if __name__ == "__main__":
    folds = load_folds_from_folder()
    counter = 0
    for fold in folds:
        test_set = fold["test"]
        lm = LinkageMethod(prims_mst, FeatureNode.EdgeCostFunction([1, 1, 1]))
        fold_name = "fold" + str(counter) + "_mst"
        output_file_name = "weighted_mst_results/" + fold_name + ".json"
        counter += 1
        map_list_compare_linkages(test_set, fold_name, "all_annotations.json", lm, output_file_name)
        get_stats_from_results_file(output_file_name, "all_annotations.json")