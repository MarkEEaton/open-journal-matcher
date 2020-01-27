""" run the comparisons using trio (async) """

import spacy
import trio
import glob
import requests
import base64
import settings
from datetime import datetime


nlp = spacy.load("en_core_web_md")
comp = {}

inp = input("Abstract: ")
abs_data = nlp(inp)
counter = 0

t0 = datetime.now()


async def parent(counter, abs_data):
    print("running parent")
    async with trio.open_nursery() as nursery:
        for item in glob.glob("docs-md/*")[:30]:
            counter += 1
            nursery.start_soon(fileio, item, abs_data)


async def fileio(item, abs_data):
    with open(item, "rb") as i:
        resp = requests.post(settings.cloud_function, data={"d": [[abs_data]], "e": base64.b64encode(i.read())})
    #comp[item[8:]] = score
    print(resp.text)


trio.run(parent, counter, abs_data)

"""
print("sorting")
top = sorted(comp.items(), key=lambda x: x[1], reverse=True)[:5]

print("get journal info from API")
for item in top:
    journal_data = requests.get(
        "https://doaj.org/api/v1/search/journals/issn%3A" + item[0]
    )
    journal_json = journal_data.json()
    try:
        title = journal_json["results"][0]["bibjson"]["title"]
    except:
        title = " "
    issn = item[0]
    score = item[1]
    print(issn, title)

t1 = datetime.now()
print(t1 - t0)
"""
