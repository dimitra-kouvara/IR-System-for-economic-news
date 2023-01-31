import json
import numpy as np
from scipy.spatial import distance
import pandas as pd


def countSimilarity(queryEmbedding, summaryEmbeding):

    cosSimilarity = distance.cosine(queryEmbedding, summaryEmbeding)

    return 1-cosSimilarity



def getEmbeddings(embeddingsDataframe, queryEmbedding):

    # import the embeddings file
    with open('embeddingsTable.json', 'r') as aFile:
        data = json.load(aFile)

    keepSimilarities = []

    for i in range(len(embeddingsDataframe)):
        dummyEmbedding = np.array(data[embeddingsDataframe['link'][i]][0])
        keepSimilarities.append(countSimilarity(queryEmbedding, dummyEmbedding))

    embeddingsDataframe['similarity'] = 0.0
    for i in range(len(embeddingsDataframe)):
        embeddingsDataframe['similarity'][i] = keepSimilarities[i]

    return embeddingsDataframe.sort_values(by='similarity', ascending=False)
