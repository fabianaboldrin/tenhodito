from django.core.management.base import BaseCommand
from application import models
from django.db import transaction
from collections import Counter
from click import progressbar
from nlp import cache


class Command(BaseCommand):

    themes = models.Theme.objects.all()

    @transaction.atomic
    def handle(self, *args, **options):
        classifier = cache.load_from_cache('theme_classifier')
        speeches = models.Speech.objects.all()
        with progressbar(speeches, label='Classifying speeches') as data:
            for speech in data:
                indexes = speech.indexes.all()
                themes = Counter()
                for index in indexes:
                    prob_dist = classifier.prob_classify(index.text)
                    label = prob_dist.max()
                    if prob_dist.prob(label) > 0.5:
                        themes.update([label])
                        self.update_index_theme(index, label)
                self.update_speech_themes(speech, themes)
        for deputy in models.Deputy.objects.exclude(speeches=None):
            for speech in deputy.speeches.all():
                themes = Counter()
                for theme in speech.themes.all():
                    themes.update([theme.slug])
                print(themes)

    @transaction.atomic
    def update_index_theme(self, index, theme):
        theme_obj = self.themes.get(slug=theme)
        index.theme = theme_obj
        index.save()

    @transaction.atomic
    def update_speech_themes(self, speech, themes):
        for theme in themes.keys():
            speech.themes.add(self.themes.get(slug=theme))

    def get_percentages(self, counter):
        percentages = Counter()
        total = sum(counter.values())
        for key in counter.keys():
            percentages[key] = round(counter[key] / total * 100, 2)
        return percentages
