import requests
import time
import asks
import trio
import settings
import secrets
try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass
from celery import Celery, group
from celery.decorators import task
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length
from flask import Flask, render_template, request, url_for, Response
from datetime import datetime

print("libraries loaded...")

app = Flask(__name__, static_url_path="/static")
Bootstrap(app)
app.config["SECRET_KEY"] = secrets.token_hex()

celery_app = Celery("compare", backend="rpc://", broker=settings.local_broker)


class WebForm(FlaskForm):
    """ for validation """

    web_abstract_var = TextAreaField(
        validators=[
            Length(
                min=25,
                max=10000,
                message="Your abstract must be between 25 and 10000 characters.",
            )
        ],
    )
    submit = SubmitField("Search")


@app.route("/", methods=["GET", "POST"])
def index():
    """ display index page """
    print("index function called...")
    form = WebForm()
    if request.method == "POST" and form.validate_on_submit():
        celery_app.control.purge()
        inp = form.web_abstract_var.data
        print(inp)
        t0 = datetime.now()

        # do the work
        job = group([storageio.s(blob, inp) for blob in settings.bucket_list])
        result = job.apply_async()
        result = result.get()

        scores = sorted(result, key=lambda t: t[1], reverse=True)

        output = {}
        trio.run(tabulate, scores[:5], output)
        output_list = [v for v in output.values()]
        sorted_output = sorted(output_list, key=lambda t: t[0], reverse=True)

        # calculate running time
        t1 = datetime.now()
        print(t1 - t0)

        return render_template("index.html", form=form, errors={}, output=sorted_output)

    elif request.method == "POST" and not form.validate_on_submit():
        celery_app.control.purge()
        return render_template("index.html", form=form, errors=form.errors, output="")

    else:
        print("at render...")
        #celery_app.control.purge()
        return render_template("index.html", form=form, errors={}, output="")


@task(name="access_storage")
def storageio(blob, inp):
    """ interact with google cloud function """
    status = 0
    max_out = 0
    while (status != 200) and (max_out < 10):
        with requests.post(settings.cloud_function, json={"d": inp, "f": blob}) as resp:
            print(resp.status_code, blob)
            status = resp.status_code
            max_out += 1
    return (blob[10:19], resp.text)


def test_response(resp):
    """ some abstract collections raise ValueErrors. Ignore these. """
    try:
        return float(resp)  # will evaluate as false if float == 0.0
    except ValueError:
        return False


async def tabulate(scores, output):

    # test for validity
    tested = [[item[0], item[1]] for item in scores if test_response(item[1])]
    print("Journals checked:" + str(len(tested)))

    # make calls to the doaj API asynchronously
    async with trio.open_nursery() as nursery:
        for item in tested:
            nursery.start_soon(titles, item, output)
    return


async def titles(item, output):
    journal_data = await asks.get(
        "https://doaj.org/api/v1/search/journals/issn%3A" + item[0]
    )
    journal_json = journal_data.json()
    try:
        title = journal_json["results"][0]["bibjson"]["title"]
        if title[-1:] == " ":
            title = title[:-1]
    except:
        title = "Title lookup failed. Try finding this item by ISSN instead.."
    issn = item[0]
    score = float(item[1]) * 100
    output[issn] = [score, title, issn]
    return


if __name__ == "__main__":
    app.run(port=8000, host="127.0.0.1", debug=True)
