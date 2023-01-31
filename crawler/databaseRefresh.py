# import basic libraries
import mysql.connector
import pandas as pd
import json
import datetime


# since the files from the site are saved into json format
# use this module to transform them to dataframe
def jsonToDataframe(myFile):
    with open(myFile) as inputFile:
        data = json.load(inputFile)

    df_data = pd.DataFrame.from_dict(data, orient='index')
    df_data.reset_index(level=0, inplace=True)
    df_data.rename(columns={'index': 'Link'}, inplace=True)

    return df_data


# in case someone wants the last time the files were updated
# can run the below function and get the latest article post in the database
def getLastRefreshDate():
    # connect to the db. use your credentials
    db = mysql.connector.connect(host='localhost', user='root', password='@cg-DS-2020!')

    # name the cursor and execute commands
    myCursor = db.cursor()

    myCursor.execute('USE newspaper')
    myCursor.reset()

    # extract the last refresh date
    sqlCommand = 'SELECT MAX(date) FROM articles'
    myCursor.execute(sqlCommand)
    lastRefresh = myCursor.fetchall()

    db.close()

    returnedDate = lastRefresh[0][0]
    mindate = datetime.datetime(1900, 1, 1, 10, 50, 0)

    if returnedDate is None:
        return mindate
    else:
        return returnedDate


# use the code below to update the database with the latest files
def appendNewArticles(toUpdate):

    toUpdate['Date'] = pd.to_datetime(toUpdate['Date'])

    toUpdate = toUpdate.loc[toUpdate['Date'] >= getLastRefreshDate()]

    # connect to the db. use your credentials
    db = mysql.connector.connect(host='localhost',
                                 user='root',
                                 password='@cg-DS-2020!')

    # name the cursor and execute commands
    myCursor = db.cursor()

    myCursor.execute('USE newspaper')
    myCursor.reset()

    # append items to the table
    cols = ",".join([str(i) for i in toUpdate.columns.tolist()])

    for i, row in toUpdate.iterrows():
        try:
            sqlCommand = "INSERT INTO articles (" + cols + ") VALUES " + str(tuple(row))
            myCursor.execute(sqlCommand)
            db.commit()
        except:
            print('Duplicate Found')

    db.close()
