""" loop through the issns, gather abstracts and wite to abstracts/ """
import json
import os
import requests
import spacy
from time import sleep
from bs4 import BeautifulSoup

MONTH = "2021-09"
nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "ner", "lemmatizer"])

def fetch(issn):
    base_url = "https://doaj.org/api/v1/search/articles/issn%3A"
    pagesize = "?pageSize=100&sort=year%3Adesc"

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
    if len(articles) <= 10:
        return abstracts
    for article in articles:
        try:
            abstract = article["bibjson"]["abstract"]
            abstract = BeautifulSoup(abstract, "lxml").text
            abstracts = abstracts + " " + abstract
            doc = nlp(abstracts)
            doc_bytes = doc.to_bytes()
        except KeyError:
            doc_bytes = None
            pass
    return doc_bytes


if __name__ == "__main__":
    with open("issnlist-" + MONTH + ".txt") as issnfile:
        issns = json.loads(issnfile.read())

    issns_output = []
    
    for idx, issn in enumerate(issns):
        if not os.path.exists("abstracts-" + MONTH + "/" + issn):
            articles = fetch(issn)
            doc_bytes = parse(articles)
            if not doc_bytes:
                pass
            else:
                with open("abstracts-" + MONTH + "/" + issn, "wb") as abstractfile:
                    abstractfile.write(doc_bytes)
                issns_output.append(issn)
        else:
            issns_output.append(issn)
    nlp.config.to_disk("abstracts-" + MONTH + "/config.cfg")
    with open("issns-" + MONTH + ".txt", "w") as issnfile:
        issnfile.write(json.dumps(issns_output))
