from django.conf import settings

from datetime import date
from elasticsearch_dsl import Search
from .constants import CATALOG_INDICES
from .elastic_models import NACPDeclaration

def settings_processor(request):
    return {
        "SITE_URL": settings.SITE_URL,
        "CURR_YEAR": date.today().year,
        "ENABLED_FLAGS": NACPDeclaration.ENABLED_FLAGS,
    }
