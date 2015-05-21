"""
Django settings for declarations_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = '/media/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'PLEASEREPLACEMEREPLACEMEREPLACEMDONTLEAVEMELIKETHAT'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

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
    'django_jinja',
    'django_jinja.contrib._humanize',

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

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "catalog.context_processors.stats_processor",
    "cms_pages.context_processors.menu_processor"
)

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

USE_I18N = False
USE_L10N = False
USE_TZ = True


TEMPLATE_LOADERS = (
    'django_jinja.loaders.AppLoader',
    'django_jinja.loaders.FileSystemLoader',
)
DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'
JINJA2_EXTENSIONS = ["pipeline.jinja2.ext.PipelineExtension"]

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'pipeline.finders.PipelineFinder',
)

PIPELINE_CSS = {
    'css_all': {
        'source_filenames': (
            'css/bootstrap.css',
            'css/material.css',
            'css/ripples.css',
            'css/animate.css',
            'css/style.css',
            'css/decls.css',
        ),
        'output_filename': 'css/merged.css',
        'extra_context': {
            'media': 'screen,projection',
        },
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
            "js/main.js"
        ),
        'output_filename': 'js/merged.js',
    }
}

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Application settings
CATALOG_PER_PAGE = 30

# django-compressor settings (for a fucking wagtail)
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

LOGIN_URL = "/admin/login/"
WAGTAIL_SITE_NAME = 'Declarations'

try:
    from .local_settings import *
except ImportError:
    pass


# Init Elasticsearch connections
from elasticsearch_dsl import connections
connections.connections.configure(**ELASTICSEARCH_CONNECTIONS)
