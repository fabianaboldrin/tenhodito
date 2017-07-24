from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse
from application import models


def home_json(request):
    themes = {}
    analysis = models.Analysis.objects.latest()
    for state in models.State.objects.all():
        state_theme = analysis.statetheme_related.get(
            state__initials=state.initials,
            is_main=True
        )
        themes[state.initials] = {
            'slug': state_theme.theme.slug,
            'theme': state_theme.theme.description
        }
    return JsonResponse(themes)


def state_json(request, state):
    themes = []
    state = models.State.objects.get(initials=state)
    analysis = models.Analysis.objects.latest()
    state_themes = analysis.statetheme_related.filter(
        state__initials=state.initials
    )
    for state_theme in state_themes:
        themes.append({
            'value': state_theme.amount * 100,
            'name': state_theme.theme.description,
            'slug': state_theme.theme.slug
        })
    return JsonResponse({'themes': themes})


class StateView(TemplateView):
    template_name = 'states.html'

    def get_context_data(self, **kwargs):
        context = super(StateView, self).get_context_data(**kwargs)
        context['deputies'] = models.Deputy.objects.filter(
            data__region=context['state']
        ).order_by('data__parliamentary_name')
        return context


class DeputyView(DetailView):
    template_name = 'deputy.html'
    pk_url_kwarg = 'deputy_id'
    model = models.Deputy

    def get_context_data(self, **kwargs):
        context = super(DeputyView, self).get_context_data(**kwargs)
        context['deputies'] = models.Deputy.objects.filter(
            data__party=self.object.data.party
        )
        return context


class ProposalsListView(DetailView):
    template_name = 'proposals.html'
    pk_url_kwarg = 'deputy_id'
    model = models.Deputy

    def get_context_data(self, **kwargs):
        context = super(ProposalsListView, self).get_context_data(**kwargs)
        all_proposals = self.object.ordered_proposals

        paginator = Paginator(all_proposals, 10)
        page = self.request.GET.get('p')

        try:
            proposals = paginator.page(page)
        except PageNotAnInteger:
            proposals = paginator.page(1)
        except EmptyPage:
            proposals = paginator.page(paginator.num_pages)

        context['proposals'] = proposals
        return context


class SpeechesListView(DetailView):
    template_name = 'speeches.html'
    pk_url_kwarg = 'deputy_id'
    model = models.Deputy

    def get_context_data(self, **kwargs):
        context = super(SpeechesListView, self).get_context_data(**kwargs)
        all_speeches = self.object.ordered_speeches

        paginator = Paginator(all_speeches, 10)
        page = self.request.GET.get('p')

        try:
            speeches = paginator.page(page)
        except PageNotAnInteger:
            speeches = paginator.page(1)
        except EmptyPage:
            speeches = paginator.page(paginator.num_pages)

        context['speeches'] = speeches
        return context
