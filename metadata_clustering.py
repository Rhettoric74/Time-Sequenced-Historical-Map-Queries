"""
Purpose: Cluster the documents in the csv dataset to speed up process of searching maps
Idea: Use sklearn's TfidfVectorizer to vectorize documents, and then use scipy's 
agglomerate heirarchical clustering on the map metadata
Hopefully this will show """
from csv import DictReader
import re
import random
import numpy as np
from scipy.spatial.distance import pdist
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import extract_year

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = None
kmeans = None
svd = None
def vectorize_metadata(filename = "luna_omo_metadata_56628_20220724.csv"):
    corpus = []
    with open(filename, errors="ignore") as f:
        reader = DictReader(f)
        for row in reader:
            file_metadata = " ".join([row["title"], row["description"], row["fieldValues"]])
            corpus.append(re.sub('\b[0-9][0-9.,-]*\b', 'NUMBER-SPECIAL-TOKEN', file_metadata))
    global vectorizer 
    vectorizer = TfidfVectorizer(analyzer = "word", stop_words = "english", min_df=200)
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    words_only = [name for name in feature_names if not name.isnumeric()]
    print(X.shape)
    return X
def k_means(vectorized_documents, k, iterations, filename = "luna_omo_metadata_56628_20220724.csv"):
    """
    Purpose: use k nearest neighbors algorithm to cluster vectorized documents
    Parameters: vectorized documents, a 2-D numpy array obtained from running vectorize_metadata
    """
    
    global kmeans
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto").fit(vectorized_documents)
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
def find_most_relevant_cluster(search_terms):
    """
    Purpose: Given a search term, find the clusters most relevant to its.
    Parameters: search_terms (string), text to compare to the clusters to find the most similar clusters.
    Returns: most similar cluster id to the search vector."""
    search_vector = vectorizer.transform([search_terms])
    #reduced_search_vector = svd.transform(search_vector)
    return kmeans.predict(search_vector)[0]

class ClusterRetriever:
    def __init__(self, num_clusters = 200):
        self.vectorized_documents = vectorize_metadata()
        self.clustered_ids = k_means(self.vectorized_documents, num_clusters, 10)
        
    def find_relevant_map_ids(self, search_terms):
        cluster_found = find_most_relevant_cluster(search_terms)
        print(cluster_found)
        return self.clustered_ids[cluster_found]


if __name__ == "__main__":
    retriever = ClusterRetriever()
    cluster_sizes = [len(cluster) for cluster in retriever.clustered_ids.values()]
    print(max(cluster_sizes), min(cluster_sizes), np.std(cluster_sizes))

    searches = ["oslo christiania kristiania", "tokyo edo yedo"]
    for i in range(2):
        cluster = find_most_relevant_cluster(searches[i])
        print(searches[i])
        sample = random.sample(retriever.clustered_ids[cluster], 10)
        print(cluster, sample)
        print(np.std(list(extract_year.extract_years(sample).values())))


    print("clustered")
