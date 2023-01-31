import mysql.connector
import json
import warnings
from sklearn import svm
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

warnings.filterwarnings('ignore')


# connect to the db.use your credentials
db = mysql.connector.connect(host='localhost',
                             user='root',
                             password='@cg-DS-2020!')

# name the cursor and execute commands
myCursor = db.cursor()
myCursor.execute('USE newspaper')

sql = ("(SELECT link, label FROM articles) UNION (SELECT link, label FROM indianews)")
myCursor.execute(sql)
df = pd.DataFrame(myCursor.fetchall(), columns=['link', 'label'])
db.close()

file = 'embeddingsTable.json'
with open(file) as jsonFile:
    aDict = json.load(jsonFile)

for i in aDict:
    aDict[i] = aDict[i][0]

embeddingsList = []
labelsList = []
for i in range(len(df)):
    embeddingsList.append(aDict[df['link'][i]])
    labelsList.append(df['label'][i])

# percentage for testing
perc = 0.8
x_train, x_test, y_train, y_test = train_test_split(embeddingsList, labelsList, train_size=perc)

clf = svm.SVC(decision_function_shape='ovo')
clf.fit(x_train, y_train)

Y_pred = clf.predict(x_train)
Y_true_pred = clf.predict(x_test)

confMatrixTrain = confusion_matrix(y_train, Y_pred, labels=None)
confMatrixTest = confusion_matrix(y_test, Y_true_pred, labels=None)

print('train: Conf matrix svm')
print(confMatrixTrain)

print('test: Conf matrix svm')
print(confMatrixTest)

print(f1_score(y_test, Y_true_pred, average=None))

logisticRegr = LogisticRegression()
logisticRegr.fit(x_train, y_train)
Y_pred = logisticRegr.predict(x_train)
Y_true_pred = logisticRegr.predict(x_test)

confMatrixTrain = confusion_matrix(y_train, Y_pred, labels=None)
confMatrixTest = confusion_matrix(y_test, Y_true_pred, labels=None)
print('train: Conf matrix logistic regression')
print(confMatrixTrain)

print('test: Conf matrix logistic regression')
print(confMatrixTest)

print(f1_score(y_test, Y_true_pred, average=None))

filename = 'queryPrediction.sav'
# save the model to disk
pickle.dump(logisticRegr, open(filename, 'wb'))
