from django.db import models
from django.utils.text import slugify
from pygov_br.django_apps.camara_deputados import models as cd_models
from itertools import chain


class Theme(models.Model):
    description = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.description)
        return super(Theme, self).save(*args, **kwargs)


class Analysis(models.Model):
    datetime = models.DateTimeField(auto_now=True)
    speeches_count = models.IntegerField(default=0)
    deputies_count = models.IntegerField(default=0)
    proposals_count = models.IntegerField(default=0)

    class Meta:
        get_latest_by = 'datetime'

    def __str__(self):
        return str(self.datetime)


class State(models.Model):
    name = models.CharField(max_length=50)
    initials = models.CharField(max_length=2)

    def get_main_theme(self):
        analysis = Analysis.objects.latest()
        return analysis.statetheme_related.get(
            state=self, is_main=True
        )

    def get_all_themes(self):
        analysis = Analysis.objects.latest()
        return analysis.statetheme_related.get(
            state=self
        ).order_by('-amount')

    def __str__(self):
        return self.initials


class Speech(models.Model):
    data = models.OneToOneField(cd_models.Speech)
    author = models.ForeignKey('Deputy', related_name='speeches')

    def __str__(self):
        return self.data.author.parliamentary_name

    def get_main_theme(self):
        analysis = Analysis.objects.latest()
        return analysis.speechtheme_related.get(
            speech=self, is_main=True
        )

    def get_all_themes(self):
        analysis = Analysis.objects.latest()
        return analysis.speechtheme_related.get(
            speech=self
        ).order_by('-amount')


class SpeechIndex(models.Model):
    speech = models.ForeignKey(Speech, related_name='indexes')
    text = models.TextField()

    @property
    def author(self):
        return self.speech.author

    def __str__(self):
        return self.text


class Proposal(models.Model):
    data = models.OneToOneField(cd_models.Proposal)
    author = models.ForeignKey('Deputy', related_name='proposals')

    def __str__(self):
        return self.data.name


class ProposalIndex(models.Model):
    proposal = models.ForeignKey(Proposal, related_name='indexes')
    text = models.TextField()

    @property
    def author(self):
        return self.proposal.author

    def __str__(self):
        return self.text


class Deputy(models.Model):
    data = models.OneToOneField(cd_models.Deputy)

    class Meta:
        ordering = ['data__parliamentary_name', 'data__region']

    def __str__(self):
        return self.data.parliamentary_name

    @property
    def speeches_count(self):
        analysis = Analysis.objects.latest()
        return analysis.speechtheme_related.filter(
            speech__author=self, is_main=True
        ).count()

    @property
    def total_speeches(self):
        return self.speeches.filter(data__session_phase__code='PE').count()

    @property
    def proposals_count(self):
        analysis = Analysis.objects.latest()
        return analysis.proposaltheme_related.filter(
            proposal__author=self, is_main=True
        ).count()

    @property
    def ordered_proposals(self):
        unclassified = self.proposals.filter(themes=None)
        classified = self.proposals.exclude(themes=None)
        return list(chain(classified, unclassified))

    @property
    def ordered_speeches(self):
        all_speeches = self.speeches.filter(data__session_phase__code='PE')
        unclassified = all_speeches.filter(themes=None)
        classified = all_speeches.exclude(themes=None)
        return list(chain(classified, unclassified))

    def get_main_theme(self):
        analysis = Analysis.objects.latest()
        return analysis.deputytheme_related.get(
            deputy=self, is_main=True
        )

    def get_all_themes(self):
        analysis = Analysis.objects.latest()
        return analysis.deputytheme_related.filter(
            deputy=self
        ).order_by('-amount')

    def get_speeches_themes(self):
        analysis = Analysis.objects.latest()
        return analysis.speechtheme_related.filter(
            speech__author=self
        ).order_by('-amount')


class ThemeRelation(models.Model):
    amount = models.FloatField()
    is_main = models.BooleanField(default=False)
    analysis = models.ForeignKey(Analysis, related_name='%(class)s_related')

    class Meta:
        abstract = True


class SpeechIndexTheme(ThemeRelation):
    theme = models.ForeignKey(Theme, related_name='speech_indexes')
    index = models.ForeignKey(SpeechIndex, related_name='themes')


class SpeechTheme(ThemeRelation):
    theme = models.ForeignKey(Theme, related_name='speeches')
    speech = models.ForeignKey(Speech, related_name='themes')


class DeputyTheme(ThemeRelation):
    theme = models.ForeignKey(Theme, related_name='deputies')
    deputy = models.ForeignKey(Deputy, related_name='themes')


class StateTheme(ThemeRelation):
    theme = models.ForeignKey(Theme, related_name='states')
    state = models.ForeignKey(State, related_name='themes')


class ProposalTheme(ThemeRelation):
    theme = models.ForeignKey(Theme, related_name='proposals')
    proposal = models.ForeignKey(Proposal, related_name='themes')


class ProposalIndexTheme(ThemeRelation):
    theme = models.ForeignKey(Theme, related_name='proposal_indexes')
    index = models.ForeignKey(ProposalIndex, related_name='themes')
