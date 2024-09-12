import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from metric_learn import MMC
from matplotlib import pyplot as plt
"""This section is for my experiments trying to predict the optimal weights for minimum spanning tree
edge cost functions, based on collected data for other sampled weights and the resulting recall."""
def load_data_from_csv(filename = "recall_data.csv"):
    return pd.read_csv(filename)
def plot_weight_against_recall_data(data_frame, column):
    data_frame.plot.scatter(x=column, y="recall")
    plt.title("Recall of MSTs with edge cost function weight for " + column)
    plt.xlabel("weight of " + column + " in edge cost function")
    plt.ylabel("Recall of MSTs in samples of 10 maps")
    plt.show()
def random_forest_regressor(data_frame):
    X = data_frame.drop("recall", axis=1)
    y = data_frame["recall"]
    # Train Random Forest model
    model = RandomForestRegressor(n_estimators=300, random_state=18)
    model.fit(X, y)

    # Predict edge costs
    data_frame["predicted_recall"] = model.predict(X)
    # Evaluate the model
    mse = mean_squared_error(y, data_frame['predicted_recall'])
    print('Mean Squared Error:', mse)

    # Feature importance
    importances = model.feature_importances_
    feature_names = X.columns
    feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
    print(feature_importance_df)
    more_precise_df = pd.DataFrame(np.array([[0.01 * i, 0.01 * j, 0.01 * k] for i in range(201) for j in range(101) for k in range(101)]), columns=["a","b","c"])
    more_precise_df["predicted_recall"] = model.predict(more_precise_df)
    return more_precise_df.loc[more_precise_df["predicted_recall"].idxmax()]

"""This next section instead seeks to train a random forest classifier based on the same features I used for the MSTs.
Given a pair of labels and the distance, height ratio, sin angle difference, and capitalization difference of the two labels, whether there should be an edge between them"""
def load_pairwise_label_data(filename = "train_label_pair_attributes.csv"):
    return pd.read_csv(filename)
def preprosses_dataframe(data_frame):
    X = data_frame.drop(["label1", "label2", "connected"], axis=1)
    min_max_scaler = preprocessing.MinMaxScaler()
    #X_minmax = min_max_scaler.fit_transform(X)
    Y = data_frame["connected"]
    print("preprocessing complete")
    return X, Y
def label_linking_rf_classifier(data_frame):
    rf_classifier = RandomForestClassifier(n_estimators=100, n_jobs = -1, random_state=42)
    X, Y = preprosses_dataframe(data_frame)
    print("starting training")
    rf_classifier.fit(X, Y)

    # Predict edge costs
    predicted_connections = rf_classifier.predict(X)
    # Evaluate the model
    accuracy = accuracy_score(Y, predicted_connections)
    print(f'Accuracy: {accuracy * 100:.2f}%')
    print(classification_report(Y, predicted_connections))
    print(confusion_matrix(Y, predicted_connections))

    # Feature importance
    importances = rf_classifier.feature_importances_
    feature_names = data_frame.columns
    print(feature_names)
    print(importances)
    return rf_classifier
def label_linking_logistic_regression(data_frame):
    X, Y = preprosses_dataframe(data_frame)
    lr = LogisticRegression(random_state=0)
    lr.fit(X, Y)
    return lr

def predict_connections_with_classifier(classifier, data_frame):
    X, Y = preprosses_dataframe(data_frame)
    predicted_connections = classifier.predict(X)
    accuracy = accuracy_score(Y, predicted_connections)
    print(f'Accuracy: {accuracy * 100:.2f}%')
    print(classification_report(Y, predicted_connections))
    print(confusion_matrix(Y, predicted_connections))
    return predicted_connections
def find_mahalanobis_metric(data_filepath):
    df = load_pairwise_label_data(data_filepath)
    df["height_ratio"] = df["height_ratio"] - 1
    used_features = ["normalized_distance", "height_ratio", "sine_angle_difference", "capitalization_difference"]
    difference_stats = df[used_features].to_numpy()
    # the above stats are measuring the difference of the features between pairs. 
    # to use with MMC, we need a pair of stats to compare for each pair, so we create
    # a 0 vector allong with each row of feature differences to represent the pairs
    pairs = np.array([[np.array([0,0,0,0]), differences] for differences in difference_stats])
    y = df["connected"]
    y = np.array([1 if connected_value == 1 else -1 for connected_value in y])
    print(len(y))
    mmc = MMC()
    mmc.fit(pairs, y)
    print(mmc.get_mahalanobis_matrix())
    return mmc
    





if __name__ == "__main__":
    # first part
    """ df = load_data_from_csv()
    print(random_forest_regressor(df))
    plot_weight_against_recall_data(df, "a")
    plot_weight_against_recall_data(df, "b")
    plot_weight_against_recall_data(df, "c") """
    """
    Results so far: Mean Squared Error: 2.6972549635648344e-07
    1       b    0.493497
    0       a    0.293017
    2       c    0.213487
    a                   1.760000
    b                   0.880000
    c                   0.880000
    predicted_recall    0.837945
    """
    #second part
    lr_classifier = label_linking_logistic_regression(load_pairwise_label_data("filtered_train_label_pair_attributes.csv"))
    predict_connections_with_classifier(lr_classifier, load_pairwise_label_data("filtered_val_label_pair_attributes.csv"))
    print(lr_classifier.coef_)
    convex_weights = find_mahalanobis_metric("filtered_val_label_pair_attributes.csv")
    """
    The optimal value is: 1.720877714005484e-06
    The optimal x is: [[ 1.11313482e-12  3.13458326e-13  1.24207785e-12  6.15977615e-05]
    [ 3.13458326e-13 -1.20164867e-14  3.01346467e-14  2.33032980e-13]
    [ 1.24207785e-12  3.01346467e-14  3.98830366e-15  2.95402825e-12]
    [ 6.15977615e-05  2.33032980e-13  2.95402825e-12  1.28687769e-14]]"""