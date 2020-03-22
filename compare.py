""" run the comparisons using asyncio """

import asyncio
import asks
import trio
import settings
import aiohttp
from quart import Quart, render_template, request
from wtforms import Form, StringField, validators
from datetime import datetime

app = Quart(__name__)


class AbstractForm(Form):
    abstract = StringField(
        "abstract",
        [
            validators.Length(
                min=25,
                max=10000,
                message="Your abstract must be between 25 and 10000 characters.",
            )
        ],
    )


def getlist(key):
    return self[key] if type(self[key]) == list else [self[key]]


@app.route("/", methods=["GET", "POST"])
async def index():
    """ display index page """
    form = AbstractForm([request.form])
    if request.method == "POST":
        comp = {}
        scores = {}
        if form.validate():
            inp = request.form.data["abstract"]
            t0 = datetime.now()
            asyncio.run(parent(inp))
            trio.run(tabulate, comp)
            print(scores)
            t1 = datetime.now()
            print(t1 - t0)

        else:
            return await render_template(
                "index.html", error_message=form.errors["abstract_field"][0]
            )

    else:
        return await render_template("index.html")


async def parent(inp):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[storageio(blob, inp, session) for blob in settings.bucket_list]
        )
    return


async def storageio(blob, inp, session):
    status = 0
    max_out = 0
    try:
        while (status != 200) and (max_out < 10):
            async with session.post(
                settings.cloud_function, json={"d": inp, "f": blob}
            ) as resp:
                print(resp.status, blob)
                status = resp.status
                max_out += 1
                comp[blob[10:19]] = await resp.text()
    except asyncio.TimeoutError:
        print("timeout")
        pass
    return


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
        title = "[Title lookup failed. Try finding this by ISSN instead...]"
    rank = idx + 1
    issn = item[0]
    score = item[1]
    scores[rank] = (issn, title, score)
    return


if __name__ == "__main__":
    app.run(port=8000, host="127.0.0.1", debug=True)
