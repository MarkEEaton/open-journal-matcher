import spacy

nlp = spacy.load("en_core_web_md")

def doaj_trio(request):
    data = request.get_json(force=True)
    journal_data = data["e"]
    journal_nlp = spacy.tokens.Doc(nlp.vocab).from_bytes(bytes(journal_data, 'latin-1'))
    user_nlp = nlp(data["d"])
    sim = user_nlp.similarity(journal_nlp)
    return str(sim)
