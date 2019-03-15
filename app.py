import requests
from pprint import pprint

BASEURL = "https://doaj.org/api/v1/search/articles/issn%3A"
ISSN = "1715-720X"
PAGESIZE = "?pageSize=100"

data = requests.get(BASEURL + ISSN + PAGESIZE)
articles = data.json().get('results')

next = data.json()['next']

while next:
    data = requests.get(next)
    new_articles = data.json().get('results')
    articles = articles + new_articles
    next = data.json().get('next')

print(len(articles))

