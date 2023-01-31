import mysql.connector
import json
import pandas as pd
import pickle
import numpy as np


def main():
    # connect to the db.use your credentials
    db = mysql.connector.connect(host='localhost',
                                 user='root',
                                 password='@cg-DS-2020!')

    # name the cursor and execute commands
    myCursor = db.cursor()
    myCursor.execute('USE newspaper')
    myCursor.reset()
    myCursor.execute("(SELECT link FROM articles WHERE label is NULL) UNION (SELECT link FROM indianews WHERE label is NULL)")
    df = pd.DataFrame(myCursor.fetchall(), columns=['link'])
    db.close()

    with open('embeddingsTable.json', 'r') as aFile:
        data = json.load(aFile)

    listOfLabels = []
    listOfEmbedds = []

    filename = 'queryPrediction.sav'
    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))

    for i in range(len(df)):
        listOfEmbedds.append(data[df['link'][i]])
    embeddingsArray = np.array(listOfEmbedds)

    for i in range(len(embeddingsArray)):
        try:
            listOfLabels.append(loaded_model.predict(embeddingsArray[i:i+1,])[0])
        except:
            listOfLabels.append(loaded_model.predict(embeddingsArray[len(embeddingsArray)-1:,])[0])

    df['label'] = 0

    for i in range(len(df)):
        df['label'][i] = listOfLabels[i]

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


if __name__ == "__main__":
    main()
