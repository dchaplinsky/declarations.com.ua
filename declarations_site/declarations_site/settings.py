"""
Django settings for declarations_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import sentry_sdk
import raven
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

from django_jinja.builtins import DEFAULT_EXTENSIONS

def get_env_str(k, default):
    return os.environ.get(k, default)

def get_env_str_list(k, default=""):
    if os.environ.get(k) is not None:
        return os.environ.get(k).strip().split(" ")
    return default

def get_env_bool(k, default):
    return str(get_env_str(k, default)).lower() in ["1", "y", "yes", "true"]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = get_env_str('MEDIA_ROOT', os.path.join(BASE_DIR, "media"))
STATIC_ROOT = get_env_str('STATIC_ROOT', os.path.join(BASE_DIR, "static"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_str('SECRET_KEY', os.getenv('APP_SECRET_KEY', 'verysecretsecretthatmustbereset'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('APP_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = get_env_str_list('ALLOWED_HOSTS', [])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'django_jinja',
    'django_jinja.contrib._humanize',
    "django_jinja.contrib._easy_thumbnails",
    "easy_thumbnails",
    "ckeditor",
    "ckeditor_uploader",


    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',

    'social_django',
    'spotter',
    'chatbot',
    'landings',
    "nested_admin",

    'catalog',
    'cms_pages',
    'procurements',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'declarations_site.urls'

WSGI_APPLICATION = 'declarations_site.wsgi.application'

PROMETHEUS_ENABLE = get_env_bool("PROMETHEUS_ENABLE", False)
db_backend = "django.db.backends.postgresql_psycopg2"
if PROMETHEUS_ENABLE:
    db_backend = "django_prometheus.db.backends.postgresql"


DATABASES = {
    'default': {
        # Strictly PostgreSQL
        'ENGINE': db_backend,
        'NAME': get_env_str('DB_NAME', None),
        'USER': get_env_str('DB_USER', None),
        'PASSWORD': get_env_str('DB_PASS', None),
        'HOST': get_env_str('DB_HOST', None),
        'PORT': get_env_str('DB_PORT', '5432'),
    }
}

# Setup Elasticsearch default connection
ELASTICSEARCH_CONNECTIONS = {
    'default': {
        'hosts': get_env_str('ELASTICSEARCH_DSN', 'localhost:9200'),
        'timeout': int(get_env_str('ELASTICSEARCH_TIMEOUT', '30')),
    }
}

BOTAPI_APP_ID = get_env_str('BOTAPI_APP_ID', 'x')
BOTAPI_APP_SECRET = get_env_str('BOTAPI_APP_SECRET', '')
BOTAPI_JWT_VERIFY = get_env_bool('BOTAPI_JWT_VERIFY', False)

DB_CACHE_TABLE = get_env_str('DB_CACHE_TABLE', None)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' \
            if DB_CACHE_TABLE is None \
                else 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': DB_CACHE_TABLE
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

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = get_env_str('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = get_env_str('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/userinfo.email']

SOCIAL_AUTH_FACEBOOK_KEY = get_env_str('SOCIAL_AUTH_FACEBOOK_KEY', '')
SOCIAL_AUTH_FACEBOOK_SECRET = get_env_str('SOCIAL_AUTH_FACEBOOK_SECRET', '')
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

FROM_EMAIL = get_env_str('FROM_EMAIL', 'robot@declarations.com.ua')
DEFAULT_FROM_EMAIL = get_env_str('DEFAULT_FROM_EMAIL', None)
EMAIL_HOST = get_env_str('EMAIL_HOST', 'localhost')
EMAIL_HOST_USER = get_env_str('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = get_env_str('EMAIL_HOST_PASSWORD', None)
EMAIL_PORT = int(get_env_str('EMAIL_PORT', '587'))
EMAIL_USE_TLS = get_env_bool('EMAIL_USE_TLS', False)
EMAIL_TIMEOUT = int(get_env_str('EMAIL_TIMEOUT', '5'))

RSS_AUTHOR_NAME = 'Сайт «Декларації» - проект Канцелярської сотні'
RSS_AUTHOR_LINK = SITE_URL
RSS_AUTHOR_EMAIL = 'dbihus@declarations.com.ua'
RSS_TTL = 10800

TIME_ZONE = 'Europe/Kiev'

DATE_FORMAT = "d.m.Y"
DATETIME_FORMAT = 'd.m.Y H:i:s'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'uk'
gettext = lambda s: s
LANGUAGES = (
    ('uk', gettext('Ukrainian')),
    ('en', gettext('English')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

APPEND_SLASH = False

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
                "django.template.context_processors.i18n",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "catalog.context_processors.settings_processor",
                "cms_pages.context_processors.menu_processor"
            ),
            "extensions": DEFAULT_EXTENSIONS + [
                'pipeline.jinja2.PipelineExtension',
                'wagtail.core.jinja2tags.core',
                'wagtail.images.jinja2tags.images',
                'jinja2.ext.i18n',
            ],
            "globals": {
                "replace_arg": "catalog.utils.replace_arg",
                "sort_flag": "catalog.utils.sort_flag",
                "generate_all_names": "names_translator.name_utils.generate_all_names",
                "translate_url": "catalog.utils.translate_url",
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
        }
    },
    'JAVASCRIPT': {
        'js_all': {
            'source_filenames': (
                'js/jquery.min.js',
                'js/typeahead.bundle.js',
                'js/partials/popup.js',
                'js/partials/mobile-menu.js',
                'js/partials/n-select.js',
                'js/partials/n-tooltip.js',
                'js/partials/n-table.js',
                'js/partials/search-form.js',
                'js/partials/modal.js',
                'js/partials/account-block.js',
                'js/partials/request-block.js',
                'js/partials/login-block.js',
                'js/partials/card-actions.js',
                'js/partials/compare-card.js',
                'js/partials/compare-popup.js',
                'js/partials/add-request.js',
                'js/partials/sort-block.js',
                'js/partials/analytics-tabs.js',
                'js/partials/declaration.js',
                'js/partials/tabs.js',
            ),
            'output_filename': 'js/merged.js',
        },
        'js_landing': {
            'source_filenames': (
                'js/pages/landing.js',
            ),
            'output_filename': 'js/merged_landing.js',
        },
        'js_charts': {
            'source_filenames': (
                "js/Chart.bundle.js",
                "js/cytoscape.min.js",
                "js/accounting.js",
                "js/compare-charts.js",
            ),
            'output_filename': 'js/merged_charts.js',
        }
    }
}


STATIC_URL = '/static/'
MEDIA_URL = '/media/'

NACP_DECLARATIONS_PATH = get_env_str('NACP_DECLARATIONS_PATH', '')

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Application settings
CATALOG_PER_PAGE = 30
MAX_PAGES = int(get_env_str('MAX_PAGES', '33334'))


LOGIN_URL = "/admin/login/"
WAGTAIL_SITE_NAME = 'Declarations'
# Slug of the analytics page. Handle with care as analytics script
# will use it to find existing page.
ANALYTICS_SLUG = 'analytics'
# Only used during page creation (changeable)
ANALYTICS_TITLE = 'Аналіз декларацій чиновників'

EMAIL_TIMEOUT = 5
BROADCAST_TELEGRAM_CHANNEL = "@EndlessFrustration"
BROADCAST_TELEGRAM_BOT_TOKEN = get_env_str('BROADCAST_TELEGRAM_BOT_TOKEN', '')
BROADCASTER_USER = "whistleblower@telegram.broadcast"

SITEMAP_DECLARATIONS_PER_PAGE = 50000

try:
    GIT_VERSION = raven.fetch_git_sha(os.path.abspath(os.path.join(BASE_DIR, "..")))
except raven.exceptions.InvalidGitRepository:
    GIT_VERSION = "undef"

LOGGERS_TO_IGNORE = [
    "django.security.DisallowedHost",
    "dragnet.nacp_parser",
    "spotter.utils",
]

SENTRY_DSN = get_env_str('SENTRY_DSN', None)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        release=get_env_str('VERSION', GIT_VERSION),
    )

    for l in LOGGERS_TO_IGNORE:
        ignore_logger(l)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (250, 250), 'crop': True},
    },
}

if PROMETHEUS_ENABLE:
    MIDDLEWARE = (
        ['django_prometheus.middleware.PrometheusBeforeMiddleware',] +
        MIDDLEWARE +
        ['django_prometheus.middleware.PrometheusAfterMiddleware',]
    )

    INSTALLED_APPS = INSTALLED_APPS + ['django_prometheus',]

try:
    from .local_settings import *
except ImportError:
    pass


# Init Elasticsearch connections
from elasticsearch_dsl import connections
connections.connections.configure(**ELASTICSEARCH_CONNECTIONS)
