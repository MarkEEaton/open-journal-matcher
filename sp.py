import json
import spacy


nlp = spacy.load('en_core_web_lg')


with open('abstractlist.txt') as ab:
    data = json.loads(ab.read())

tokenized = []

print('looping')
for key in list(data)[2:4]:
    print('processing: ' + str(key))
    tokenized.append(nlp(data[key][:99999]))

print(tokenized[0].similarity(tokenized[1]))

