import json
import os
import textblob

from click import secho, progressbar
from django.conf import settings
from django.core.management.base import BaseCommand
from nlp import cache
from plagiarism import tokenize, bag_of_words, stopwords, tokenizers
from plagiarism.input import yn_input
from pygov_br.django_apps.camara_deputados.models import Speech
from application.models import SpeechSentence
from textblob.classifiers import NaiveBayesClassifier as Classifier
from unidecode import unidecode

STOPWORDS = stopwords.get_stop_words('portuguese')
STOPWORDS += ['tribuna', 'orador', 'sr', 'falar', 'pronunciamento', 'v.exa',
              'presidente', 'obrigado', 'é', 'deputado', 'srs', 'agradeço',
              'agradecimento', 'sras', 'revisão', 'boa', 'tarde', 'v', 'exa']


def extractor(text, train_set):
    tokens = tokenizers.stemmize(
        text,
        language='portuguese',
        stop_words=STOPWORDS,
    )
    features = dict(bag_of_words(tokens, 'boolean'))
    features['?'] = '?' in text
    features['!'] = '!' in text
    return features


class Command(BaseCommand):

    def handle(self, *args, **options):
        paragraphs = cache.load_from_cache('paragraphs', self._get_paragraphs,
                                           force_update=True)
        secho('%s paragraphs' % len(paragraphs), bold=True)
        # self.text_examples = self._load_initial_texts()
        # protocol_classifier = cache.load_from_cache(
        #     'protocol_classifier', self._protocol_classifier)

        # secho('Building bests examples', bold=True)
        # protocol_best_examples = self.build_best_examples(
        #     paragraphs, protocol_classifier, 0.8, train_name='protocol')

        # secho('%d protocols and %d contents initially classified' %
        #       (len(protocol_best_examples['protocol']),
        #        len(protocol_best_examples['content'])), bold=True)

        # if not cache.load_from_cache('protocol_classifier_trained'):
        #     secho('Training the classifier', bold=True)
        #     protocol_classifier = self.train_classifier(
        #         protocol_classifier, protocol_best_examples, 100, 'protocol')
        #     cache.update('protocol_classifier', protocol_classifier)

        # if yn_input('Start supervisioned training? [Y/n] '):
        #     secho("Initializing supervisioned training", bold=True)
        #     protocol_classifier = self.supervisioned_train(
        #         paragraphs, protocol_classifier, 'protocol')
        #     cache.update('protocol_classifier', protocol_classifier)

        # protocols_contents = self.classify(paragraphs, protocol_classifier)

        contents = paragraphs
        secho('%s paragraphs will be classified by themes' % len(contents),
              bold=True)
        if not yn_input('Continue? [Y/n] '):
            return
        theme_classifier = cache.load_from_cache('theme_classifier',
                                                 self._theme_classifier)

        themes_best_examples = self.build_best_examples(
            contents, theme_classifier, 0.8, train_name='theme')
        for key, value in themes_best_examples.items():
            secho('%d %s paragraphs' % (len(value), key), bold=True)

        if not cache.load_from_cache('theme_classifier_trained'):
            secho('Training the classifier', bold=True)
            theme_classifier = self.train_classifier(
                theme_classifier, themes_best_examples, 10, 'theme')
            cache.update('theme_classifier', theme_classifier)

        if yn_input('Start supervisioned training? [Y/n] '):
            secho("Initializing supervisioned training", bold=True)
            theme_classifier = self.supervisioned_train(
                paragraphs, theme_classifier, 'theme')
            cache.update('theme_classifier', theme_classifier)

        themes = self.classify(paragraphs, theme_classifier)
        import ipdb; ipdb.set_trace()

    def build_best_examples(self, paragraphs, classifier, min_prob,
                            train_name=''):
        best_examples = cache.load_from_cache('best_%s' % train_name)

        if best_examples is not None:
            return best_examples

        best_examples = self._get_labels_dict(classifier)

        for paragraph in paragraphs:
            prob_dist = classifier.prob_classify(paragraph)
            classification = prob_dist.max()
            probability = prob_dist.prob(classification)

            if probability > min_prob:
                secho(classification.upper(), bold=True)
                secho('%s\n\n' % paragraph)
                best_examples[classification].append((probability, paragraph))
                best_examples[classification].sort(reverse=True)
        cache.update('best_%s' % train_name, best_examples)
        return best_examples

    def train_classifier(self, classifier, training_set, training_set_size,
                         train_name=''):
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
                        classifier.update([(self._tokenize_text(paragraph),
                                            label)])
                        self._sort_training_set(training_set, classifier)
                except IndexError:
                    continue
        cache.update('%s_classifier_trained' % train_name, True)
        return classifier

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

                secho('\n%d%% %s:' % ((100 * value), label.upper()), bold=True)
                secho('%s\n' % paragraph)

                if yn_input('Are you agree? [Y/n] '):
                    classifier.update([(self._tokenize_text(paragraph),
                                        label)])
                    unclassified.remove(paragraph)
                else:
                    secho("Classifier's labels: %s" % str(classifier.labels()))
                    correct_label = input("What's the correct label? ")
                    if correct_label in classifier.labels():
                        classifier.update([(self._tokenize_text(paragraph),
                                            correct_label)])
                        unclassified.remove(paragraph)

                cache.update('%s_unclassified' % train_name, unclassified)
                cache.update('%s_classifier' % train_name, classifier)

                if not yn_input('Next paragraph? [Y/n] '):
                    next_paragraph = False
                    break

            if yn_input('Continue as unsupervisioned train? [Y/n] '):
                return self.unsupervisioned_train(unclassified, classifier,
                                                  train_name)
        return classifier

    def unsupervisioned_train(self, paragraphs, classifier, train_name=''):
        with progressbar(paragraphs, label='Unsupervisioned training') as data:
            for paragraph in data:
                prob_dist = classifier.prob_classify(paragraph)
                label = prob_dist.max()
                classifier.update([(paragraph, label)])
                paragraphs.remove(paragraph)
                cache.update('%s_unclassified' % train_name, paragraphs)
                cache.update('%s_classifier' % train_name, classifier)
        return classifier

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

    def _tokenize_text(self, text):
        tokens = tokenizers.stemmize(text, language='portuguese',
                                     stop_words=STOPWORDS)
        return ' '.join(tokens)

    def _theme_classifier(self):
        classifier = Classifier([], feature_extractor=extractor)
        themes = ["adm-publica", "agricultura", "arte-cultura-informacao",
                  "assistencia-social", "cidades", "ciencia-tecnologia",
                  "comercio-consumidor", "comunicacao-social",
                  "desenvolvimento-regional", "direitos-humanos-minorias",
                  "economia-financas-publicas", "educação", "esporte-lazer",
                  "gestao", "justica", "meio-ambiente", "politica",
                  "relacoes-exteriores", "saude", "seguranca",
                  "trabalho-emprego", "viacao-transporte"]
        themes_dir = os.path.join(settings.BASE_DIR,
                                  'nlp/initial_training/')
        for theme in themes:
            with open(os.path.join(themes_dir, theme + '.txt')) as tfile:
                for line in tfile:
                    print('[{}] {}'.format(theme, line))
                    classifier.update([(line, theme)])
        return classifier

    def _load_initial_texts(self):
        examples_file = open(os.path.join(settings.BASE_DIR,
                                          'nlp/classify_text_examples.json'))
        return json.load(examples_file)

    def _get_paragraphs(self):
        return list(SpeechSentence.objects.all().values_list('text', flat=True))
        data = Speech.objects.all().values_list('full_text', flat=True)
        paragraphs = []
        for speech in data:
            if speech:
                paragraphs.extend(speech)

        blob = textblob.TextBlob(' '.join(data))
        sentences = list(
            map(lambda x: str(x).casefold().strip('.- '), blob.sentences)
        )
        return sentences
        return sorted(set(paragraphs))
        sentences_tokens = []
        for sentence in sentences:
            token = tokenizers.stemmize(
                sentence,
                language='portuguese',
                stop_words=STOPWORDS,
            )

            if len(token):
                sentences_tokens.append(' '.join(token))
        return sentences_tokens
