from django.core.management.base import BaseCommand
from django.db import transaction
from pygov_br.django_apps.camara_deputados.models import Speech
from nlp import pre_processing
from application import models


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        speeches = Speech.objects.all()
        for speech in speeches:
            # if speech.indexes:
            #     indexes = []
            #     for line in speech.indexes.splitlines():
            #         indexes += line.split(',')
            #     for index in indexes:
            #         models.SpeechIndex.objects.get_or_create(
            #             speech=speech,
            #             text=index
            #         )
            if speech.summary:
                sentences = pre_processing.speech_to_sentences(speech.summary)
                for sentence in sentences:
                    # Split no ;
                    models.SpeechSentence.objects.get_or_create(
                        speech=speech,
                        text=sentence
                    )
