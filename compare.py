""" run the comparisons using asyncio """

import asyncio
import asks
import regex
import settingsnovember2020 as settings
import aiohttp
import langdetect
import os
import schedule
from time import sleep
from flask_bootstrap import Bootstrap
from collections import OrderedDict
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length, ValidationError
from flask import Flask, render_template, request, url_for, Response, abort
from datetime import datetime
from redislite import StrictRedis

app = Flask(__name__, static_url_path="/static")
Bootstrap(app)
app.config["SECRET_KEY"] = settings.csrf
REDIS = os.path.join("/tmp/redis.db")
r = StrictRedis(REDIS, charset="utf-8", decode_responses=True)
r.hset("counter", "increment", 0)


def reset_redis():
    r.hset("counter", "increment", 0)


schedule.every().hour.do(reset_redis)


class WebForm(FlaskForm):
    """ for validation """

    webabstract = TextAreaField(
        validators=[
            Length(
                min=150,
                max=10000,
                message="Your abstract must be between 150 and 10,000 characters.",
            )
        ]
    )

    def validate_webabstract(form, field):
        try:
            language = langdetect.detect(field.data)
        except langdetect.lang_detect_exception.LangDetectException:
            raise ValidationError(
                "Your abstract must be between 150 and 10,000 characters."
            )
        print(language)
        if language != "en":
            raise ValidationError(
                "The Open Journal Matcher only works with abstracts written in English."
            )

    submit = SubmitField("Search")


@app.route("/", methods=["GET", "POST"])
def index():
    """ display index page """
    form = WebForm()
    valid = form.validate_on_submit()
    schedule.run_pending()
    if request.method == "POST" and valid:

        # check to ensure not over rate limit
        counter = int(r.hget("counter", "increment"))
        counter += 1
        print("counter:", counter)
        if counter >= 40:
            rate_error = {
                "webabstract": [
                    "The application is experiencing peak load. Please try again later."
                ]
            }
            return render_template(
                "index.html", form=form, errors=rate_error, output=""
            )
        r.hset("counter", "increment", counter)

        # lay the groundwork
        comp = {}
        unordered_scores = {}
        inp = form.webabstract.data
        t0 = datetime.now()

        # do the work
        asyncio.run(parent1(inp, comp))
        asyncio.run(parent2(comp, unordered_scores))

        # sort the results
        scores = OrderedDict(
            sorted(unordered_scores.items(), key=lambda t: t[0], reverse=True)
        )

        # calculate running time
        t1 = datetime.now()
        print(t1 - t0)

        return render_template("index.html", form=form, errors={}, output=scores)

    elif request.method == "POST" and not valid:
        return render_template("index.html", form=form, errors=form.errors, output="")

    else:
        return render_template("index.html", form=form, errors={}, output="")


@app.after_request
def add_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["X-XSS-Protection"] = "1; mode=block"
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    resp.headers[
        "Content-Security-Policy"
    ] = "script-src 'self'; style-src 'self'; default-src 'none'"
    return resp


async def parent1(inp, comp):
    """ manage the async calls to GCP """
    await asyncio.gather(
        *[cloud_work(blob, inp, comp, 0) for blob in settings.bucket_list]
    )
    return


async def cloud_work(blob, inp, comp, count):
    """ interact with google cloud function """
    max_out = 0
    try:
        async with aiohttp.ClientSession() as session:
            while max_out < 16:
                async with session.post(
                    settings.cloud_function,
                    json={"d": inp, "f": blob, "t": settings.token},
                ) as resp:
                    if max_out >= 15:
                        raise Exception("Max out")
                    if resp.status == 200:
                        comp[blob[10:19]] = await resp.text()
                        break
                    elif resp.status == 500:
                        max_out += 1
                    elif resp.status == 429:
                        sleep(0.01)
                    else:
                        raise Exception(str(resp.status))
    except (
        aiohttp.client_exceptions.ClientConnectorError,
        aiohttp.client_exceptions.ServerDisconnectedError,
        asyncio.TimeoutError,
    ) as e:
        # print(type(e), e, str(count))
        if count < 5:
            await cloud_work(blob, inp, comp, count + 1)
    except Exception as e:
        print(type(e), e)
    return


async def parent2(comp, unordered_scores):
    """ manage the async calls to the DOAJ api """

    # test for validity
    to_sort = [(k, v) for k, v in comp.items() if test_response(v)]
    print("Journals checked:" + str(len(to_sort)))

    # this sort is needed to reduce API calls to doaj.org
    top = sorted(to_sort, key=lambda x: x[1], reverse=True)[:5]

    # make calls to the doaj API asynchronously
    await asyncio.gather(
        *[titles(idx, item, unordered_scores) for idx, item in enumerate(top)]
    )
    return


def test_response(resp):
    """ some abstract collections raise ValueErrors. Ignore these """
    try:
        return float(resp)  # will evaluate as false if float == 0.0
    except ValueError:
        return False


async def titles(idx, item, unordered_scores):
    if regex.match(r"^[0-9]{4}-[0-9]{3}[0-9Xx]$", item[0]):
        issn = item[0]
    else:
        raise Exception("ISSN does not match regex")

    journal_data = await asks.get(
        "https://doaj.org/api/v2/search/journals/issn%3A" + issn
    )
    journal_json = journal_data.json()

    try:
        title = journal_json["results"][0]["bibjson"]["title"]
        if title[-1:] == " ":
            title = title[:-1]
        url = "https://doaj.org/toc/" + issn
    except:
        title = "Title lookup failed. Try finding this item by ISSN instead.."
        url = ""
    score = float(item[1]) * 100
    unordered_scores[score] = (title, issn, url)
    return


if __name__ == "__main__":
    app.run()
