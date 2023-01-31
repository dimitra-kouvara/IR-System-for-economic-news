import numpy as np
import pandas as pd
import json
import umap.umap_ as umap
import sklearn.cluster as cluster
from kneed import KneeLocator
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import warnings
import mysql.connector

warnings.filterwarnings('ignore')

file = 'embeddingsTable.json'
with open(file) as jsonFile:
    aDict = json.load(jsonFile)

embeddingsList = list(aDict.values())
for i in range(len(embeddingsList)):
    embeddingsList[i] = embeddingsList[i][0]

embeddingsArray = np.array(embeddingsList)

standard_embedding = umap.UMAP(random_state=42).fit_transform(embeddingsArray)
plt.scatter(standard_embedding[:, 0], standard_embedding[:, 1], s=10, cmap='Spectral')
plt.show()

# A list holds the silhouette coefficients for each k
sse = []
silhouette_coefficients = []
kmeans_kwargs = {
    "init": "random",
    "n_init": 10,
    "max_iter": 3000,
    "n_jobs": -1}
for k in range(2, 50):
    kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
    kmeans.fit(embeddingsArray)
    sse.append(kmeans.inertia_)
    score = silhouette_score(embeddingsArray, kmeans.labels_)
    silhouette_coefficients.append(score)

plt.plot(range(2, 50), silhouette_coefficients, '*-')
plt.xticks(range(2, 50))
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Coefficient")
plt.show()

# choose the best inertia
kl = KneeLocator(range(2, 50), sse, curve="convex", direction="decreasing")
print("The number of clusters using the elbow method are ", kl.elbow)
kl.plot_knee()
plt.show()

kmeans_labels = cluster.KMeans(n_clusters=kl.elbow, n_init=500, max_iter=500,
                               random_state=50).fit_predict(embeddingsList)

plt.scatter(standard_embedding[:, 0], standard_embedding[:, 1], c=kmeans_labels, s=10, cmap='Spectral')
plt.show()

newDict = {}
for i in range(len(aDict.keys())):
    newDict.update({list(aDict.keys())[i]: kmeans_labels[i]})

df = pd.DataFrame.from_dict(newDict, orient='index', columns=['label']).reset_index()

df.rename(columns={'index': 'link'}, inplace=True)

# connect to the db.use your credentials
db = mysql.connector.connect(host='localhost',
                             user='root',
                             password='@cg-DS-2020!')

# name the cursor and execute commands
myCursor = db.cursor()
myCursor.execute('USE newspaper')

# refresh database labels
for i in range(len(df)):
    if "marketbeat" in df['link'][i]:
        sql = ("UPDATE articles SET label = " + str(df['label'][i]) + " WHERE link LIKE '" + df['link'][i] + "'")
        myCursor.execute(sql)
        db.commit()
    if "indiatimes" in df['link'][i]:
        sql = ("UPDATE indianews SET label = " + str(df['label'][i]) + " WHERE link LIKE '" + df['link'][i] + "'")
        myCursor.execute(sql)
        db.commit()

db.close()
