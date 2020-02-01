""" run the comparisons using trio (async) """

import asks
import trio
import settings
from glob import glob
from datetime import datetime

comp = {}
scores = {}
inp = input("Abstract: ")
counter = 0
t0 = datetime.now()


async def parent(counter, inp):
    print("running parent")
    async with trio.open_nursery() as nursery:
        for item in glob("abstracts/*"):
            counter += 1
            nursery.start_soon(fileio, item, inp)


async def fileio(item, inp):
    status = 0
    max_out = 0
    async with await trio.open_file(item, mode="r") as i:
        # don't use binary here because plain text is easier to send over the wire
        raw_data = await i.read()
    while (status != 200) and (max_out <= 10):
        resp = await asks.post(settings.cloud_function, json={"d": inp, "e": raw_data})
        status = resp.status_code
        if status == 503:
            # truncate the data if there is a memory error
            raw_data = raw_data[:100000]
        max_out += 1
    comp[item[10:19]] = resp.text
    return


trio.run(parent, counter, inp)


def test_response(resp):
    try:
        return float(resp)  # will evaluate as false if float == 0.0
    except ValueError:
        return False


async def tabulate(data):
    to_sort = [(k, v) for k, v in comp.items() if test_response(v)]
    print("Journals checked:" + str(len(to_sort)))
    top = sorted(to_sort, key=lambda x: x[1], reverse=True)[:5]

    async with trio.open_nursery() as nursery:
        for idx, item in enumerate(top):
            nursery.start_soon(titles, idx, item)


async def titles(idx, item):
    journal_data = await asks.get(
        "https://doaj.org/api/v1/search/journals/issn%3A" + item[0]
    )
    journal_json = journal_data.json()
    try:
        title = journal_json["results"][0]["bibjson"]["title"]
    except:
        title = "[title not found... look up by ISSN]"
    rank = idx + 1
    issn = item[0]
    score = item[1]
    scores[rank] = (issn, title, score)
    return


trio.run(tabulate, comp)
print(scores)
t1 = datetime.now()
print(t1 - t0)
