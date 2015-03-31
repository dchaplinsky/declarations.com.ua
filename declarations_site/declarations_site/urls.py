from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', 'catalog.views.home', name='home'),
    url(r'^ajax/suggest$', 'catalog.views.suggest', name='suggest'),
    url(r'^about/$', TemplateView.as_view(template_name='about.jinja'),
        name="about"),

    url(r'^search$', 'catalog.views.search', name='search'),
    url(r'^declaration/(?P<declaration_id>\d+)$', 'catalog.views.details',
        name='details'),
    url(r'^region$', 'catalog.views.regions_home', name='regions_home',),

    url(r'^region/(?P<region_name>[^\/]+)/(?P<office_name>.+)$', 'catalog.views.region_office',
        name='region_office'),
    url(r'^region/(?P<region_name>.+)$', 'catalog.views.region',
        name='region'),

    url(r'^office/(?P<office_name>.+)$', 'catalog.views.office',
        name='office'),
)
