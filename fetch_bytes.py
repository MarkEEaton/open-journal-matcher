""" loop through the issns, gather abstracts and wite to abstracts/ """
import json
import os
import requests
import spacy
from time import sleep
from bs4 import BeautifulSoup

MONTH = "2021-12"
nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "ner", "lemmatizer", "attribute_ruler"])


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
    counter = 0
    print("Number of articles: " + str(len(articles)))
    for article in articles:
        try:
            abstract = article["bibjson"]["abstract"]
            abstract = BeautifulSoup(abstract, "lxml").text
            abstracts = abstracts + " " + abstract
            counter += 1
        except KeyError:
            pass
    if abstracts and counter >= 10:
        doc = nlp(abstracts)
        doc_bytes = doc.to_bytes()
    else:
        doc = None
        print("fail! " + str(counter))
    return doc


if __name__ == "__main__":
    with open("issnlist-" + MONTH + ".txt") as issnfile:
        issns = json.loads(issnfile.read())

    issns_output = []

    for idx, issn in enumerate(issns[:200]):
        if not os.path.exists("abstracts-" + MONTH + "/" + issn):
            articles = fetch(issn)
            doc = parse(articles)
            if not doc:
                # if the file does not exist but there is no data
                pass
            else:
                # if the file does not exist and there is data
                doc_bytes = doc.to_bytes()
                with open("abstracts-" + MONTH + "/" + issn, "wb") as abstractfile:
                    abstractfile.write(doc_bytes)
                os.makedirs("abstracts-" + MONTH + "/" + issn + "-vocab")
                doc.vocab.to_disk("abstracts-" + MONTH + "/" + issn + "-vocab")
                issns_output.append(issn)
        else:
            # if the file exists
            issns_output.append(issn)
            pass
    nlp.config.to_disk("abstracts-" + MONTH + "/config.cfg")
    with open("issns-" + MONTH + ".txt", "w") as issnfile:
        issnfile.write(json.dumps(issns_output))
