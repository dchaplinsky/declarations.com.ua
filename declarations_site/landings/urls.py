from django.conf.urls import url
from .views import LandingPageDetail, LandingPagePerson

urlpatterns = [
    url(r"^(?P<pk>[\w-]+)/$", LandingPageDetail.as_view(), name="landing_page_details"),
    url(
        r"^(?P<body_id>[\w-]+)/(?P<pk>\d+)$",
        LandingPagePerson.as_view(),
        name="landing_page_person",
    ),
]
