from django.conf import settings

from elasticsearch_dsl import Search
from .constants import CATALOG_INDICES

def settings_processor(request):
    return {
        "SITE_URL": settings.SITE_URL
    }
