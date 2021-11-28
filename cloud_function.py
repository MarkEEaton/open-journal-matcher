import os
import spacy
from flask import Response, request
from google.cloud import storage
from spacy.tokens import Doc
from thinc.api import Config


def doaj_trio(request):
    try:
        user_nlp = request.data
        blob = request.headers.get('blob')

        client = storage.Client()
        bucket = client.get_bucket(os.environ['bucket'])

        config_blob = bucket.get_blob(os.environ['config'])
        config_text = config_blob.download_as_text()
        config = Config().from_str(config_text)

        blob_object = bucket.get_blob(blob)
        journal_nlp = blob_object.download_as_bytes()

        lang_cls = spacy.util.get_lang_class(config["nlp"]["lang"])
        nlp = lang_cls.from_config(config)
        user_sim = Doc(nlp.vocab).from_bytes(user_nlp)
        journal_sim = Doc(nlp.vocab).from_bytes(journal_nlp)

        sim = user_sim.similarity(journal_sim)
        return str(sim)

    except:
        raise
