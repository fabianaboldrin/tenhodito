from collections import Counter
from textblob.classifiers import NaiveBayesClassifier as Classifier
from application import models
from nlp.cache import load_from_cache
from nlp.pre_processing import normalize, extract
from django.conf import settings
import json
import os


class ThemeNaiveBayesClassifier(object):

    def __init__(self):
        self.used_words = load_from_cache('used_words', self._get_used_words)
        self.initial_trainset = load_from_cache('initial_trainset',
                                                self._get_initial_trainset)
        self.analysis = models.Analysis.objects.create()
        self.themes = models.Theme.objects.all()
        self.create_lists = {
            models.SpeechIndexTheme: [],
            models.ProposalIndexTheme: [],
            models.SpeechTheme: [],
            models.ProposalTheme: [],
        }

    @property
    def classifier(self):
        return load_from_cache('theme_classifier', self._get_classifier)

    def save_objects(self):
        for _class, object_list in self.create_lists.items():
            _class.objects.bulk_create(object_list)

    def classify_indexed(self, indexed, rel_field,
                         indexed_theme_class, index_theme_class):
        themes = self._classify_indexes(indexed.indexes.all(),
                                        index_theme_class)
        for i, theme in enumerate(themes.most_common()):
            indexed_theme = indexed_theme_class(
                theme=self.themes.get(slug=theme[0]),
                amount=theme[1],
                analysis=self.analysis
            )
            setattr(indexed_theme, rel_field, indexed)

            if i == 0:
                indexed_theme.is_main = True
            self.create_lists[indexed_theme_class].append(indexed_theme)

    def _classify_indexes(self, indexes, index_theme_class):
        themes = Counter()
        for index in indexes:
            index_theme = self._classify_index(index, index_theme_class)
            if index_theme:
                themes.update([index_theme.theme.slug])

        return Counter({
            k: v / total
            for total in (sum(themes.values()), )
            for k, v in themes.items()
        })

    def _classify_index(self, index, index_theme_class):
        prob_dist = self.classifier.prob_classify(index.text)
        label = prob_dist.max()
        if prob_dist.prob(label) > 0.5:
            index_theme = index_theme_class(
                amount=1,
                theme=self.themes.get(slug=label),
                index=index,
                is_main=True,
                analysis=self.analysis
            )
            self.create_lists[index_theme_class].append(index_theme)
            return index_theme

    def _get_classifier(self):
        return Classifier(self.initial_trainset, feature_extractor=extract)

    def _get_initial_trainset(self):
        trainset_dir = os.path.join(settings.BASE_DIR, 'nlp/')
        with open(os.path.join(trainset_dir, 'thesaurus.json')) as thes:
            thesaurus = json.load(thes)
            del thesaurus['politica']
            del thesaurus['gestao']
            del thesaurus['desenvolvimento-regional']
            del thesaurus['comunicacao-social']
            del thesaurus['adm-publica']
            trainset = [
                (normalize(token), theme)
                for theme, tokens in thesaurus.items()
                for token in tokens
                if normalize(token) in self.used_words
            ]
        return trainset

    def _get_used_words(self):
        speech_indexes = list(
            models.SpeechIndex.objects.all().values_list('text', flat=True)
        )
        proposal_indexes = list(
            models.ProposalIndex.objects.all().values_list('text', flat=True)
        )
        return speech_indexes + proposal_indexes
