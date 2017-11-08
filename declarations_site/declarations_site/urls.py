from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from django.contrib import admin
from django.views.generic import TemplateView

from catalog import views as catalog_views
from chatbot import urls as chatbot_urls
from spotter import urls as spotter_urls

urlpatterns = [
    url(r'^ajax/suggest$', catalog_views.suggest, name='suggest'),

    url(r'^search$', catalog_views.search, name='search'),
    url(r'^fuzzy_search$', catalog_views.fuzzy_search),
    url(r'^declaration/(?P<declaration_id>[\d\w_\-]+)$', catalog_views.details,
        name='details'),

    url(r'^region$', catalog_views.regions_home, name='regions_home',),
    url(r'^office$', catalog_views.offices_home, name='offices_home',),

    url(r'^toBIfree/$', catalog_views.business_intelligence,
        name='business_intelligence',),

    # Please maintain that order
    url(r'^region/(?P<region_name>[^\/]+)/(?P<office_name>.+)$',
        catalog_views.region_office, name='region_office'),
    url(r'^region/(?P<region_name>.+)$', catalog_views.region,
        name='region'),

    url(r'^office/(?P<office_name>.+)$', catalog_views.office,
        name='office'),

    url(r'^sitemap_general.xml$', catalog_views.sitemap_general,
        name='sitemap_general'),

    url(r'^sitemap_declarations_(?P<page>[\d]+).xml$',
        catalog_views.sitemap_declarations, name='sitemap_declarations'),

    url(r'^sitemap.xml$', catalog_views.sitemap_index,
        name='sitemap_index'),

    url(r'^compare$',
        catalog_views.compare_declarations,
        name='compare'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^bot/', include(chatbot_urls)),
    url(r'user/', include('social_django.urls', namespace='social')),
    url(r'user/', include(spotter_urls)),
    url(r'', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
