import spacy
import base64

nlp = spacy.load("en_core_web_md")


def doaj_trio(request):
    journal_data = request.values["e"]
    journal_decoded = base64.b64decode(journal_data)
    journal_nlp = spacy.tokens.Doc(nlp.vocab).from_bytes(journal_decoded)
    user_nlp = nlp(request.values["d"])
    sim = user_nlp.similarity(journal_nlp)
    return str(sim)
