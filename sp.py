import json
import spacy


nlp = spacy.load('en_core_web_lg')


with open('abstractlist.txt') as ab:
    data = json.loads(ab.read())

print('looping')
for key in list(data):
    print('processing: ' + str(key))
    with open('docs/{}'.format(key), 'wb') as outfile:
        n_data = nlp(data[key][:99999])
        outfile.write(n_data.to_bytes())

