import spacy
import glob
import collections
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

print(sorted(comp.items(), key=lambda x: x[1]))