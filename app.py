import parse
import requests
import nltk
from bs4 import BeautifulSoup
from pprint import pprint
from collections import Counter

nltk.download("maxent_ne_chunker")
nltk.download("words")
nltk.download("wordnet")
nltk.download("stopwords")


def fetch():
    base_url = "https://doaj.org/api/v1/search/articles/issn%3A"
    issn = "1715-720X"
    pagesize = "?pageSize=100"

    print("fetching data...")
    data = requests.get(base_url + issn + pagesize)
    articles = data.json().get("results")

    nex = data.json()["next"]

    while nex:
        data = requests.get(nex).json()
        new_articles = data.get("results")
        articles = articles + new_articles
        nex = data.get("next")

    print("removing html tags...")
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
    abstracts = fetch()
    print("parsing parts of speech...")
    tagged = nltk.pos_tag(nltk.word_tokenize(abstracts))

    nouns = parse.get_nouns(tagged)
    pprint(nouns)

    verbs = parse.get_verbs(tagged)
    pprint(verbs)

    proper_names = parse.get_proper_names(tagged)
    pprint(proper_names)
