import requests
import nltk
from bs4 import BeautifulSoup
from pprint import pprint
from collections import Counter
from nltk.tree import Tree
from nameparser.parser import HumanName

nltk.download("maxent_ne_chunker")
nltk.download("words")
nltk.download("wordnet")


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


def get_nouns(text):
    print("collecting nouns...")

    nouns = []
    for item in tagged:
        if item[1] == "NN":
            nouns.append(item[0])
    return Counter(nouns)


def get_proper_names(text):
    print("collecting proper names...")

    sentt = nltk.ne_chunk(text, binary=False)
    person_list = []
    person = []
    name = ""
    print("checking names against a dictionary...")
    for subtree in sentt.subtrees(filter=lambda t: t.label() == "PERSON"):
        for leaf in subtree.leaves():
            if not nltk.corpus.wordnet.synsets(leaf[0]):
                person.append(leaf[0])
        #if len(person) > 1:  # avoid grabbing lone surnames
        for part in person:
            name += part + " "
        person_list.append(name[:-1])
        name = ""
        person = []

    return Counter(person_list)


if __name__ == "__main__":
    abstracts = fetch()
    print("parsing parts of speech...")
    tagged = nltk.pos_tag(nltk.word_tokenize(abstracts))
    nouns = get_nouns(tagged)
    pprint(nouns.most_common(20))
    proper_names = get_proper_names(tagged)
    pprint(proper_names.most_common(20))
