import torch
from transformers import LongformerModel, LongformerTokenizer
import numpy as np
import mysql.connector
import pandas as pd
import json
from string import digits
from re import sub


# some basic cleaning function for bert
def cleanSentence(sentence):
    # step 1: remove digits
    removeDigits = str.maketrans('', '', digits)
    sentence = sentence.translate(removeDigits)

    # step 2: remove punctuation
    punctuation = '()-[]{};:\'"”“’—\,.<>/@#$%^&*_~\n'
    removePunctuation = str.maketrans('', '', punctuation)
    sentence = sentence.translate(removePunctuation)
    sentence = sentence.strip()
    sentence = sub(' +', ' ', sentence)

    return ''.join(sentence)


def main():
    # call the pretrained bert model
    model = LongformerModel.from_pretrained('allenai/longformer-base-4096')
    tokenizer = LongformerTokenizer.from_pretrained('allenai/longformer-base-4096')

    # connect to the db.use your credentials
    db = mysql.connector.connect(host='localhost',
                                 user='root',
                                 password='@cg-DS-2020!')

    # name the cursor and execute commands
    myCursor = db.cursor()
    myCursor.execute('USE newspaper')
    myCursor.reset()
    myCursor.execute("(SELECT link, article FROM articles where label is NULL) UNION (SELECT link, article FROM indianews where label is NULL)")
    df = pd.DataFrame(myCursor.fetchall(), columns=['link', 'article'])
    db.close()

    # make a list to hold the embeddings
    sentence_embeddings = []

    zZ = 1
    # run the model and get the embeddings
    for i in range(len(df)):
        print("This is loop number ", zZ)
        dummyValue = cleanSentence(df['article'][i])
        input_ids = torch.tensor(tokenizer.encode(dummyValue, truncation=True, max_length=4096)).unsqueeze(0)
        outputs = model(input_ids)
        # sequence_output = outputs.last_hidden_state
        pooled_output = outputs.pooler_output
        sentence_embeddings.append(pooled_output.detach().numpy()[0])
        zZ += 1

    # make a dictionary to keep the key:embedding
    writter = {}

    for i in range(len(df)):
        writter[df['link'][i]] = sentence_embeddings[i].tolist()

    # write the embeddings to .json file which will be the embeddings database
    # jsonObject = json.dumps(writter) To use only when the file is not initialized
    jsonFile = 'embeddingsTable.json'

    with open(jsonFile, "r+") as outfile:
        data = json.load(outfile)
        data.update(writter)
        outfile.seek(0)
        json.dump(data, outfile)


if __name__ == "__main__":
    main()
