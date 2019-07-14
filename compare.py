import spacy
import glob
import collections
import requests
from spacy.tokens import Doc
from flask import Flask, render_template, request

nlp = spacy.load('en_core_web_md')
comp = {}

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """ display index page """
    if request.method == "GET":
        return render_template('index.html')
    
    else:
        abs_data = nlp(abstract)

        for item in glob.glob('docs/*'):
            print(item)
            with open(item, 'rb') as item_data:
                data = Doc(nlp.vocab).from_bytes(item_data.read())
                print(abs_data.similarity(data))
                comp[item[5:]] = abs_data.similarity(data)


        top = sorted(comp.items(), key=lambda x: x[1], reverse=True)[:5]

        for item in top:
            journal_data = requests.get('https://doaj.org/api/v1/search/journals/issn%3A' + item[0])
            journal_json = journal_data.json()
            title = journal_json['results'][0]['bibjson']['title']
            issn = item[0]
            score = item[1]
            data = [title, issn, score]
        return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(port=8000, host="127.0.0.1", debug=True)