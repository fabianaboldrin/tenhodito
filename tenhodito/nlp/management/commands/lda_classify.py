from django.core.management.base import BaseCommand
from pygov_br.django_apps.camara_deputados.models import Speech
from plagiarism import stopwords, tokenizers
from gensim import corpora, models, similarities
from gensim.models.ldamodel import LdaModel
import textblob


STOPWORDS = stopwords.get_stop_words('portuguese')
STOPWORDS += ['tribuna', 'orador', 'sr', 'falar', 'pronunciamento', 'v.exa',
              'presidente', 'obrigado', 'é', 'deputado', 'srs', 'agradeço',
              'agradecimento', 'sras', 'revisão', 'boa', 'tarde']


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        sentences = self.read_sentences()
        print('sentences')
        dictionary = corpora.Dictionary(sentences)
        dictionary.save('cache.dic')
        print('dict')
        corpus = [dictionary.doc2bow(text) for text in sentences]
        corpora.MmCorpus.serialize('cache.mm', corpus)
        print('corpus')
        lda = LdaModel(corpus, num_topics=15)
        lda.save('lda')
        import ipdb; ipdb.set_trace()
        print('lda')


    def read_sentences(self):
        speeches = Speech.objects.all().values_list(
            'full_text',
            flat=True
        )

        blob = textblob.TextBlob(' '.join(speeches))
        sentences = list(
            map(lambda x: str(x).casefold().strip('.- '), blob.sentences)
        )

        sentences_tokens = []
        for sentence in sentences:
            token = tokenizers.stemmize(
                sentence,
                language='portuguese',
                stop_words=STOPWORDS,
            )

            if len(token):
                sentences_tokens.append(token)
        return sentences_tokens
