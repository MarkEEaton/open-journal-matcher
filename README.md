# A journal recommender tool built on the Directory of Open Access Journals

This application suggests open access journals based on their similarity to a draft abstract submitted by the user. It is meant to be useful for authors who are trying to discovers suitable journals where they can submit their work. The results are supposed to be serendipitous; the goal is to uncover unexpected but highly relevant journals.

The application is built with Flask, combined with "serverless" infrastructure for data analysis. The Flask application calls a Google Cloud Function many times asynchronously. All of the computationally intensive work is done by the Cloud Function. Specificaly, the Cloud Function does the similarity calculations using spaCy and returns a similarity score for each potential target journal to the the Flask application.

Presented at the 18th Annual CUNY IT Conference. New York, NY. December 5, 2019.

This project is partly supported by a grant of Google Cloud Platform credits.
