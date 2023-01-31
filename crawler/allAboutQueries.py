from transformers import LongformerModel, LongformerTokenizer
import pickle
import time
import retrieveLabeledItems
import retrieveRelativeEmbeddings
import torch


model = LongformerModel.from_pretrained('allenai/longformer-base-4096')
tokenizer = LongformerTokenizer.from_pretrained('allenai/longformer-base-4096')
filename = 'queryPrediction.sav'
# load the model from disk
loaded_model = pickle.load(open(filename, 'rb'))

while True:
    # ask for the user input
    queryInput = input('What are you interested in?')

    if queryInput == 'q' or queryInput == 'Q':
        print('You are now exiting the search engine.\nPlease come again.')
        break

    # turn query to embedding
    input_ids = torch.tensor(tokenizer.encode(queryInput, truncation=True, max_length=4096)).unsqueeze(0)
    outputs = model(input_ids)
    qBert = outputs.pooler_output.detach().numpy()[0]

    qLabel = loaded_model.predict(qBert.reshape(1, -1))[0]

    print('The query is of theme ', qLabel)

    relativeArticles = retrieveLabeledItems.getLabelledData(qLabel)

    relativeArticles = retrieveRelativeEmbeddings.getEmbeddings(relativeArticles, qBert)

    print(relativeArticles['summary'].head())

    del input_ids
    del outputs
    del qBert
    del qLabel
    del relativeArticles
    # print('These are some '+str(len(relativeArticles))+' articles that may interest you.\n')
    #
    # for i in range(5):
    #     print(relativeArticles['summary'][i]+"\n")
    #     time.sleep(2)
    #
    # time.sleep(2)

    queryInput = input('If you want to exit press q or Q.')

    if queryInput == 'q' or queryInput == 'Q':
        print('You are now exiting the search engine.\nPlease come again.')
        break
    else:
        print('The search process is starting again in 2 seconds!')
        time.sleep(1)
        continue
