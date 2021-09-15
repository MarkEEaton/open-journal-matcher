import json
import os
import spacy
import asyncio
from flask import Response
from google.cloud import storage

nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "ner", "lemmatizer"])

async def doaj_trio(request):
    try:
        encoded_data = request.data
        string_data = encoded_data.decode()
        data = json.loads(string_data)

        assert data["t"] == os.environ['token']
        client = storage.Client()
        bucket = client.get_bucket(os.environ['bucket'])

        blob = data["f"]
        print(blob)
            
        blob_object = bucket.get_blob(blob)
        raw_data = blob_object.download_as_text()
        journal_nlp = nlp(str(raw_data)[:100000])
        user_nlp = nlp(data["d"])
        sim = user_nlp.similarity(journal_nlp)
        return str(sim)

    except (AssertionError, KeyError, json.decoder.JSONDecodeError):
        return Response("403 Forbidden", status=403, mimetype="text/plain")
    except:
        raise
        return Response("500 Error", status=500, mimetype="text/plain")
