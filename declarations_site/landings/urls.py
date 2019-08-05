from django.conf.urls import url
from .views import LandingPageDetail

urlpatterns = [
    url(r'^(?P<pk>[\w-]+)/$', LandingPageDetail.as_view()),
]