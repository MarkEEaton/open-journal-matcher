import spacy
import glob
import collections
import requests
from spacy.tokens import Doc

nlp = spacy.load('en_core_web_lg')
comp = {}

abstract = input('abstract: ')
abs_data = nlp(abstract)

for item in glob.glob('docs/*'):
    print(item)
    with open(item, 'rb') as item_data:
        data = Doc(nlp.vocab).from_bytes(item_data.read())
        print(abs_data.similarity(data))
        comp[item[5:]] =  abs_data.similarity(data)

top = sorted(comp.items(), key=lambda x: x[1], reverse=True)[:5]

for item in top:
    journal_data = requests.get('https://doaj.org/api/v1/search/journals/issn%3A' + item[0])
    journal_json = journal_data.json()
    title = journal_json['results'][0]['bibjson']['title']
    issn = item[0]
    score = item[1]
    print(title, issn, score)
