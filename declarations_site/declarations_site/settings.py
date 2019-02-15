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
SECRET_KEY = os.getenv('APP_SECRET_KEY', 'verysecretsecretthatmustbereset')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('APP_DEBUG', 'False') == 'True'

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

    'social_django',
    'spotter',
    'chatbot',

    'catalog',
    'cms_pages',
    'procurements',
    'raven.contrib.django.raven_compat',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

ROOT_URLCONF = 'declarations_site.urls'

WSGI_APPLICATION = 'declarations_site.wsgi.application'

DATABASES = {
    'default': {
        # Strictly PostgreSQL
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}

# Setup Elasticsearch default connection
ELASTICSEARCH_CONNECTIONS = {
    'default': {
        'hosts': os.getenv('ES_HOST', 'localhost'),
        'timeout': 30
    }
}

BOTAPI_APP_ID = 'x'
BOTAPI_APP_SECRET = ''
BOTAPI_JWT_VERIFY = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION = 'spotter.utils.clean_username'
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details'
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/userinfo.email']

SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'id,name,email'}

SOCIAL_AUTH_LOGIN_ERROR_URL = '/?login_error'
LOGOUT_REDIRECT = '/'

SITE_URL = 'https://declarations.com.ua'

DEFAULT_DEEPSEARCH = True

SPOTTER_SAVE_FOUND_IDS = False
SPOTTER_TASK_LIMIT = 500
CHATBOT_SERP_COUNT = 5

# EMAIL_SITE_URL used for full hrefs in email templates
EMAIL_SITE_URL = SITE_URL

FROM_EMAIL = 'robot@declarations.com.ua'
EMAIL_HOST = 'localhost'
EMAIL_TIMEOUT = 5

RSS_AUTHOR_NAME = 'Сайт «Декларації» - проект Канцелярської сотні'
RSS_AUTHOR_LINK = SITE_URL
RSS_AUTHOR_EMAIL = 'dbihus@declarations.com.ua'
RSS_TTL = 10800

LANGUAGE_CODE = 'uk-ua'
TIME_ZONE = 'Europe/Kiev'

DATE_FORMAT = "d.m.Y"
DATETIME_FORMAT = 'd.m.Y H:i:s'
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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "catalog.context_processors.settings_processor",
                "cms_pages.context_processors.menu_processor"
            ),
            "extensions": DEFAULT_EXTENSIONS + [
                'pipeline.jinja2.PipelineExtension',
                'wagtail.wagtailcore.jinja2tags.core',
                'wagtail.wagtailimages.jinja2tags.images',
            ],
            "globals": {
                "replace_arg": "catalog.utils.replace_arg",
                "sort_flag": "catalog.utils.sort_flag",
                "generate_all_names": "names_translator.name_utils.generate_all_names",
            }
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
                "catalog.context_processors.settings_processor",
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
    'pipeline.finders.PipelineFinder',
)

# Can you include here https://github.com/dizballanze/django-compressor-autoprefixer , please?
PIPELINE = {
    'COMPILERS': ('pipeline.compilers.sass.SASSCompiler',),
    'SASS_ARGUMENTS': '-q',
    'CSS_COMPRESSOR': 'pipeline.compressors.cssmin.CssminCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.uglifyjs.UglifyJSCompressor',
    'STYLESHEETS': {
        'css_all': {
            'source_filenames': (
                'sass/style.scss',
            ),
            'output_filename': 'css/merged.css',
            'extra_context': {},
        },
        'css_infographics': {
            'source_filenames': (
                'sass/infographics.scss',
            ),
            'output_filename': 'css/merged_infographics.css',
            'extra_context': {},
        }
    },
    'JAVASCRIPT': {
        'js_all': {
            'source_filenames': (
                "js/jquery-1.11.2.js",
                "js/bootstrap.js",
                "js/bootstrap3-typeahead.js",
                "js/ripples.js",
                "js/material.js",
                'js/jquery.magnific-popup.js',
                "js/main.js",
                "js/decl-compare.js",
                "js/user.js",
                "js/analytics.js",
            ),
            'output_filename': 'js/merged.js',
        },

        'js_charts': {
            'source_filenames': (
                "js/Chart.bundle.js",
                "js/accounting.js",
                "js/compare-charts.js",
            ),
            'output_filename': 'js/merged_charts.js',
        },

        'js_infographics': {
            'source_filenames': (
                "js/d3.js",
                "js/d3-tip.js",
                "js/infographics_on_main.js",
            ),
            'output_filename': 'js/merged_infographics.js',
        }
    }
}


STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = '/media/'

NACP_DECLARATIONS_PATH = os.getenv('APP_NACP_PATH', '')

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Application settings
CATALOG_PER_PAGE = 30
MAX_PAGES = 33334


LOGIN_URL = "/admin/login/"
WAGTAIL_SITE_NAME = 'Declarations'
# Slug of the analytics page. Handle with care as analytics script
# will use it to find existing page.
ANALYTICS_SLUG = 'analytics'
# Only used during page creation (changeable)
ANALYTICS_TITLE = 'Аналіз декларацій чиновників'

EMAIL_TIMEOUT = 5
BROADCAST_TELEGRAM_CHANNEL = "@EndlessFrustration"
BROADCAST_TELEGRAM_BOT_TOKEN = ""
BROADCASTER_USER = "whistleblower@telegram.broadcast"

SITEMAP_DECLARATIONS_PER_PAGE = 50000

try:
    from .local_settings import *
except ImportError:
    pass


# Init Elasticsearch connections
from elasticsearch_dsl import connections
connections.connections.configure(**ELASTICSEARCH_CONNECTIONS)
