import threading
import databaseRefresh
import marketBeatScraper
import indiaNewsRefresh
import indiatimesScraper
import updateSummaries
import updateSummariesIndia
import bertEmbeddingsCreator
import newAdditionsLabeling


def main():
    # start the scrapers
    t1 = threading.Thread(target=marketBeatScraper.main())
    t2 = threading.Thread(target=indiatimesScraper.main())

    t2.start()
    t1.start()

    t1.join()
    myFile = 'bigTable.json'
    t2.join()
    myFile2 = 'anotherTable.json'

    # insert the new articles in the database
    print('Inserting new data to articles table')
    df = databaseRefresh.jsonToDataframe(myFile)
    print('Inserting new data to indianews table')
    df2 = indiaNewsRefresh.jsonToDataframe(myFile2)

    t3 = threading.Thread(target=databaseRefresh.appendNewArticles(df))
    t4 = threading.Thread(target=indiaNewsRefresh.appendNewArticles(df2))

    t3.start()
    t4.start()

    # insert article summaries in database
    print('Accessing data without summary')
    t5 = threading.Thread(target=updateSummaries.main())
    t6 = threading.Thread(target=updateSummariesIndia.main())

    t5.start()
    t6.start()

    # insert bert embeddings in json file used as database
    print('Creating new Bert Embeddings')
    bertEmbeddingsCreator.main()

    # label any new articles with the trained classifier
    print('Labeling new items in the database')
    newAdditionsLabeling.main()


if __name__ == "__main__":
    main()
