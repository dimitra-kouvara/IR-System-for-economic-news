import mysql.connector
import pandas as pd

def getLabelledData(label):
    # connect to the db.use your credentials
    db = mysql.connector.connect(host='localhost',
                                 user='root',
                                 password='@cg-DS-2020!')

    # name the cursor and execute commands
    myCursor = db.cursor()
    myCursor.execute('USE newspaper')
    myCursor.reset()
    myCursor.execute("SELECT link, summary, article FROM articles WHERE label = '"+str(label)+"(' UNION SELECT link, summary, article FROM indianews WHERE label = '"+str(label)+"'")
    df = pd.DataFrame(myCursor.fetchall(), columns=['link', 'summary', 'article'])
    db.close()

    return df
