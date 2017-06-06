from pygov_br.django_apps.camara_deputados import models as cd_models
from application import models
from textblob import TextBlob


def speech_to_sentences(text):
    blob = TextBlob(text)
    return list(lambda x: str(x).casefold(), blob.sentences)
