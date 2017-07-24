from django.core.management.base import BaseCommand
from django.db import transaction
from pygov_br.django_apps.camara_deputados import models as cd
from application import models
from click import progressbar
from unidecode import unidecode


normalize = lambda x: unidecode(x.lower().strip('.,:?!- '))


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        speeches = cd.Speech.objects.all()
        with progressbar(speeches, label='Processing speeches') as data:
            for speech in data:
                speech = models.Speech.objects.get_or_create(
                    id=speech.id,
                    data_id=speech.id,
                    author_id=speech.author_id
                )[0]
                self.get_speech_indexes(speech)

        deputies = cd.Deputy.objects.all()
        with progressbar(deputies, label='Processing deputies') as data:
            for deputy in data:
                models.Deputy.objects.get_or_create(
                    id=deputy.id,
                    data_id=deputy.id
                )

        proposals = cd.Proposal.objects.all()
        with progressbar(proposals, label='Processing proposals') as data:
            for proposal in data:
                if proposal.author:
                    proposal = models.Proposal.objects.get_or_create(
                        id=proposal.id,
                        data_id=proposal.id,
                        author_id=proposal.author_id
                    )[0]
                    self.get_proposal_indexes(proposal)

    @transaction.atomic
    def get_speech_indexes(self, speech):
        if speech.data.indexes:
            indexes = [
                normalize(word)
                for line in speech.data.indexes.splitlines()
                for word in line.split(',')
            ]

            for index in indexes:
                models.SpeechIndex.objects.get_or_create(
                    speech=speech,
                    text=index
                )

    @transaction.atomic
    def get_proposal_indexes(self, proposal):
        if proposal.data.indexes:
            indexes = [
                normalize(word)
                for line in proposal.data.indexes.splitlines()
                for word in line.split(',')
            ]

            for index in indexes:
                models.ProposalIndex.objects.get_or_create(
                    proposal=proposal,
                    text=index
                )
