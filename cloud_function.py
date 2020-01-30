import spacy

nlp = spacy.load("en_core_web_md")

def doaj_trio(request):
    data = request.json
    journal_nlp = nlp(data["e"])
    user_nlp = nlp(data["d"])
    sim = user_nlp.similarity(journal_nlp)
    return str(sim)
