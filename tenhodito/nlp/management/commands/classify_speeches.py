from django.core.management.base import BaseCommand
from application import models
from django.db import transaction
from collections import Counter
from click import progressbar
from nlp import cache


class Command(BaseCommand):

    themes = models.Theme.objects.all()
    speech_indexes_themes = []
    speech_themes = []
    proposal_themes = []
    proposal_indexes_themes = []
    deputy_themes = []
    state_themes = []
    analysis = models.Analysis()

    @transaction.atomic
    def handle(self, *args, **options):
        self.analysis.save()
        classifier = cache.load_from_cache('theme_classifier')
        speeches = models.Speech.objects.filter(data__session_phase__code='PE')
        with progressbar(speeches, label='Classifying speeches') as data:
            for speech in data:
                indexes = speech.indexes.all()
                themes = Counter()
                for index in indexes:
                    prob_dist = classifier.prob_classify(index.text)
                    label = prob_dist.max()
                    if prob_dist.prob(label) > 0.5:
                        themes.update([label])
                        self.update_index_theme(
                            index,
                            label,
                            models.SpeechIndexTheme,
                            self.speech_indexes_themes
                        )
                self.update_speech_themes(speech, themes)
        models.SpeechIndexTheme.objects.bulk_create(self.speech_indexes_themes)
        models.SpeechTheme.objects.bulk_create(self.speech_themes)

        proposals = models.Proposal.objects.all()
        with progressbar(proposals, label='Classifying proposals') as data:
            for proposal in data:
                indexes = proposal.indexes.all()
                themes = Counter()
                for index in indexes:
                    prob_dist = classifier.prob_classify(index.text)
                    label = prob_dist.max()
                    if prob_dist.prob(label) > 0.5:
                        themes.update([label])
                        self.update_index_theme(
                            index,
                            label,
                            models.ProposalIndexTheme,
                            self.proposal_indexes_themes
                        )
                self.update_proposal_themes(proposal, themes)
        models.ProposalIndexTheme.objects.bulk_create(
            self.proposal_indexes_themes
        )
        models.ProposalTheme.objects.bulk_create(self.proposal_themes)

        for deputy in models.Deputy.objects.exclude(speeches=None):
            themes = Counter()
            speeches_count = 0
            proposals_count = 0
            for speech in deputy.speeches.all():
                speech_themes = speech.themes.filter(
                    analysis=self.analysis
                )
                if speech_themes:
                    speeches_count += 1
                    for t in speech_themes:
                        theme_amount = themes.get(t.theme.slug, 0) + t.amount
                        themes[t.theme.slug] = theme_amount

            for proposal in deputy.proposals.all():
                proposal_themes = proposal.themes.filter(
                    analysis=self.analysis
                )
                if proposal_themes:
                    proposals_count += 1
                    for t in proposal_themes:
                        theme_amount = themes.get(t.theme.slug, 0) + t.amount
                        themes[t.theme.slug] = theme_amount

            for i, theme in enumerate(themes.most_common()):
                theme_obj = self.themes.get(slug=theme[0])
                deputy_theme = models.DeputyTheme(
                    theme=theme_obj,
                    deputy=deputy,
                    amount=theme[1] / (speeches_count + proposals_count),
                    analysis=self.analysis
                )
                if i == 0:
                    deputy_theme.is_main = True
                self.deputy_themes.append(deputy_theme)
            self.analysis.speeches_count += speeches_count
            self.analysis.proposals_count += proposals_count
        models.DeputyTheme.objects.bulk_create(self.deputy_themes)

        for state in models.State.objects.all():
            themes = Counter()
            deputy_count = 0
            initials = state.initials
            for deputy in models.Deputy.objects.filter(data__region=initials):
                deputy_themes = deputy.themes.all()
                if deputy_themes:
                    deputy_count += 1
                    for t in deputy_themes:
                        theme_amount = themes.get(t.theme.slug, 0) + t.amount
                        themes[t.theme.slug] = theme_amount

            for i, theme in enumerate(themes.most_common()):
                theme_obj = self.themes.get(slug=theme[0])
                state_theme = models.StateTheme(
                    theme=theme_obj,
                    state=state,
                    amount=theme[1] / deputy_count,
                    analysis=self.analysis
                )
                if i == 0:
                    state_theme.is_main = True
                self.state_themes.append(state_theme)
        models.StateTheme.objects.bulk_create(self.state_themes)

        self.analysis.deputy_count = deputy_count
        self.analysis.save()

    def update_index_theme(self, index, theme, index_theme_class, index_list):
        theme_obj = self.themes.get(slug=theme)
        index_list.append(index_theme_class(
            amount=1,
            theme=theme_obj,
            index=index,
            is_main=True,
            analysis=self.analysis
        ))

    @transaction.atomic
    def update_speech_themes(self, speech, themes):
        total = sum(themes.values())
        for i, theme in enumerate(themes.most_common()):
            theme_obj = self.themes.get(slug=theme[0])
            speech_theme = models.SpeechTheme(
                theme=theme_obj,
                speech=speech,
                amount=themes[theme[0]] / total,
                analysis=self.analysis
            )
            if i == 0:
                speech_theme.is_main = True
            self.speech_themes.append(speech_theme)

    @transaction.atomic
    def update_proposal_themes(self, proposal, themes):
        total = sum(themes.values())
        for i, theme in enumerate(themes.most_common()):
            theme_obj = self.themes.get(slug=theme[0])
            proposal_theme = models.ProposalTheme(
                theme=theme_obj,
                proposal=proposal,
                amount=themes[theme[0]] / total,
                analysis=self.analysis
            )
            if i == 0:
                proposal_theme.is_main = True
            self.proposal_themes.append(proposal_theme)

    def get_percentages(self, counter):
        percentages = Counter()
        total = sum(counter.values())
        for key in counter.keys():
            percentages[key] = round(counter[key] / total * 100, 2)
        return percentages
