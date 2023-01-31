# import the libraries
from json import JSONDecodeError
import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import datefinder
import random
import databaseRefresh
import re


# pass in to requests some random user agent to represent a human and different machine for the STARTING PAGE
def chromeUserStartingPage(agentsList):
  credentialsDict = {
      'User-Agent': random.choice(agentsList),
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'Upgrade-Insecure-Requests': '1'
  }
  return credentialsDict


# pass in to requests some random user agent to represent a human and different machine
def chromeUserGenerator(agentsList):
    credentialsDict = {
        'User-Agent': random.choice(agentsList),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
        'Upgrade-Insecure-Requests': '1'
    }

    return credentialsDict

# use http protocol free proxies to attemp to scrape
def randomProxyGenerator(proxyList):
  randomDict = {'http': 'http://'+random.choice(proxyList)}

  return randomDict

def remove_html_tags(text):

    clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

    return re.sub(clean, '', text).strip()

# this is the links scrapper
def siteUrlScrapper(centralUrl, url, agentsList, proxiesList):

    # send the request to server
    page = requests.get(url, headers=chromeUserStartingPage(agentsList), proxies=randomProxyGenerator(proxiesList),
                        timeout=random.randint(7, 10))

    # pass the site to beautiful soup
    soup = BeautifulSoup(page.content, "html.parser")

    # get the latest news pages to download
    resultsFooter = soup.find(class_="headlines-footer")

    # we will create a dictionary with article name as key and datetime as value
    sitesRepository = {}

    # create a loop to get the scrolling footers for latest news
    for a in resultsFooter.find_all('a', href=True):

        dummyList = []
        dummyDates = []

        # since the sub-string /headlines/ is in footer, split it at / and get last part of the latest news url
        separatedLink = a['href'].split('/', 2)

        newUrl = url + separatedLink[2]

        # search again for the links of the site
        page = requests.get(newUrl, headers=chromeUserStartingPage(agentsList),
                            proxies=randomProxyGenerator(proxiesList), timeout=random.randint(7, 10))

        # pass the site to beautiful soup
        soup = BeautifulSoup(page.content, "html.parser")

        # search for the main part, where text is located
        results = soup.find(id="updatePanel1")

        # get from the body of results the class with name title, holding the link of each document
        for a in results.find_all('a', class_='title'):

            dummyString = a['href']

            # some links have the full address and some not
            if centralUrl not in dummyString:
                dummyString = centralUrl + dummyString

            dummyList.append(dummyString)

        # get from the body of results the class with name post time, holding when the site was posted
        for each in results.find_all('div', class_='post-time'):

            # found it easier to extract the date as text
            y = str(each)
            y = y.split('>')
            y = y[1].split('<')
            y = y[0]

            # with datefinder it autodetects the datetime and converts it to the correct type
            matches = datefinder.find_dates(y)

            for match in matches:
                dummyDates.append(match)

        lastRefresh = databaseRefresh.getLastRefreshDate()

        # create the site repository with url and date
        for j in dummyList:
            for z in dummyDates:
                if z >= lastRefresh:
                    sitesRepository[j] = z
                    dummyDates.remove(z)
                    break
                else:
                    break

        time.sleep(random.randint(3, 6))

    return sitesRepository


# this gets the data and saves them to json file
def scrapTheArticles(urlDictionary, agentsList, proxiesList):
    # create big table like dictionary
    writterData = {}
    errorPointer = 0

    for url in urlDictionary.keys():

        try:

            errorPointer += 1

            # send the request to server
            page = requests.get(url, headers=chromeUserGenerator(agentsList), proxies=randomProxyGenerator(proxiesList),
                                timeout=random.randint(7, 10))

            # pass the site to beautiful soup
            soup = BeautifulSoup(page.content, "html.parser")

            # search for the main part, where text is located
            # results = soup.find(id="main")
            results = soup.find('div', class_='page-wrap').find('main').find('div', class_='headlinearticle')

            # create an empty string and populate it with the article
            try:
                emptyString = remove_html_tags(results.text)

            except:
            # a few pages return nothing when searching with headlinearticle
            # the text is located under the container financialterm
                if emptyString == '':
                    try:
                        content = soup.find('div', class_='page-wrap').find('main').find("div", class_="financialterm")
                        emptyString = remove_html_tags(content.text)
                    except:
                        pass

            # get the site information in json
            dataContainer = soup.find(type="application/ld+json")
            for i in dataContainer:
                js = json.loads(i)

            # get the article title
            articleTitle = js['headline']

            # get the article author
            articleAuthor = js['author']['name']

            # get the article publisher
            articlePublisher = js['publisher']['name']

            # data to write
            writterData[url] = {'Title': articleTitle, 'Author': articleAuthor, 'Publisher': articlePublisher,
                                'Date': urlDictionary[url], 'Article': emptyString}

        except JSONDecodeError:
            print('Again the same error')
            print('Errors place at position:', errorPointer)

        except AttributeError:
            print('There may be a new type of tags')

        except ConnectionError:
            print('Change your free proxies')

        time.sleep(random.randint(3, 6))

    return writterData

# use it to serialize the datetime into json
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def main():
    # import a file to create the random user agents
    userAgentsFile = 'userAgents.txt'

    with open(userAgentsFile, 'r') as inputFile:
      agentsList = inputFile.readlines()

    for item in range(len(agentsList)):
      agentsList[item] = agentsList[item][:-1]

    # import a file and create the random proxies
    proxiesListFile = 'proxiesList.txt'

    with open(proxiesListFile, 'r') as inputFile:
      proxiesList = inputFile.readlines()

    for item in range(len(proxiesList)):
      proxiesList[item] = proxiesList[item][:-1]

    # site home page
    centralUrl = 'https://www.marketbeat.com'

    # enter the URL for article in site marketbeat
    url = 'https://www.marketbeat.com/headlines/'

    # starting message
    print('The links scrapping has started at: ', datetime.datetime.now())

    # get the links and dates
    urlAndDateDict = siteUrlScrapper(centralUrl, url, agentsList, proxiesList)

    print('The links have been retrieved at: ', datetime.datetime.now())

    print('The articles scraping sequence has started at: ', datetime.datetime.now())

    # scrap the data
    writterData = scrapTheArticles(urlAndDateDict, agentsList, proxiesList)

    print('The articles have been gathered at: ', datetime.datetime.now())

    # serializing json
    jsonObject = json.dumps(writterData, indent=4, default=myconverter)

    # path to write the files
    # path = '/content/drive/My Drive/scraperProject/'

    # writing to json
    jsonFile = 'bigTable.json'

    with open(jsonFile, "w") as outfile:
      outfile.write(jsonObject)

    print('The files have stored in a .json file in the corresponding path')
    print('The program will now stop')

if __name__== "__main__":
    main()
