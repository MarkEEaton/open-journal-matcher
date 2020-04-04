""" run the comparisons using asyncio """

import time
import asyncio
import asks
import trio
import settings
import aiohttp
import secrets
from flask_bootstrap import Bootstrap
from collections import OrderedDict
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length
from flask import Flask, render_template, request, url_for, Response
from datetime import datetime

app = Flask(__name__, static_url_path="/static")
Bootstrap(app)
app.config["SECRET_KEY"] = secrets.token_hex()


class WebForm(FlaskForm):
    """ for validation """

    web_abstract_var = TextAreaField(
        validators=[
            Length(
                min=25,
                max=10000,
                message="Your abstract must be between 25 and 10000 characters",
            )
        ],
    )
    submit = SubmitField("Search")


@app.route("/", methods=["GET", "POST"])
def index():
    """ display index page """
    global READ
    READ = 0
    form = WebForm()
    if request.method == "POST" and form.validate_on_submit():
        comp = {}
        unordered_scores = {}
        inp = form.web_abstract_var.data
        print(inp)
        t0 = datetime.now()

        # do the work
        asyncio.run(parent(inp, comp))
        trio.run(tabulate, comp, unordered_scores)

        # sort the results
        scores = OrderedDict(
            sorted(unordered_scores.items(), key=lambda t: t[0], reverse=True)
        )

        # calculate running time
        t1 = datetime.now()
        print(t1 - t0)

        return render_template("index.html", form=form, output=scores)

    elif request.method == "POST" and not form.validate_on_submit():
        return render_template("index.html", form=form, output=form.errors)

    else:
        return render_template("index.html", form=form, output="")


@app.route('/progress')
def progress():
    def generate():
        while READ <= 100:
            return "data:" + str(READ) + "\n\n" + "retry: 5\n\n"

    return Response(generate(), mimetype='text/event-stream')


async def parent(inp, comp):
    """ manage the async work """
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[storageio(blob, inp, session, comp) for blob in settings.bucket_list]
        )
    return


async def storageio(blob, inp, session, comp):
    """ interact with google cloud function """
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
    global READ
    READ += 1 / len(settings.bucket_list) * 100
    return


def test_response(resp):
    """ some abstract collections raise ValueErrors. Ignore these """
    try:
        return float(resp)  # will evaluate as false if float == 0.0
    except ValueError:
        return False


async def tabulate(comp, unordered_scores):

    # test for validity
    to_sort = [(k, v) for k, v in comp.items() if test_response(v)]
    print("Journals checked:" + str(len(to_sort)))

    # this sort is needed to reduce API calls to doaj.org
    top = sorted(to_sort, key=lambda x: x[1], reverse=True)[:5]

    # make calls to the doaj API asynchronously
    async with trio.open_nursery() as nursery:
        for idx, item in enumerate(top):
            nursery.start_soon(titles, idx, item, unordered_scores)
    return


async def titles(idx, item, unordered_scores):
    journal_data = await asks.get(
        "https://doaj.org/api/v1/search/journals/issn%3A" + item[0]
    )
    journal_json = journal_data.json()
    try:
        title = journal_json["results"][0]["bibjson"]["title"]
        if title[-1:] == " ":
            title = title[:-1]
    except:
        title = "[Title lookup failed. Try finding this item by ISSN instead...]"
    rank = idx + 1
    issn = item[0]
    score = float(item[1]) * 100
    unordered_scores[score] = (title, issn)
    return


if __name__ == "__main__":
    app.run(port=8000, host="127.0.0.1", debug=True)
