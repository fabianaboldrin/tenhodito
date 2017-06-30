from textblob import TextBlob


def speech_to_sentences(text):
    blob = TextBlob(text)
    return list(map(lambda x: str(x).casefold(), blob.sentences))
