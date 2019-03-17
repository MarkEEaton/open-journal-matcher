import nltk
from collections import Counter


def get_nouns(text):
    print("collecting nouns...")

    nouns = []
    stop = nltk.corpus.stopwords.words("english")
    for item in text:
        if (
            item[1] == "NN"
            and item[0].lower() not in stop
            and item[0].lower().isalpha()
        ):
            nouns.append(item[0])
    counter = Counter(nouns).most_common(100)
    return [(k, v / counter[0][1]) for k, v in counter]


def get_verbs(text):
    print("collecting verbs...")

    verbs = []
    stop = nltk.corpus.stopwords.words("english")
    for item in text:
        if (
            item[1][0] == "V"
            and item[0].lower() not in stop
            and item[0].lower().isalpha()
        ):
            verbs.append(item[0])
    counter = Counter(verbs).most_common(100)
    return [(k, v / counter[0][1]) for k, v in counter]


def get_proper_names(text):
    print("collecting proper names...")

    sentt = nltk.ne_chunk(text, binary=False)
    person_list = []
    person = []
    name = ""
    print("checking names against a dictionary...")
    for subtree in sentt.subtrees(filter=lambda t: t.label() == "PERSON"):
        for leaf in subtree.leaves():
            if not nltk.corpus.wordnet.synsets(leaf[0]):
                person.append(leaf[0])
        if len(person) > 1:
            for part in person:
                name += part + " "
            if name[:-1]:
                person_list.append(name[:-1])
            name = ""
        person = []

    counter = Counter(person_list).most_common(100)
    return [(k, v / counter[0][1]) for k, v in counter]
