import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot as plt

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
if __name__ == "__main__":
    df = load_data_from_csv()
    print(random_forest_regressor(df))
    """ plot_weight_against_recall_data(df, "a")
    plot_weight_against_recall_data(df, "b")
    plot_weight_against_recall_data(df, "c") """
    """
    Results so far:
    Mean Squared Error: 0.00028605970339935603
    feature  importance
    2       c    0.344153
    1       b    0.341773
    0       a    0.314074
    a                   1.510000
    b                   0.600000
    c                   0.360000
    predicted_recall    0.894369
    """