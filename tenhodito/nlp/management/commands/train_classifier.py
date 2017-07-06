import os

from click import secho, progressbar
from django.conf import settings
from django.core.management.base import BaseCommand
from nlp import cache
from plagiarism import bag_of_words, stopwords, tokenizers
from plagiarism.input import yn_input
from application.models import SpeechIndex
from textblob.classifiers import NaiveBayesClassifier as Classifier
import numpy as np


STOPWORDS = stopwords.get_stop_words('portuguese')
STOPWORDS += ['tribuna', 'orador', 'sr', 'falar', 'pronunciamento', 'v.exa',
              'presidente', 'obrigado', 'é', 'deputado', 'srs', 'agradeço',
              'agradecimento', 'sras', 'revisão', 'boa', 'tarde', 'v', 'exa']


def get_corpus_tokens(corpus):
    corpus_tokens = []
    for text, label in corpus:
        corpus_tokens.append(tokenizers.stemmize(
            text,
            language='portuguese',
            stop_words=STOPWORDS,
        ))
    return corpus_tokens


def n_containing(token, corpus):
    return sum(1 for document in corpus if token in document)


def tfidf(bow, corpus):
    for token in bow:
        weight = np.log(len(corpus) / (n_containing(token, corpus) + 1))
        bow[token] = bow[token] * weight


def extractor(text, train_set):
    tokens = tokenizers.stemmize(
        text,
        language='portuguese',
        stop_words=STOPWORDS,
    )
    features = bag_of_words(tokens, 'boolean')
    # corpus = cache.load_from_cache('corpus', get_corpus_tokens,
    #                                corpus=train_set)
    # tfidf(features, corpus)
    return dict(features)


class Command(BaseCommand):

    def handle(self, *args, **options):
        paragraphs = cache.load_from_cache('paragraphs', self._get_paragraphs,
                                           force_update=True)
        secho('%s paragraphs' % len(paragraphs), bold=True)

        contents = paragraphs
        secho('%s paragraphs will be classified by themes' % len(contents),
              bold=True)
        if not yn_input('Continue? [Y/n] '):
            return
        theme_classifier = cache.load_from_cache('theme_classifier',
                                                 self._theme_classifier)

        self.accuracy(theme_classifier)

        # if yn_input('Start supervisioned training? [Y/n] '):
        #     secho("Initializing supervisioned training", bold=True)
        #     theme_classifier = self.supervisioned_train(
        #         paragraphs, theme_classifier, 'theme')
        #     cache.update('theme_classifier', theme_classifier)

        # themes = self.classify(paragraphs, theme_classifier)

    def supervisioned_train(self, paragraphs, classifier, train_name=''):
        unclassified = cache.load_from_cache('%s_unclassified' % train_name)
        if unclassified is None:
            unclassified = paragraphs

        next_paragraph = True

        while unclassified and next_paragraph:
            for paragraph in unclassified:
                prob_dist = classifier.prob_classify(paragraph)
                label = prob_dist.max()
                value = prob_dist.prob(label)
                if value > 0.5:
                    secho('\n%d%% %s:' % ((100 * value), label.upper()),
                          bold=True)
                    secho('%s\n' % paragraph)

                    if yn_input('Are you agree? [Y/n] '):
                        classifier.update([(paragraph, label)])
                        unclassified.remove(paragraph)
                    else:
                        labels = classifier.labels()
                        secho("Classifier's labels: %s" % str(labels))
                        correct_label = input("What's the correct label? ")
                        if correct_label in classifier.labels():
                            classifier.update([(paragraph, correct_label)])
                            unclassified.remove(paragraph)

                    cache.update('%s_unclassified' % train_name, unclassified)
                    cache.update('%s_classifier' % train_name, classifier)

                    if not yn_input('Next paragraph? [Y/n] '):
                        next_paragraph = False
                        break

        return classifier

    def initial_training(self, classifier):
        trainingset_dir = os.path.join(settings.BASE_DIR,
                                       'nlp/initial_training/')
        with open(os.path.join(trainingset_dir, 'sentences.txt')) as tfile:
            trainingset = list(
                map(lambda x: (x.split(';')[0].strip(),
                               x.split(';')[1].strip()),
                    tfile.readlines())
            )
            classifier.update(trainingset)

    def classify(self, paragraphs, classifier):
        classified = self._get_labels_dict(classifier)
        with progressbar(paragraphs, label='Classifying') as data:
            for paragraph in data:
                prob_dist = classifier.prob_classify(paragraph)
                label = prob_dist.max()
                classified[label].append(paragraph)
        return classified

    def _get_labels_dict(self, classifier):
        labels_dict = {}
        for label in classifier.labels():
            labels_dict[label] = []
        return labels_dict

    def _theme_classifier(self):
        classifier = Classifier(self.get_initial_training_set(),
                                feature_extractor=extractor)
        return classifier

    def accuracy(self, classifier):
        training_set_dir = os.path.join(settings.BASE_DIR,
                                        'nlp/initial_training/')
        trainingset = []
        with open(os.path.join(training_set_dir, 'sentences.txt')) as tfile:
            trainingset += list(
                map(lambda x: (x.split(';')[0].strip(),
                               x.split(';')[1].strip()),
                    tfile.readlines())
            )
        print(classifier.accuracy(trainingset))

    def get_initial_training_set(self):
        training_set_dir = os.path.join(settings.BASE_DIR,
                                        'nlp/initial_training/')
        trainingset = []
        themes = ["adm-publica", "agricultura", "arte-cultura-informacao",
                  "assistencia-social", "cidades", "ciencia-tecnologia",
                  "comercio-consumidor", "comunicacao-social",
                  "direitos-humanos-minorias",
                  "economia-financas-publicas", "educacao", "esporte-lazer",
                  "justica", "meio-ambiente", "politica",
                  "relacoes-exteriores", "saude", "seguranca",
                  "trabalho-emprego", "viacao-transporte"]

        for theme in themes:
            with open(os.path.join(training_set_dir, theme + '.txt')) as tfile:
                trainingset += list(
                    map(lambda x: (x.strip(), theme), tfile.readlines())
                )

        return trainingset

    def _get_paragraphs(self):
        return list(
            SpeechIndex.objects.all().values_list('text', flat=True)
        )
