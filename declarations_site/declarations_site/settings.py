"""
Django settings for declarations_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

from django_jinja.builtins import DEFAULT_EXTENSIONS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'PLEASEREPLACEMEREPLACEMEREPLACEMDONTLEAVEMELIKETHAT'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'easy_thumbnails',
    'django_jinja',
    'django_jinja.contrib._humanize',
    'django_jinja.contrib._easy_thumbnails',

    'compressor',
    'taggit',
    'modelcluster',

    'wagtail.wagtailcore',
    'wagtail.wagtailadmin',
    'wagtail.wagtaildocs',
    'wagtail.wagtailsnippets',
    'wagtail.wagtailusers',
    'wagtail.wagtailimages',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsearch',
    'wagtail.wagtailredirects',
    'wagtail.wagtailforms',

    'catalog',
    'cms_pages',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

ROOT_URLCONF = 'declarations_site.urls'

WSGI_APPLICATION = 'declarations_site.wsgi.application'

DATABASES = {
    'default': {
        # Strictly PostgreSQL
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

# Setup Elasticsearch default connection
ELASTICSEARCH_CONNECTIONS = {
    'default': {
        'hosts': 'localhost',
        'timeout': 20
    }
}

LANGUAGE_CODE = 'uk-ua'
TIME_ZONE = 'Europe/Kiev'

DATE_FORMAT = "d.m.Y"
USE_I18N = True
USE_L10N = False
USE_TZ = True

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.stats_processor",
                "cms_pages.context_processors.menu_processor"
            ),
            "extensions": DEFAULT_EXTENSIONS + [
                "pipeline.jinja2.ext.PipelineExtension"
            ],
        }
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.stats_processor",
                "cms_pages.context_processors.menu_processor"
            ),
        },
        "APP_DIRS": True,
    },
]

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE_ENABLED = True
PIPELINE_SASS_ARGUMENTS = "-q"
PIPELINE_COMPILERS = ('pipeline.compilers.sass.SASSCompiler',)
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CssminCompressor'

PIPELINE_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS = {
    'css_all': {
        'source_filenames': (
            'sass/style.scss',
        ),
        'output_filename': 'css/merged.css',
        'extra_context': {},
    },

    'css_bi': {
        'source_filenames': (
            "sass/bi/style.scss",
        ),
        'output_filename': 'css/merged_bi.css',
        'extra_context': {},
    },
}

PIPELINE_JS = {
    'js_all': {
        'source_filenames': (
            "js/jquery-1.11.2.js",
            "js/bootstrap.js",
            "js/bootstrap3-typeahead.js",
            "js/ripples.js",
            "js/material.js",
            'js/jquery.magnific-popup.js',
            "js/main.js",
            "js/analytics.js",
            "js/jquery.dataTables.min.js",
            "js/bi/d3.min.js",
            "js/bi/widget_home.js",
        ),
        'output_filename': 'js/merged.js',
    },

    'js_bi': {
        'source_filenames': (
            "js/bi/crossfilter.min.js",
            "js/bi/offices.js",
            "js/bi/csv.js",
            "js/bi/main.js",
        ),
        'output_filename': 'js/merged_bi.js',
    }
}

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = '/media/'

NACP_DECLARATIONS_PATH = ""

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Application settings
CATALOG_PER_PAGE = 30

# django-compressor settings (for a fucking wagtail)
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

LOGIN_URL = "/admin/login/"
WAGTAIL_SITE_NAME = 'Declarations'
# Slug of the analytics page. Handle with care as analytics script
# will use it to find existing page.
ANALYTICS_SLUG = 'analytics'
# Only used during page creation (changeable)
ANALYTICS_TITLE = 'Аналіз декларацій чиновників'


THUMBNAIL_ALIASES = {
    '': {
        'homepage_news': {'size': (390, 220), 'crop': True}
    },
}

SITEMAP_DECLARATIONS_PER_PAGE = 50000

try:
    from .local_settings import *
except ImportError:
    pass


# Init Elasticsearch connections
from elasticsearch_dsl import connections
connections.connections.configure(**ELASTICSEARCH_CONNECTIONS)
