""" loop through the issns, gather abstracts and wite to abstracts/ """
import json
import requests
from time import sleep
from bs4 import BeautifulSoup


def fetch(issn):
    base_url = "https://doaj.org/api/v1/search/articles/issn%3A"
    pagesize = "?pageSize=100"

    data = requests.get(base_url + issn + pagesize)
    print(
        "fetching data for "
        + issn
        + ". "
        + str(idx + 1)
        + "/"
        + str(len(issns))
        + ". status: "
        + str(data.status_code)
    )
    try:
        articles = data.json().get("results")
    except:
        articles = ""
    status = str(data.status_code)
    if status == "429":
        sleep(10)
        print("forbidden")
        articles = fetch(issn)
    return articles


def parse(articles):
    abstracts = ""
    print('Number of articles: ' + str(len(articles)))
    for article in articles:
        try:
            abstract = article["bibjson"]["abstract"]
            abstract = BeautifulSoup(abstract, "lxml").text
            abstracts = abstracts + abstract
        except KeyError:
            pass
    return abstracts


if __name__ == "__main__":
    with open("issnlist.txt") as issnfile:
        issns = json.loads(issnfile.read())

    for idx, issn in enumerate(issns):
        articles = fetch(issn)
        abstracts = parse(articles)
        with open("abstracts/" + issn + ".txt", "w") as abstractfile:
            abstractfile.write(json.dumps(abstracts))
