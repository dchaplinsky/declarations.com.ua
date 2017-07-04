import jwt
import json
import logging
import requests
from time import sleep
from hashlib import sha1
from random import randint
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from elasticsearch_dsl import Search
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from requests.exceptions import RequestException, BaseHTTPError
from catalog.constants import CATALOG_INDICES
from catalog.utils import base_search_query
from chatbot.models import ChatHistory
from spotter.utils import (DjangoStorage, clean_username, save_search_task,
    find_search_task, list_search_tasks, get_user_notify)


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


def requests_retry(func, *args, **kwargs):
    max_retries = kwargs.pop('max_retries', 5)
    retry_sleep = kwargs.pop('retry_sleep', 0)
    # send response with retry
    for retry in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (IOError, RequestException, BaseHTTPError) as e:
            logger.error('Retry({}) {} {}'.format(retry, args, e))
            if retry_sleep:
                sleep(retry_sleep)


def botframework_jwt_keys():
    # This is a static URL that you can hardcode into your application.
    openidURL = 'https://login.botframework.com/v1/.well-known/openidconfiguration'
    cached_keys = cache.get(openidURL)
    if cached_keys:
        return cached_keys

    response = requests_retry(requests.get, openidURL, timeout=30)
    config = response.json()

    if config['issuer'] != 'https://api.botframework.com':
        return False

    response = requests_retry(requests.get, config['jwks_uri'], timeout=30)
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
    response = requests_retry(requests.post, tokenURL, data, timeout=30)
    creds = response.json()
    if creds and creds.get('expires_in'):
        cache.set(settings.BOTAPI_APP_ID, creds, creds['expires_in'] - 10)
    return creds


def chat_last_message(data, return_text=False, not_older_than=5):
    from_id = data.get('from', {}).get('id', '')[:250]
    from_name = data.get('from', {}).get('name', '')[:250]
    channel = data.get('channelId', '')[:250]
    conversation = data.get('conversation', {}).get('id', '')[:250]

    if from_id and channel and conversation:
        not_older = timezone.now() - timedelta(minutes=not_older_than)
        try:
            msg = ChatHistory.objects.filter(from_id=from_id, from_name=from_name, channel=channel,
                conversation=conversation, created__gt=not_older).order_by('-created')[0]
        except IndexError:
            return None
        if return_text:
            return msg.query
        return msg


def chat_user_email(data):
    from_id = data.get('from', {}).get('id', '')[:250]
    channel = data.get('channelId', '')[:250]

    if from_id and channel:
        return '{}@{}.chatbot'.format(from_id, channel)


def get_chat_user_by_email(chat_email):
    for user in DjangoStorage.user.get_users_by_email(chat_email):
        return user


def get_or_create_chat_user(data):
    chat_email = chat_user_email(data)
    user = get_chat_user_by_email(chat_email)

    if not user:
        from_id = data.get('from', {}).get('id', '')[:250]
        channel = data.get('channelId', '')[:250]
        name = data.get('from', {}).get('name', '')[:250]

        if not from_id or not channel:
            raise ValueError('Недостатньо даних')

        username = '{}{}'.format(channel, randint(1e6, 1e8))
        username = clean_username(username)
        # always remember about birthday paradox
        while DjangoStorage.user.get_user(username=username):
            username = '{}{}'.format(channel, randint(1e6, 1e8))
            username = clean_username(username)

        if name and ' ' in name:
            first_name, last_name = name.split(' ', 1)
        else:
            first_name, last_name = name, ''

        user = DjangoStorage.user.create_user(username=username, email=chat_email,
            first_name=first_name, last_name=last_name)
        DjangoStorage.user.create_social_auth(user=user, uid=from_id, provider=channel)

    return user


def chat_response(data, message='', messageType='message', attachments=None, auto_reply=False, save_answer=True):
    if data.get('text', ''):
        short_answer = message[:80] if save_answer else '-'
        ChatHistory(
            user=get_chat_user_by_email(chat_user_email(data)),
            from_id=data.get('from', {}).get('id', '')[:250],
            from_name=data.get('from', {}).get('name', '')[:250],
            channel=data.get('channelId', '')[:250],
            conversation=data.get('conversation', {}).get('id', '')[:250],
            query=data['text'][:250],
            answer=short_answer,
            timestamp=data.get('timestamp', '')[:40],
            auto_reply=auto_reply
        ).save()

    creds = client_credentials()

    responseURL = "{}/v3/conversations/{}/activities/{}".format(
        data['serviceUrl'],
        data['conversation']['id'],
        data['id'])
    resp = {
        'type': messageType,
        'timestamp': timezone.now().isoformat(),
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
    retry_sleep = 5 if auto_reply else 0
    requests_retry(requests.post, responseURL, json=resp, headers=headers, timeout=30,
        retry_sleep=retry_sleep)


def send_to_chat(notify, context):
    from chatbot.views import decl_list_to_chat_cards

    plural = ukr_plural(context['found_new'], 'нову декларацію', 'нові декларації', 'нових декларацій')
    message = 'За підпискою: {}'.format(context['query'])
    message += '\n\nЗнайдено {} {}'.format(context['found_new'], plural)
    if context['found_new'] > settings.CHATBOT_SERP_COUNT:
        message += '\n\nПоказані перші {}'.format(settings.CHATBOT_SERP_COUNT)

    data = json.loads(notify.task.chat_data)
    data['text'] = context['query']

    deepsearch = 'on' if notify.task.deepsearch else ''
    attachments = decl_list_to_chat_cards(context['decl_list'], data, settings, deepsearch,
        notify_id=notify.id)
    chat_response(data, message, attachments=attachments, auto_reply=True)


def create_subscription(data, query):
    user = get_or_create_chat_user(data)

    if not user.is_active:
        raise ValueError('Користувач заблокований')

    data.pop('text', '')

    return save_search_task(user, query, chat_data=json.dumps(data))


def find_subscription(data, query, deepsearch=False):
    user = get_chat_user_by_email(chat_user_email(data))
    if not user:
        return
    return find_search_task(user, query, deepsearch)


def find_subscription2(data, query):
    task = find_subscription(data, query, deepsearch=False)
    if not task:
        task = find_subscription(data, query, deepsearch=True)
    return task


def list_subscriptions(data):
    user = get_chat_user_by_email(chat_user_email(data))
    if not user:
        return []
    return list_search_tasks(user)


def load_notify(data, notify_id):
    user = get_chat_user_by_email(chat_user_email(data))
    if not user:
        return
    return get_user_notify(user, notify_id)
