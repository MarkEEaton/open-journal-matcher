import json
import requests
from time import sleep
from bs4 import BeautifulSoup


def fetch(issn):
    base_url = "https://doaj.org/api/v1/search/articles/issn%3A"
    pagesize = "?pageSize=100"

    data = requests.get(base_url + issn + pagesize)
    print("fetching data for " + issn + ". " + str(idx + 1) + "/" + str(len(issns)) + '. status: ' + str(data.status_code))
    articles = data.json().get("results")

    nex = data.json().get("next")

    while nex:
        data = requests.get(nex).json()
        sleep(2)
        new_articles = data.get("results")
        if articles and new_articles:
            articles = articles + new_articles
        nex = data.get("next")

    abstracts = ""
    for article in articles:
        try:
            abstract = article["bibjson"]["abstract"]
            abstract = BeautifulSoup(abstract, "lxml").text
            abstracts = abstracts + abstract
        except KeyError:
            pass
    return abstracts


if __name__ == "__main__":
    with open('issnlist.txt') as issnfile:
        issns = json.loads(issnfile.read())

    for idx, issn in enumerate(issns):
        abstracts = fetch(issn)
        with open("abstracts/" + issn + '.txt', 'w') as abstractfile:
            abstractfile.write(json.dumps(abstracts))
