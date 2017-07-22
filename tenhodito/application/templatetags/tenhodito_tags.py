from application import models
from django import template


register = template.Library()


@register.filter(name='percentage')
def get_percentage(value):
    return value * 100


@register.simple_tag(name='deputy_proposal_theme_bar')
def proposal_theme_percentage(deputy, theme):
    if deputy.proposals_count:
        analysis = models.Analysis.objects.latest()
        proposals = analysis.proposaltheme_related.filter(
            proposal__author=deputy, theme__slug=theme
        ).count()
        return (proposals / deputy.proposals_count) * 100
    else:
        return 0


@register.simple_tag(name='deputy_speech_theme_bar')
def speech_theme_percentage(deputy, theme):
    if deputy.speeches_count > 0:
        analysis = models.Analysis.objects.latest()
        proposals = analysis.speechtheme_related.filter(
            speech__author=deputy, theme__slug=theme
        ).count()
        return (proposals / deputy.speeches_count) * 100
    else:
        return 0
