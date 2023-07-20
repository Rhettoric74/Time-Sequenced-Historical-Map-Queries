"""
Purpose: Cluster the documents in the csv dataset to speed up process of searching maps
Idea: Use sklearn's TfidfVectorizer to vectorize documents, and then use scipy's 
agglomerate heirarchical clustering on the map metadata
Hopefully this will show """
from csv import DictReader
import re
import random
import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import extract_year

from sklearn.feature_extraction.text import TfidfVectorizer

def vectorize_metadata(filename = "luna_omo_metadata_56628_20220724.csv"):
    corpus = []
    with open(filename, errors="ignore") as f:
        reader = DictReader(f)
        for row in reader:
            file_metadata = " ".join([row["title"], row["description"], row["fieldValues"]])
            corpus.append(re.sub('\b[0-9][0-9.,-]*\b', 'NUMBER-SPECIAL-TOKEN', file_metadata))
    vectorizer = TfidfVectorizer(analyzer = "word", stop_words = "english", min_df=200)
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    words_only = [name for name in feature_names if not name.isnumeric()]
    print(len(feature_names), len(words_only))
    print(X.shape)
    return X
def k_means(vectorized_documents, k, iterations, filename = "luna_omo_metadata_56628_20220724.csv"):
    """
    Purpose: use k nearest neighbors algorithm to cluster vectorized documents
    Parameters: vectorized documents, a 2-D numpy array obtained from running vectorize_metadata
    """
    """ 
    svd = TruncatedSVD(100)
    reduced_vectors = svd.fit_transform(X)
    print("dimensions reduced")
    print(len(reduced_vectors[0])) """
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto").fit(X)
    clustered_ids = {}
    with open(filename, errors="ignore") as f:
        reader = DictReader(f)
        i = 0
        for row in reader:
            label = kmeans.labels_[i]
            if label not in clustered_ids:
                clustered_ids[label] = [row["filename"]]
            else:
                clustered_ids[label].append(row["filename"])
            i += 1
    return clustered_ids
if __name__ == "__main__":
    X = vectorize_metadata()
    print("vectorized")
    
    num_clusters = 100
    clustered_ids = k_means(X, num_clusters, 10)
    cluster_names = list(clustered_ids.keys())
    print(cluster_names)
    num_samples = 10
    for i in range(num_samples):
        cluster = random.choice(cluster_names)
        sample = random.sample(clustered_ids[cluster], 10)
        print(cluster, sample)
        print(extract_year.extract_years(sample))

    print("clustered")
