import os
import spacy
from configparser import ConfigParser
from flask import Response, request
from google.cloud import storage

nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "ner", "lemmatizer"])

def doaj_trio(request):
    try:
        user_nlp = request.data
        blob = request.headers.get('blob')

        client = storage.Client()
        bucket = client.get_bucket(os.environ['bucket'])

        config_blob = bucket.get_blob('config.cfg')
        config_text = config_blob.download_as_text()
        config = ConfigParser(allow_no_value=True)
        config.read_string(config_text)

        lang_cls = spacy.util.get_lang_class(config["nlp"]["lang"])
        nlp = lang_cls.from_config(config)
        user = nlp.from_bytes(user_nlp)

        blob_object = bucket.get_blob(blob)
        journal_nlp = blob_object.download_as_bytes()
        journal = nlp.from_bytes(journal_nlp)
        sim = user.similarity(journal)
        return str(sim)

    except:
        raise
