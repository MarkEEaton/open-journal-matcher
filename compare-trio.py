""" run the comparisons using trio (async) """

import asyncio
import asks
import trio
import settings
from time import sleep
from google.cloud import storage
from glob import glob
from datetime import datetime
from gcloud.aio.storage import Storage
from aiohttp import ClientSession as Session

comp = {}
scores = {}
inp = input("Abstract: ")
counter = 0
t0 = datetime.now()


async def parent(counter, inp):
    print("running parent")
    async with Session() as session:
        storage = Storage(session=session)
        bucket = storage.get_bucket(settings.bucket_name)
        blobs = await bucket.list_blobs()
        await asyncio.gather(*[fileio(x, inp, bucket) for x in blobs])
    return


async def fileio(blob, inp, bucket):
    print("start fileio")
    status = 0
    max_out = 0
    blob_object = await bucket.get_blob(blob)
    raw_data = await blob_object.download()
    print("start while")
    while (status != 200) and (max_out <= 10):
        resp = await asks.post(settings.cloud_function, json={"d": inp, "e": str(raw_data)})
        print(resp.status_code, blob_object.name)
        status = resp.status_code
        if status == 503:
            # truncate the data if there is a memory error
            raw_data = raw_data[:100000]
        print(max_out)
        max_out += 1
    print(blob.name)
    comp[blob.name[10:19]] = resp.text
    return 


asyncio.run(parent(counter, inp))
print("Counter: " + str(counter))

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
    return


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
