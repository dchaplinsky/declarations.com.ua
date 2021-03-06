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
from django.urls import reverse
from django.template.loader import render_to_string

from elasticsearch_dsl import Search
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from requests.exceptions import RequestException, BaseHTTPError
from social_django.models import DjangoStorage
import telegram

from catalog.constants import CATALOG_INDICES
from catalog.utils import base_search_query
from chatbot.models import ChatHistory
from spotter.utils import (ukr_plural, clean_username, save_search_task,
    find_search_task, list_search_tasks, get_user_notify, get_login_temporary_link)


logger = logging.getLogger(__name__)

_BROADCAST_BOT_INSTANCE = None

TABLE_LINE = ("=" * 15)


def get_broadcast_bot_instance():
    global _BROADCAST_BOT_INSTANCE
    if not _BROADCAST_BOT_INSTANCE:
        _BROADCAST_BOT_INSTANCE = telegram.Bot(token=settings.BROADCAST_TELEGRAM_BOT_TOKEN)
    return _BROADCAST_BOT_INSTANCE


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
    # perform request with retry
    for retry in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (IOError, RequestException, BaseHTTPError) as e:
            logger.error('Retry({}) {} {}'.format(retry, args, e))
            if retry_sleep:
                sleep(retry_sleep)


def telegram_retry(func, *args, **kwargs):
    max_retries = kwargs.pop('max_retries', 5)
    retry_sleep = kwargs.pop('retry_sleep', 0)
    # perform request with retry
    for retry in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (telegram.error.TimedOut,) as e:
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


def chat_last_message(data, as_text=False, not_older_than=5):
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
        if as_text:
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
        short_answer = message.strip(' \r\n\t=-')[:80] if save_answer else '-'
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

    if data.get('channelId', '') == 'skype' and "\n\n-\n\n" in message:
        message = message.replace("\n\n-\n\n", "\n\n")

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
    if auto_reply and data.get('channelId', '') == 'facebook':
        resp['channelData'] = {
            "messaging_type": "MESSAGE_TAG",
            "notification_type": "REGULAR",
            "tag": "NON_PROMOTIONAL_SUBSCRIPTION",
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
    message = 'За підпискою: {} '.format(context['query_title'])
    message += '\n\nЗнайдено {} {}'.format(context['found_new'], plural)
    if context['found_new'] > settings.CHATBOT_SERP_COUNT:
        message += '\n\nПоказані перші {}'.format(settings.CHATBOT_SERP_COUNT)
    message = TABLE_LINE + "\n\n{}\n\n".format(message) + TABLE_LINE

    data = json.loads(notify.task.chat_data)
    data['text'] = context['query']

    deepsearch = 'on' if notify.task.deepsearch else ''
    attachments = decl_list_to_chat_cards(context['decl_list'], data, settings, deepsearch,
        total=notify.found_new, notify_id=notify.id)
    chat_response(data, message, attachments=attachments, auto_reply=True)
    return 1


# LITTLE COPY-PASTAH wouldn't hurt for now
def decl_list_to_messages(decl_list):
    from chatbot.views import join_res
    attachments = []
    for found in decl_list:
        if 'date' in found.intro:
            found.intro.date = 'подана ' + str(found.intro.date)[:10]
        if 'corrected' in found.intro:
            if found.intro.corrected:
                found.intro.corrected = 'Уточнена'
        url = settings.SITE_URL + reverse('details', args=[found.meta.id])

        att = {
            "title": join_res(found.general, ('last_name', 'name', 'patronymic'), ' '),
            "subtitle": join_res(found.intro, ('declaration_year', 'doc_type', 'corrected', 'date'), ', '),
            "text": join_res(found.general.post, ('region', 'office', 'post'), ', '),
            "url": url
        }

        attachments.append(att)
    return attachments


def send_to_channels(notify, context):
    bot_instance = get_broadcast_bot_instance()
    for att in decl_list_to_messages(context['decl_list']):
        telegram_retry(bot_instance.send_message,
            chat_id=settings.BROADCAST_TELEGRAM_CHANNEL,
            text=render_to_string("telegram_card.jinja", att),
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        sleep(2)

    return 1


def get_chat_login_link(data):
    user = get_or_create_chat_user(data)

    if not user.is_active:
        raise ValueError('Користувач заблокований')

    return get_login_temporary_link(user.id, user.email)


def create_subscription(data, query):
    user = get_or_create_chat_user(data)

    if not user.is_active:
        raise ValueError('Користувач заблокований')

    data.pop('text', '')

    return save_search_task(user, query, chat_data=json.dumps(data))


def find_subscription(data, query, **kwargs):
    user = get_chat_user_by_email(chat_user_email(data))
    if not user:
        return
    return find_search_task(user, query, **kwargs)


def list_subscriptions(data):
    user = get_chat_user_by_email(chat_user_email(data))
    if not user:
        return []
    return list_search_tasks(user)


def load_notify(data, notify_id):
    email = chat_user_email(data)
    if not email:
        return
    return get_user_notify(notify_id, email=email, task__is_enabled=True)
