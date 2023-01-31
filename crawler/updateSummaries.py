from transformers import BartForConditionalGeneration, BartTokenizer
import mysql.connector
import pandas as pd
from re import sub
from string import digits


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
    # get the large facebook tokenizer and create the model
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    # connect to the db.use your credentials
    db = mysql.connector.connect(host='localhost',
                                 user='root',
                                 password='@cg-DS-2020!')
    # name the cursor and execute commands
    myCursor = db.cursor()
    myCursor.execute('USE newspaper')

    aTest = True
    trackOfRuns = 1

    while aTest:
        print('This is loop number '+str(trackOfRuns))
        myCursor.execute("SELECT link, title, article FROM articles WHERE summary is NULL LIMIT 10")
        df = pd.DataFrame(myCursor.fetchall(), columns=['link', 'title', 'articles'])

        if len(df) == 0:
            break

        trackOfRuns += 1

        # insert in database a column for clean text
        df['clean'] = ''

        for i in range(len(df['articles'])):
            df['clean'][i] = cleanSentence(df['articles'][i])

        # insert in database a column for the summary
        df['summarized'] = ''

        # Encoding the inputs and passing them to model.generate()
        for i in range(len(df['clean'])):
            inputs = tokenizer.batch_encode_plus([df['clean'][i]], return_tensors='pt', truncation=True, max_length=512)
            summary_ids = model.generate(inputs['input_ids'], early_stopping=True)
            # Decoding and printing the summary
            bart_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            df['summarized'][i] = bart_summary

        # Remove the dots from the sentences for bert
        for i in range(len(df['summarized'])):
            df['summarized'][i] = cleanSentence(df['summarized'][i])

        # insert in database before closing.
        for i in range(len(df)):
            sql = ("UPDATE articles SET summary = '" + df['summarized'][i] + "' WHERE link LIKE '" + df['link'][i] + "'")
            myCursor.execute(sql)
            db.commit()
    db.close()


if __name__ == "__main__":
    main()
