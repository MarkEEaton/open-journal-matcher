""" run the comparisons in a flask app """

import spacy
import glob
import collections
import requests
from spacy.tokens import Doc
from flask import Flask, render_template, request
from wtforms import Form, StringField, validators

nlp = spacy.load("en_core_web_md")
comp = {}

app = Flask(__name__)

class RegistrationForm(Form):
    abstract = StringField('abstract', [validators.length(min=25, max=10000, message="Your abstract must be between 25 and 10000 characters.")])


@app.route("/", methods=["GET", "POST"])
def index():
    """ display index page """
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():

        abs_data = nlp(form.abstract.data)

        for item in glob.glob("docs/*"):
            print(item)
            with open(item, "rb") as item_data:
                data = Doc(nlp.vocab).from_bytes(item_data.read())
                print(abs_data.similarity(data))
                comp[item[5:]] = abs_data.similarity(data)

        top = sorted(comp.items(), key=lambda x: x[1], reverse=True)[:5]

        for item in top:
            journal_data = requests.get(
                "https://doaj.org/api/v1/search/journals/issn%3A" + item[0]
            )
            journal_json = journal_data.json()
            title = journal_json["results"][0]["bibjson"]["title"]
            issn = item[0]
            score = item[1]
        return render_template("index.html", title=title, issn=issn, score=score)

    elif request.method == "POST" and not form.validate():
        return render_template("index.html", error_message=form.errors['abstract'][0]) 

    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(port=8000, host="127.0.0.1", debug=True)
