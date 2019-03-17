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
    issns = ["1715-720X", "0003-9438", "0008-7629", "0011-393X"]
    pagesize = "?pageSize=100"
    abstracts = []

    for issn in issns:
        print("fetching data for..." + issn)
        data = requests.get(base_url + issn + pagesize)
        articles = data.json().get("results")

        nex = data.json().get("next")

        while nex:
            data = requests.get(nex).json()
            new_articles = data.get("results")
            articles = articles + new_articles
            nex = data.get("next")

        print("removing html tags...")
        cat_abstracts = ""
        for article in articles:
            try:
                abstract = article["bibjson"]["abstract"]
                abstract = BeautifulSoup(abstract, "lxml").text
                cat_abstracts = cat_abstracts + abstract
            except KeyError:
                pass
        abstracts.append(cat_abstracts)

    return abstracts


if __name__ == "__main__":
    abstracts = fetch()
    print("parsing parts of speech...")
    print(abstracts)
    print(len(abstracts))

    """
    tagged = nltk.pos_tag(nltk.word_tokenize(abstracts))

    nouns = parse.get_nouns(tagged)
    pprint(nouns)

    verbs = parse.get_verbs(tagged)
    pprint(verbs)

    proper_names = parse.get_proper_names(tagged)
    pprint(proper_names)
    """
