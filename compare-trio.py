""" run the comparisons in a flask app """
""" non async runs at 7.3 to 7.5 with [:20] """

import spacy
import trio
import glob
import collections
import requests
from spacy.tokens import Doc
from datetime import datetime


nlp = spacy.load("en_core_web_md")
comp = {}

inp = input("Abstract: ")
abs_data = nlp(inp)
counter = 0

t0 = datetime.now()

async def parent(counter):
    print('running parent')
    async with trio.open_nursery() as nursery:
        for item in glob.glob("docs/*")[:80]:
            counter += 1
            nursery.start_soon(fileio, item)
            print(item, counter)
    
async def fileio(item):
    print("opening file")
    with open(item, "rb") as item_data:
        data = Doc(nlp.vocab).from_bytes(item_data.read())
        print(abs_data.similarity(data))
        comp[item[5:]] = abs_data.similarity(data)

trio.run(parent, counter)

print("sorting")
top = sorted(comp.items(), key=lambda x: x[1], reverse=True)[:5]

print("get journal info from API")
for item in top:
    journal_data = requests.get(
        "https://doaj.org/api/v1/search/journals/issn%3A" + item[0]
    )
    journal_json = journal_data.json()
    title = journal_json["results"][0]["bibjson"]["title"]
    issn = item[0]
    score = item[1]
    print(issn, title)

t1 = datetime.now()
print(t1 - t0)