import json
import os

from click import secho
from django.conf import settings
from django.core.management.base import BaseCommand
from nlp import cache
from plagiarism import tokenize, bag_of_words
from plagiarism.input import yn_input
from pygov_br.django_apps.camara_deputados.models import Speech
from textblob.classifiers import NaiveBayesClassifier as Classifier
from unidecode import unidecode


def extractor(text):
    tokens = tokenize(unidecode(text.casefold()), 'stems',
                      language='portuguese')
    features = dict(bag_of_words(tokens, 'bool'))
    features['?'] = '?' in text
    features['!'] = '!' in text
    return features


class Command(BaseCommand):

    def handle(self, *args, **options):
        paragraphs = cache.load_from_cache('paragraphs', self._get_paragraphs,
                                           force_update=True)
        secho('%s paragraphs' % len(paragraphs), bold=True)
        self.text_examples = self._load_initial_texts()
        self.protocol_classifier = cache.load_from_cache(
            'protocol_classifier', self._protocol_classifier)

        secho('Building bests examples', bold=True)
        protocols_contents = self.build_best_examples(paragraphs)

        secho('%d protocols and %d contents initially classified' %
              (len(protocols_contents['protocol']),
               len(protocols_contents['content'])), bold=True)

        if not cache.load_from_cache('protocol_classifier_trained'):
            secho('Training the classifier', bold=True)
            self.protocol_classifier = self.train_classifier(
                self.protocol_classifier, protocols_contents, 100)
            cache.update_cache('protocol_classifier', self.protocol_classifier)
        else:
            secho('Classifier already trained', bold=True)

        secho("Initializing supervisioned training", bold=True)
        classified_paragraphs = self.supervisioned_train(
            paragraphs, self.protocol_classifier)


    def build_best_examples(self, paragraphs):
        protocols_contents = cache.load_from_cache('protocols_contents')

        if protocols_contents is None:
            protocols_contents = {'protocol': [], 'content': []}

        if protocols_contents['protocol'] == [] \
           or protocols_contents['content'] == []:

            for paragraph in paragraphs:
                prob_dist = self.protocol_classifier.prob_classify(paragraph)
                classification = prob_dist.max()
                probability = prob_dist.prob(classification)

                if probability > 0.8:
                    secho(classification.upper(), bold=True)
                    secho('%s\n\n' % paragraph)
                    protocols_contents[classification].append((probability,
                                                               paragraph))
                    protocols_contents[classification].sort(reverse=True)
            cache.update_cache('protocols_contents', protocols_contents)
        return protocols_contents

    def train_classifier(self, classifier, training_set, training_set_size):
        training_set = self._get_training_set(training_set, training_set_size)
        for idx in range(1, training_set_size + 1):
            secho("%s) Differences:" % idx)
            for label, data in training_set.items():
                try:
                    old_prob, paragraph = data.pop()
                    pdf = classifier.prob_classify(paragraph)
                    if pdf.prob(label) > 0.95:
                        fmt = (label, 1 - old_prob, 1 - pdf.prob(label))
                        secho("%s: from %.1e to %.1e" % fmt)
                        classifier.update([(paragraph, label)])
                        self._sort_training_set(training_set, classifier)
                except IndexError:
                    continue
        cache.update_cache('protocol_classifier_trained', True)
        return classifier

    def supervisioned_train(self, paragraphs, classifier):
        classified = {}
        for label in classifier.labels():
            classified[label] = []
        unclassified = paragraphs
        next_paragraph = True

        while unclassified and next_paragraph:
            for paragraph in unclassified:
                prob_dist = classifier.prob_classify(paragraph)
                label = prob_dist.max()
                value = prob_dist.prob(label)

                secho('\n%s:' % label.upper(), bold=True)
                secho('%s\n' % paragraph)

                if yn_input('Are you agree? [Y/n] '):
                    classifier.update([(paragraph, value)])
                    unclassified.remove(paragraph)
                    classified[label].append(paragraph)

                if not yn_input('Next paragraph? [Y/n]'):
                    next_paragraph = False

        return classified

    def _get_training_set(self, classes_dict, size):
        training_set = {}
        for key, value in classes_dict.items():
            training_set[key] = value[:size]
        return training_set

    def _sort_training_set(self, training_set, classifier):
        for key in training_set.keys():
            training_set[key].sort(key=lambda x: classifier.prob_classify(x[1])
                                   .prob(key))

    def _protocol_classifier(self):
        return Classifier([
            (self.text_examples['protocol_example'], 'protocol'),
            (self.text_examples['content_example'], 'content'),
        ], feature_extractor=extractor)

    def _load_initial_texts(self):
        examples_file = open(os.path.join(settings.BASE_DIR,
                                          'nlp/classify_text_examples.json'))
        return json.load(examples_file)

    def _get_paragraphs(self):
        data = Speech.objects.all().values_list('full_text', flat=True)
        paragraphs = []
        for speech in data:
            paragraphs.extend(speech.splitlines())
        return sorted(set(paragraphs))
