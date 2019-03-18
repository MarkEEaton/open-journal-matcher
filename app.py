import parse
import json
import requests
import nltk
from time import sleep
from bs4 import BeautifulSoup
from pprint import pprint
from collections import Counter

nltk.download("maxent_ne_chunker")
nltk.download("words")
nltk.download("wordnet")
nltk.download("stopwords")


def fetch(issns):
    base_url = "https://doaj.org/api/v1/search/articles/issn%3A"
    pagesize = "?pageSize=100"
    abstracts = {}

    for idx, issn in enumerate(issns):
        data = requests.get(base_url + issn + pagesize)
        print("fetching data for " + issn + ". " + str(idx + 1) + "/" + str(len(issns)) + '. status: ' + str(data.status_code))
        articles = data.json().get("results")

        nex = data.json().get("next")

        while nex:
            data = requests.get(nex).json()
            print(data.status_code)
            sleep(2)
            new_articles = data.get("results")
            if articles and new_articles:
                articles = articles + new_articles
            nex = data.get("next")

        cat_abstracts = ""
        for article in articles:
            try:
                abstract = article["bibjson"]["abstract"]
                abstract = BeautifulSoup(abstract, "lxml").text
                cat_abstracts = cat_abstracts + abstract
            except KeyError:
                pass
        abstracts[issn] = cat_abstracts

    return abstracts


if __name__ == "__main__":
    with open('issnlist.txt') as issnfile:
        issns = json.loads(issnfile.read())

    abstracts = fetch(issns[:100])
    print(len(abstracts))
    with open('abstractlist.txt', 'w') as abstractfile:
        abstractfile.write(json.dumps(abstracts))

    """
    tagged = nltk.pos_tag(nltk.word_tokenize(abstracts))

    nouns = parse.get_nouns(tagged)
    pprint(nouns)

    verbs = parse.get_verbs(tagged)
    pprint(verbs)

    proper_names = parse.get_proper_names(tagged)
    pprint(proper_names)
    """
