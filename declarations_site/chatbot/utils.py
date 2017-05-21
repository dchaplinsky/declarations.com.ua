import jwt
import requests
import logging
from hashlib import sha1
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from elasticsearch_dsl import Search
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from catalog.constants import CATALOG_INDICES
from catalog.utils import base_search_query
from chatbot.models import ChatHistory


logger = logging.getLogger(__name__)


def ukr_plural(value, *args):
    value = int(value)
    rem = value % 10
    if value > 4 and value < 20:
        return args[2]
    elif rem == 1:
        return args[0]
    elif rem > 1 and rem < 5:
        return args[1]
    else:
        return args[2]


def simple_search(query, deepsearch=False):
    base_search = Search(index=CATALOG_INDICES)
    sort = 'general.full_name_for_sorting'
    source = ['meta.id', 'general.*', 'intro.*', 'declaration.*']

    search = base_search_query(base_search, query, deepsearch, {})
    search = search.sort(sort).source(source)

    if not hasattr(search, 'found_total'):
        search.found_total = search.count()

    return search


def botframework_jwt_keys():
    # This is a static URL that you can hardcode into your application.
    openidURL = 'https://login.botframework.com/v1/.well-known/openidconfiguration'
    cached_keys = cache.get(openidURL)
    if cached_keys:
        return cached_keys

    response = requests.get(openidURL, timeout=10)
    config = response.json()

    if config['issuer'] != 'https://api.botframework.com':
        return False

    response = requests.get(config['jwks_uri'], timeout=10)
    keys = response.json()
    if keys.get('keys'):
        cache.set(openidURL, keys, 86400)
    return keys


def get_jwt_public_key(kid, channel):
    keys = botframework_jwt_keys()
    for k in keys['keys']:
        if k['kid'] == kid and channel in k.get('endorsements', []):
            break
    assert k['kid'] == kid, 'Key not found'
    pem_cert = '-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----'.format(k['x5c'][0])
    cert = load_pem_x509_certificate(pem_cert.encode(), default_backend())
    return cert.public_key()


def verify_jwt(auth, data):
    if not settings.BOTAPI_JWT_VERIFY:
        return True

    try:
        method, token = auth.split(' ')
        token_fingerprint = sha1(token.encode()).hexdigest()
    except (TypeError, ValueError, AttributeError):
        logger.warning('Bad auth string')
        return False

    if method != 'Bearer':
        logger.warning('Bad auth method')
        return False

    if len(token) > 200 and cache.get(token_fingerprint):
        return True

    try:
        headers = jwt.get_unverified_header(token)
        pub_key = get_jwt_public_key(headers['kid'], data['channelId'])
        payload = jwt.decode(token, pub_key, audience=settings.BOTAPI_APP_ID, leeway=300)
    except Exception as e:
        logger.warning('JWT decode error {}'.format(e))
        return False

    if payload['iss'] != 'https://api.botframework.com':
        logger.warning('Bad JWT issuer')
        return False

    # JWT payload has serviceurl (lowercase) and data has serviceUrl (camel)
    if payload['serviceurl'] != data['serviceUrl']:
        logger.warning('Bad JWT serviceUrl')
        return False

    cache.set(token_fingerprint, 1, 300)
    return True


def client_credentials():
    cached_creds = cache.get(settings.BOTAPI_APP_ID)
    if cached_creds:
        return cached_creds
    # Botframework v3.1 login url may be hardcoded into application
    tokenURL = 'https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': settings.BOTAPI_APP_ID,
        'client_secret': settings.BOTAPI_APP_SECRET,
        'scope': 'https://api.botframework.com/.default'
    }
    response = requests.post(tokenURL, data, timeout=10)
    creds = response.json()
    if creds and creds.get('expires_in'):
        cache.set(settings.BOTAPI_APP_ID, creds, creds['expires_in'] - 10)
    return creds


def chat_response(data, message='', messageType='message', attachments=None):
    if data.get('text'):
        ChatHistory(
            from_id=data.get('from', {}).get('id', '')[:250],
            from_name=data.get('from', {}).get('name', '')[:250],
            channel=data.get('channelId', '')[:250],
            conversation=data.get('conversation', {}).get('id', '')[:250],
            query=data['text'][:250],
            answer=message[:250],
            timestamp=data.get('timestamp', '')[:40]
        ).save()

    creds = client_credentials()

    responseURL = "{}/v3/conversations/{}/activities/{}".format(
        data['serviceUrl'],
        data['conversation']['id'],
        data['id'])
    resp = {
        'type': messageType,
        'timestamp': datetime.now().isoformat(),
        'from': data['recipient'],
        'conversation': data['conversation'],
        'recipient': data['from'],
        'replyToId': data['id'],
        'text': message,
    }
    if attachments:
        resp['attachments'] = attachments
    headers = {
        'Authorization': '{} {}'.format(creds['token_type'], creds['access_token'])
    }
    requests.post(responseURL, json=resp, headers=headers, timeout=10)
