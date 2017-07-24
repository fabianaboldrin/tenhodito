"""tenhodito URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from application import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^data/?$', views.home_json, name='home_data'),
    url(r'^estado/(?P<state>[-\w]+)/$', views.StateView.as_view(),
        name='state'),
    url(r'^estado/(?P<state>[-\w]+)/data$', views.state_json,
        name='state_data'),
    url(r'^deputado/(?P<deputy_id>[\d]+)/$', views.DeputyView.as_view(),
        name='deputy'),
    url(r'^deputado/(?P<deputy_id>[\d]+)/proposicoes$',
        views.ProposalsListView.as_view(), name='proposals_details'),
    url(r'^deputado/(?P<deputy_id>[\d]+)/discursos$',
        views.SpeechesListView.as_view(), name='speeches_details'),
]
