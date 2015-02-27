from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'catalog.views.home', name='home'),
)
