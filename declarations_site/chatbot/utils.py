import requests
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from elasticsearch_dsl import Search
from catalog.constants import CATALOG_INDICES
from catalog.utils import base_search_query
from chatbot.models import ChatHistory


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


def client_credentials():
    cached_creds = cache.get(settings.BOTAPI_APP_ID)
    if cached_creds:
        return cached_creds
    tokenURL = 'https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': settings.BOTAPI_APP_ID,
        'client_secret': settings.BOTAPI_APP_SECRET,
        'scope': 'https://api.botframework.com/.default'
    }
    response = requests.post(tokenURL, data, timeout=10)
    creds = response.json()
    if creds and creds['expires_in']:
        cache.set(settings.BOTAPI_APP_ID, creds, creds['expires_in'] - 5)
    return creds


def chat_response(data, message='', messageType='message', attachments=None):
    if data.get('text'):
        ChatHistory(
            from_id=data['from']['id'][:250],
            from_name=data['from']['name'][:250],
            conversation=data['conversation']['id'][:250],
            query=data['text'][:250],
            answer=message[:250],
            timestamp=data['timestamp'][:40]
        ).save()

    creds = client_credentials()

    if not settings.DEBUG:
        data['serviceUrl'] = 'https://api.botframework.com'
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
