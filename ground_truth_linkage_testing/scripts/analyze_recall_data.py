import pandas
import numpy

def load_data_from_csv(filename = "recall_data.csv"):
    return pandas.read_csv(filename)
if __name__ == "__main__":
    df = load_data_from_csv()
    print(df.columns)
    print(df.loc[df["recall"].idxmax()])