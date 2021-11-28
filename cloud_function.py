import os
import spacy
from flask import Response, request
from google.cloud import storage
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
        nlp1 = lang_cls.from_config(config)
        nlp2 = lang_cls.from_config(config)
        nlp1.from_bytes(user_nlp)
        nlp2.from_bytes(journal_nlp)

        sim = nlp2.similarity(nlp1)
        return str(sim)

    except:
        raise

