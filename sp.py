""" write out the vectorized journals to docs/ directory """

import json
import spacy
from pathlib import Path

nlp = spacy.load("en_core_web_lg")

pathlist = Path("abstracts/").glob("*.txt")
for path in pathlist:
    with open(str(path)) as ab:
        data = json.loads(ab.read())

    print("processing: " + str(path))
    outpath = str(path)[10:19]
    with open("docs/{}".format(outpath), "wb") as outfile:
        n_data = nlp(data[:99999])
        outfile.write(n_data.to_bytes())
