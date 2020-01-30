""" run the comparisons using trio (async) """

import asks
import multio
import trio
import glob
import requests
import base64
import settings
from datetime import datetime

comp = {}
inp = input("Abstract: ")
counter = 0
t0 = datetime.now()


async def parent(counter, inp):
    print("running parent")
    async with trio.open_nursery() as nursery:
        for item in glob.glob("abstracts-sample/*"):
            counter += 1
            nursery.start_soon(fileio, item, inp)


async def fileio(item, inp):
    async with await trio.open_file(item, mode="r") as i:
        raw_data = await i.read()
    resp = await asks.post(
        settings.cloud_function, 
        json={"d": inp, "e": raw_data})
    comp[item[17:]] = resp.text 
    print(resp.text)
    return


multio.init("trio")
trio.run(parent, counter, inp)

def test_response(resp):
    try:
        return float(resp)  # will evaluate as false if float == 0.0
    except ValueError:
        return False

print("sorting")
to_sort = [(k, v) for k, v in comp.items() if test_response(v)]
top = sorted(to_sort, key=lambda x: x[1], reverse=True)[:5]
print(top)

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
