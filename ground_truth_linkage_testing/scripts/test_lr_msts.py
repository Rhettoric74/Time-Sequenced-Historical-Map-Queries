import map_graph
from analyze_recall_data import *
from draw_features_and_linkages import draw_features_and_linkages
import multiword_name_extraction

if __name__ == "__main__":
    map_filename = "5797073_h2_w9.png"
    mg = map_graph.MapGraph(map_filename)
    lr_classifier = label_linking_logistic_regression(load_pairwise_label_data("filtered_train_label_pair_attributes.csv"))
    predict_connections_with_classifier(lr_classifier, load_pairwise_label_data("filtered_val_label_pair_attributes.csv"))
    print(lr_classifier.coef_)
    map_graph.prims_mst(mg.nodes, map_graph.LogisticRegressionEdgeCost(lr_classifier))
    print(mg.count_edges())
    print(len(mg.nodes))
    map_annotations = multiword_name_extraction.extract_map_data_from_all_annotations(map_filename)
    draw_features_and_linkages(map_filename, mg, "weighted_distance_threshold.png", False)