import json
import os
import spacy
from flask import request
from google.cloud import storage
from spacy.tokens import Doc
from spacy.vocab import Vocab

nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "ner", "attribute_ruler", "lemmatizer"])

def doaj_trio(request):
    try:
        encoded_data = request.data
        string_data = encoded_data.decode()
        data = json.loads(string_data)
        user_nlp = nlp(data['inp'])

        blob = request.headers.get('blob')

        client = storage.Client()
        bucket = client.get_bucket(os.environ['bucket'])

        blob_object = bucket.get_blob(blob)
        blob_bytes = blob_object.download_as_bytes()
        blob_vocab_object = bucket.get_blob(blob + '-vocab')
        blob_vocab_bytes = blob_vocab_object.download_as_bytes()
        journal_nlp = Doc(Vocab()).from_bytes(blob_bytes)
        journal_nlp.vocab.from_bytes(blob_vocab_bytes)

        sim = user_nlp.similarity(journal_nlp)
        return str(sim)

    except:
        raise

