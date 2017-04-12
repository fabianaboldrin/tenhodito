from django.core.management.base import BaseCommand
from nlp.bow import Corpus
from nlp.clustering import kmeans
from pygov_br.django_apps.camara_deputados.models import Speech


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = Speech.objects.all()[:10].values_list('full_text', flat=True)
        corpus = Corpus(data)
        centroids, labels = kmeans(corpus, 5)

        centroids_dict = {}
        for centroid_idx, centroid in enumerate(centroids):
            centroids_dict[centroid_idx] = []
            for label_idx, value in enumerate(labels):
                text = corpus[label_idx]
                if value == centroid_idx:
                    centroids_dict[centroid_idx] += [text]

        centroids_corpus = []
        for key, value in centroids_dict.items():
            centroids_corpus.append(Corpus(value))

        print(labels)
        for key, value in centroids_dict.items():
            print('=' * 80)
            print('Centroid %r: %d texts.' % (key, len(centroids_corpus[key])))
            print(centroids_corpus[key].common_words(3))
            print('\n')

        print('\nCommon words:')
        print(corpus.common_words(40))

        print('\n')
        print(corpus.similarity_matrix())
