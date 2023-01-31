import requests
from bs4 import BeautifulSoup
import datetime
import json
import random
from selenium import webdriver
import time
from indiaNewsRefresh import getLastRefreshDate
import datefinder


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
    randomDict = {'http': 'http://' + random.choice(proxyList)}

    return randomDict


def siteUrlScrapper():
    # set the URL, a proxy server, and configure the webDriver
    url = 'https://economictimes.indiatimes.com/news/latest-news'
    proxyServer = '39.106.223.134:80'
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--proxry-server=%s' % proxyServer)

    driver = webdriver.Chrome(executable_path=r"chromedriver.exe",
                              chrome_options=chromeOptions)
    driver.get(url)
    time.sleep(10)  # Allow 2 seconds for the web page to open
    scroll_pause_time = 10  # You can set your own pause time. My laptop is a bit slow so I use 1 sec

    for i in range(10):
        # the site loads if you scroll to a point
        # it was found that the Y axis coordinates are found as the yCoord variable indicates
        scrollHeight = driver.execute_script("return document.body.scrollHeight;")
        # scrolling Y co-ordinates
        yCoord = 0.987 * scrollHeight - 1415.2
        # scroll the screen
        driver.execute_script("window.scrollTo(1, %s)" % yCoord)
        time.sleep(scroll_pause_time)

    time.sleep(2*scroll_pause_time)
    # now that the screen is scrolled, we can get the article links
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body = soup.find('body').find('main', class_="pageHolder").find('div', class_="clearfix main_container")

    # we store the links and the date of release in a dictionary
    dummyDict = {}
    for li in body.find_all('li'):
        item = li.find('a', href=True)
        date = li.find('span')
        try:
            dummyDict.update({item['href']: date['data-time']})

        except:
            pass

    # since the article links miss the path prefix, we create another dictionary with the full URLs and the date
    dummyDict2 = {}
    for key in dummyDict:
        dummyDict2[url + key] = dummyDict[key]

    print(dummyDict2)

    return dummyDict2


def articleScraper(urlDictionary, agentsList, proxiesList):
    # create big table like dictionary
    writterData = {}
    errorPointer = 0

    for url in urlDictionary.keys():
        errorPointer += 1

        try:
            # send the request to server
            page = requests.get(url, headers=chromeUserGenerator(agentsList), proxies=randomProxyGenerator(proxiesList),
                                timeout=random.randint(7, 10))

            articleSoup = BeautifulSoup(page.text, 'html.parser')

            articleInfo = articleSoup.find('div', class_='article_wrap').find('div', class_="article_block clearfix")

            lastRefresh = getLastRefreshDate()

            saveDate = datefinder.find_dates(articleInfo['data-et'])

            for match in saveDate:
                finalDate = match

            if finalDate < lastRefresh:
                continue

            articleBody = articleSoup.find('div', class_='article_wrap').find('div', class_='edition clearfix').find('div')

            articleBody = articleBody.text

            writterData[url] = {'Title': articleInfo['data-arttitle'], 'Author': articleInfo['data-agency'],
                                'Publisher': 'economictimes.indiatimes.com', 'Date': articleInfo['data-et'],
                                'Article': articleBody}
        except:

            print('Errors place at position:', errorPointer)

        time.sleep(random.randint(3, 6))

    return writterData


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

    # starting message
    print('The links scrapping has started at: ', datetime.datetime.now())

    # get the links and dates
    urlAndDateDict = siteUrlScrapper()

    print('The links have been retrieved at: ', datetime.datetime.now())

    print('The articles scraping sequence has started at: ', datetime.datetime.now())

    # scrap the data
    writterData = articleScraper(urlAndDateDict, agentsList, proxiesList)

    print('The articles have been gathered at: ', datetime.datetime.now())

    jsonObject = json.dumps(writterData, indent=4)

    jsonFile = 'anotherTable.json'
    with open(jsonFile, "w") as outfile:
        outfile.write(jsonObject)


if __name__ == "__main__":
    main()
