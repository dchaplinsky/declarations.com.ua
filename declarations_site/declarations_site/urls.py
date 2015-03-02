from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', 'catalog.views.home', name='home'),
    url(r'^ajax/suggest$', 'catalog.views.suggest', name='suggest'),
    url(r'^about/$', TemplateView.as_view(template_name='about.jinja'),
        name="about"),
)
