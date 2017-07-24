from textblob import TextBlob
from plagiarism import bag_of_words, stopwords, tokenizers
from unidecode import unidecode


STOPWORDS = stopwords.get_stop_words('portuguese')
STOPWORDS += ['tribuna', 'orador', 'sr', 'falar', 'pronunciamento', 'v.exa',
              'presidente', 'obrigado', 'é', 'deputado', 'srs', 'agradeço',
              'agradecimento', 'sras', 'revisão', 'boa', 'tarde', 'v', 'exa']


def speech_to_sentences(text):
    blob = TextBlob(text)
    return list(map(lambda x: str(x).casefold(), blob.sentences))


def normalize(text):
    return unidecode(text.lower().strip('.,:?!- '))


def extract(text):
    tokens = tokenizers.stemmize(
        text,
        language='portuguese',
        stop_words=STOPWORDS,
    )
    features = bag_of_words(tokens, 'boolean')
    if len(tokens) > 1:
        features[' '.join(tokens)] = 1
    return dict(features)
