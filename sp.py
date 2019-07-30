""" write out the vectorized journals to docs/ directory """

import json
import spacy
from pathlib import Path

nlp = spacy.load("en_core_web_md")
counter = 0

pathlist = Path("abstracts/").glob("*.txt")
for path in list(pathlist):
    with open(str(path)) as ab:
        data = json.loads(ab.read())
    counter += 1
    print("processing: " + str(path) + " #" + str(counter))
    outpath = str(path)[10:19]
    with open("docs/{}".format(outpath), "wb") as outfile:
        n_data = nlp(data[:99999])
        outfile.write(n_data.to_bytes())
