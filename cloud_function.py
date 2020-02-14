import spacy
import asyncio
from aiohttp import ClientSession as Session
from gcloud.aio.storage import Storage

nlp = spacy.load("en_core_web_md")

async def doaj_trio(request):
    data = request.json
    async with Session() as session:
        storage = Storage(session=session)
        bucket = storage.get_bucket("bucket_name")
        blob = data["f"]
        blob_object = await bucket.get_blob(blob)
        raw_data = await blob_object.download()

        journal_nlp = nlp(str(raw_data)[:100000])
        user_nlp = nlp(data["d"])
        sim = user_nlp.similarity(journal_nlp)
        return str(sim)
