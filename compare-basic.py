""" run the comparisons using the most basic approach """

import spacy
import glob
import requests
from spacy.tokens import Doc
from datetime import datetime


nlp = spacy.load("en_core_web_md")
comp = {}

inp = input("Abstract: ")
abs_data = nlp(inp)
counter = 0
result = []

t0 = datetime.now()


def fio(item):
    with open(item, "rb") as item_data:
        data = Doc(nlp.vocab).from_bytes(item_data.read())
        print(abs_data.similarity(data))
        return (abs_data.similarity(data), item[-9:])


gl = list(glob.glob("docs/*"))
for item in gl:
    result.append(fio(item))

print("sorting")
top = sorted(result, key=lambda x: x[1], reverse=True)[:5]

print("get journal info from API")
for item in top:
    journal_data = requests.get(
        "https://doaj.org/api/v1/search/journals/issn%3A" + item[1]
    )
    issn = item[1]
    score = item[0]
    if journal_data.status_code == 200:
        journal_json = journal_data.json()
        title = journal_json["results"][0]["bibjson"]["title"]
        print(issn, title, score)
    else:
        print(issn, score)

t1 = datetime.now()
print(t1 - t0)
