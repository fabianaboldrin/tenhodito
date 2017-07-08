from django.core.management.base import BaseCommand
from django.db import transaction
from pygov_br.django_apps.camara_deputados.models import Speech, Deputy
from nlp import pre_processing
from application import models
from click import progressbar


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        speeches = Speech.objects.all()
        with progressbar(speeches, label='Processing speeches') as data:
            for speech in data:
                speech = models.Speech.objects.get_or_create(
                    id=speech.id,
                    data_id=speech.id,
                    author_id=speech.author_id
                )[0]
                self.get_indexes(speech)

        deputies = Deputy.objects.all()
        with progressbar(deputies, label='Processing deputies') as data:
            for deputy in data:
                models.Deputy.objects.get_or_create(
                    id=deputy.id,
                    data_id=deputy.id
                )

    @transaction.atomic
    def get_indexes(self, speech):
        if speech.data.indexes:
            indexes = []
            for line in speech.data.indexes.splitlines():
                indexes += line.split(',')

            for index in indexes:
                models.SpeechIndex.objects.get_or_create(
                    speech=speech,
                    text=index
                )

    @transaction.atomic
    def get_sentences(self, speech):
        if speech.summary:
            sentences = pre_processing.speech_to_sentences(speech.summary)
            for sentence in sentences:
                # Split no ;
                models.SpeechSentence.objects.get_or_create(
                    speech=speech,
                    text=sentence
                )
