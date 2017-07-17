from django.core.management.base import BaseCommand
from application import models
from django.db import transaction
from collections import Counter
from click import progressbar
from nlp import cache


class Command(BaseCommand):

    themes = models.Theme.objects.all()
    indexes_themes = []
    speech_themes = []
    deputy_themes = []

    @transaction.atomic
    def handle(self, *args, **options):
        classifier = cache.load_from_cache('theme_classifier')
        speeches = models.Speech.objects.all()[:10]
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
        models.IndexTheme.objects.bulk_create(self.indexes_themes)
        models.SpeechTheme.objects.bulk_create(self.speech_themes)
        # for deputy in models.Deputy.objects.exclude(speeches=None):
        #     for speech in deputy.speeches.all():
        #         themes = Counter()
        #         for theme in speech.themes.all():
        #             themes.update([theme.slug])
        #         print(themes)


    def update_index_theme(self, index, theme):
        theme_obj = self.themes.get(slug=theme)
        self.indexes_themes.append(models.IndexTheme(
            amount=1,
            theme=theme_obj,
            index=index,
            is_main=True,
        ))

    @transaction.atomic
    def update_speech_themes(self, speech, themes):
        total = sum(themes.values())
        for i, theme in enumerate(themes.most_common()):
            theme_obj = self.themes.get(slug=theme[0])
            speech_theme = models.SpeechTheme(
                theme=theme_obj,
                speech=speech,
                amount=themes[theme[0]]/total
            )
            if i == 0:
                speech_theme.is_main = True
            self.speech_themes.append(speech_theme)

    def get_percentages(self, counter):
        percentages = Counter()
        total = sum(counter.values())
        for key in counter.keys():
            percentages[key] = round(counter[key] / total * 100, 2)
        return percentages
