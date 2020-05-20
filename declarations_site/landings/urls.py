from django.conf.urls import url
from .views import LandingPageDetail, LandingPagePerson, LandingPageList

urlpatterns = [
    url(r"^$", LandingPageList.as_view(), name="landing_page_list"),
    url(r"^(?P<pk>[\w-]+)/$", LandingPageDetail.as_view(), name="landing_page_details"),
    url(
        r"^(?P<body_id>[\w-]+)/(?P<pk>\d+)$",
        LandingPagePerson.as_view(),
        name="landing_page_person",
    ),
]
