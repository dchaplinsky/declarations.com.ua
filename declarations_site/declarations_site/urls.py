from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url, re_path
from django.urls import path
from django.views.i18n import JavaScriptCatalog


from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

from catalog import views as catalog_views
from chatbot import urls as chatbot_urls
from landings import urls as landing_urls
from spotter import urls as spotter_urls

urlpatterns = [
    url(r"^search/suggest$", catalog_views.SuggestView.as_view(), name="new_suggest"),
    url(r"^fuzzy_search$", catalog_views.fuzzy_search),
    url(
        r"^sitemap_general.xml$", catalog_views.sitemap_general, name="sitemap_general"
    ),
    url(
        r"^sitemap_declarations_(?P<page>[\d]+).xml$",
        catalog_views.sitemap_declarations,
        name="sitemap_declarations",
    ),
    url(r"^sitemap.xml$", catalog_views.sitemap_index, name="sitemap_index"),
    # url(r'^admin/', include(admin.site.urls)),
    path("admin/", admin.site.urls),
    url(r"^nested_admin/", include("nested_admin.urls")),
    re_path(r"^cms/", include(wagtailadmin_urls)),
    re_path(r"^documents/", include(wagtaildocs_urls)),
    re_path(r"^pages/", include(wagtail_urls)),
    url(r"^bot/", include(chatbot_urls)),
    url(r"user/", include("social_django.urls", namespace="social")),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]


if settings.PROMETHEUS_ENABLE:
    urlpatterns = [url('^prometheus/', include('django_prometheus.urls'))] + urlpatterns

handler404 = TemplateView.as_view(template_name="404.jinja")

urlpatterns += i18n_patterns(
    path("search", catalog_views.search, name="search"),
    path("declaration/<str:declaration_id>", catalog_views.details, name="details"),
    path("sample/<str:declaration_id>", catalog_views.sample_details, name="sample_details"),
    url(r"^region$", catalog_views.regions_home, name="regions_home"),
    url(r"^office$", catalog_views.offices_home, name="offices_home"),
    url(r"^BI/$", catalog_views.business_intelligence, name="business_intelligence"),
    # Please maintain that order
    url(
        r"^region/(?P<region_name>[^\/]+)/(?P<office_name>.+)$",
        catalog_views.region_office,
        name="region_office",
    ),
    url(r"^region/(?P<region_name>.+)$", catalog_views.region, name="region"),
    url(r"^office/(?P<office_name>.+)$", catalog_views.office, name="office"),

    url(r"^compare$", catalog_views.compare_declarations, name="compare"),
    url(r"user/", include(spotter_urls)),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r"^l/", include(landing_urls)),
    url(r"", include(wagtail_urls)),
    prefix_default_language=False,
)
