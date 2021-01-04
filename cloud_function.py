import json
import spacy
import asyncio
from flask import Response
from aiohttp import ClientSession as Session
from gcloud.aio.storage import Storage

nlp = spacy.load("en_core_web_md", disable=["tagger", "parser", "ner"])
    
async def doaj_trio(request):
    try:
        encoded_data = request.data
        string_data = encoded_data.decode()
        data = json.loads(string_data)
        if data["t"] == settings.token:
            async with Session() as session:
                storage = Storage(session=session)
                bucket = storage.get_bucket(settings.bucket_name)
                blob = data["f"]
                print(blob)
                blob_object = await bucket.get_blob(blob)
                raw_data = await blob_object.download()

                journal_nlp = nlp(str(raw_data)[:100000])
                user_nlp = nlp(data["d"])
                sim = user_nlp.similarity(journal_nlp)
                return str(sim)
        else:
            return Response("Forbidden", status=403, mimetype="text/plain")
    except:
        return Response("Error", status=500, mimetype="text/plain")
