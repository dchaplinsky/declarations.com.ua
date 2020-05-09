from django.conf.urls import url
from .views import LandingPageDetail, LandingPagePerson

urlpatterns = [
    url(r'^(?P<pk>[\w-]+)/$', LandingPageDetail.as_view()),
    url(r'^(?P<pk>[\w-]+)/(?P<pk2>\d+)$', LandingPagePerson.as_view()),
]