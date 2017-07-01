import re
import json
from random import choice
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,
    HttpResponseNotAllowed)
from chatbot.utils import (ukr_plural, chat_response, simple_search, verify_jwt, chat_last_message,
    create_subscription, find_subscription2, list_subscriptions)


def reverse_qs(viewname, qs=None, **kwargs):
    url = reverse(viewname, **kwargs)
    if qs:
        url += '?' + urlencode(qs)
    return url


def botcmd_subscribe(data):
    text = data['text']

    if ' ' in text:
        _, text = text.split(' ', 1)
    else:
        text = chat_last_message(data, True)

    if not text or is_bot_command(text):
        return chat_response(data, 'Спочатку зробіть запит')

    try:
        create_subscription(data, text.strip())
        message = 'Створено підписку за запитом: "{}",\n\n'.format(text)
        message += 'Введіть "підписки" щоб подивитись весь список.'
        chat_response(data, message)
    except Exception as e:
        chat_response(data, 'Не вдалось створити підписку: {}'.format(e))


def botcmd_unsubscribe(data):
    text = data['text']

    if ' ' in text:
        _, text = text.split(' ', 1)
    else:
        text = chat_last_message(data, True)

    if not text or is_bot_command(text):
        return chat_response(data, 'Спочатку зробіть запит')

    task = find_subscription2(data, text.strip())

    if not task:
        return chat_response(data, 'Завдання з запитом "{}" не знайдено'.format(text))

    task.is_enabled = False
    task.is_deleted = True
    task.save()

    chat_response(data, 'Завдання відмінено, ви більше не будете отримувати повідомлень за цим запитом.')


def botcmd_list_subscribe(data):
    attachments = []
    for task in list_subscriptions(data):
        plural = ukr_plural(task.found_total, 'декларацію', 'декларації', 'декларацій')
        att = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "Запит: {}".format(task.query),
                "subtitle": "Всього знайдено {} {}".format(task.found_total, plural),
                "text": "Щоб відписатись він наступних повідомлень по цьому запиту натисніть:",
                "buttons": [
                    {
                        "type": "imBack",
                        "title": "Відписатись він оновлень",
                        "value": "відписатись {}".format(task.query)
                    }
                ]
            }
        }

        attachments.append(att)

    s_count = len(attachments)
    message = "У вас всього {} {}".format(s_count, ukr_plural(s_count, "підписка", "підписки", "підписок"))

    return chat_response(data, message, attachments=attachments)


def botcmd_help(data):
    CRLFx2 = " \n\n"
    message = ("Вітаю, я бот для пошуку декларацій чиновників, я розумію наступні команди:" + CRLFx2 +
        CRLFx2 +
        "* будь-який-запит — знайти декларацію за запитом, показати результати в чаті," + CRLFx2 +
        "* “підписатись” — моніторити останній запит, отримувати оновлення в чат," + CRLFx2 +
        "* “підписки” — показати список підписок моніторингу, там же можна відписатись." + CRLFx2 +
        CRLFx2 +
        "Щоб дізнатись більше, завітайте на сайт https://declarations.com.ua" + CRLFx2 +
        "Дякую, що користуєтесь.")
    return chat_response(data, message)


QUICK_ANSWERS = (
    (re.compile('\?$'), "Вітаю, я бот для пошуку декларацій чиновників, почніть з команди 'довідка'.\n\nHello, I'm bot for search of declarations of Ukrainian officials."),
    (re.compile('(hi|hello)$'), "Hello, I'm bot for search of declarations of Ukrainian officials. I don't speak English, please ask me in Ukrainian."),
    (re.compile('(вітаю|привіт)$'), 'Вітаю, я бот для пошуку декларацій. Яку декларацію ти шукаєш сьогодні?'),
    (re.compile('привет$'), 'Привет, я бот для поиска деклараций украинских чиновников. Я понимаю запросы только на украинском языке.'),
    (re.compile('дякую$'), ['Будь ласка.', 'Нема за що!', 'Користуйтесь на здоров\'я', 'Дякую, що користуєтесь.']),
    (re.compile('спасибо$'), ['Пожалуйста', 'Не за что', 'Чому не державною?']),
    (re.compile('слава україні'), 'Героям слава!')
)

CHATBOT_COMMANDS = (
    (re.compile('(підписат|монітор|подписат|монитор|sub)'), botcmd_subscribe),
    (re.compile('(відпис|отпис|unsub)'), botcmd_unsubscribe),
    (re.compile('(мої|підписки|подписки|list)'), botcmd_list_subscribe),
    (re.compile('(допом|довідка|помощ|справка|help|info)'), botcmd_help),
)


def is_bot_command(text):
    for r, m in QUICK_ANSWERS + CHATBOT_COMMANDS:
        if r.match(text):
            return True


def send_greetings(data):
    # dont send greetings if chat already started
    message = chat_last_message(data, False, not_older_than=1)
    if message:
        return

    # send greetings to first not bot in membersAdded
    for member in data.get('membersAdded', []):
        if 'bot' in member.get('name', '').lower():
            continue
        data['from'] = {'id': data['conversation']['id']}
        message = ('Вітаю, яку декларацію ти шукаєш сьогодні?\n\n'+
                   'Якщо тут вперше, спробуй набрати "допомога".')
        chat_response(data, message)
        # send greetings only once
        break


def join_res(d, keys, sep=' '):
    """template like join dict values in signle string, safe for nonexists keys"""
    return sep.join([str(d[k]) for k in keys if k in d and d[k]])


def decl_list_to_chat_cards(decl_list, data, settings, deepsearch):
    attachments = []
    if decl_list:
        for found in decl_list:
            if 'date' in found.intro:
                found.intro.date = 'подана ' + str(found.intro.date)[:10]
            if 'corrected' in found.intro:
                if found.intro.corrected:
                    found.intro.corrected = 'Уточнена'
            url = settings.SITE_URL + reverse('details', args=[found.meta.id])
            att = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": join_res(found.general, ('last_name', 'name', 'patronymic'), ' '),
                    "subtitle": join_res(found.intro, ('declaration_year', 'doc_type', 'corrected', 'date'), ', '),
                    "text": join_res(found.general.post, ('region', 'office', 'post'), ', '),
                    "buttons": [
                        {
                            "type": "openUrl",
                            "title": "Відкрити",
                            "value": url
                        }
                    ]
                }
            }
            if 'url' in found.declaration:
                button = {
                    "type": "openUrl",
                    "title": "Показати оригінал",
                    "value": found.declaration.url
                }
                att['content']['buttons'].append(button)

            attachments.append(att)

            if len(attachments) >= 10:
                url = settings.SITE_URL + reverse_qs('search',
                    qs={'q': data['text'], 'deepsearch': deepsearch})
                att = {
                    "contentType": "application/vnd.microsoft.card.hero",
                    "content": {
                        "title": "Більше декларацій",
                        "text": "Щоб побачити більше перейдіть на сайт",
                        "buttons": [
                            {
                                "type": "openUrl",
                                "title": "Продовжити пошук на сайті",
                                "value": url
                            }
                        ]
                    }
                }
                attachments.append(att)
                break

        if not find_subscription2(data, data['text']):
            att = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": "Підписатись на запит {}".format(data['text']),
                    "text": "Отирмуйте оновлення по цьому запиту миттєво в чат",
                    "buttons": [
                        {
                            "type": "imBack",
                            "title": "Підписатись на запит",
                            "value": "підписатись {}".format(data['text'])
                        }
                    ]
                }
            }
        else:
            att = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": "Ви підписані на оновлення",
                    "text": "Щоб відписатись він наступних повідомлень по цьому запиту натисніть:",
                    "buttons": [
                        {
                            "type": "imBack",
                            "title": "Відписатись він оновлень",
                            "value": "відписатись {}".format(data['text'])
                        }
                    ]
                }
            }

        attachments.append(att)

    return attachments


def search_reply(data):
    if not data.get('text') or len(data['text']) > 100:
        return chat_response(data, 'Не зрозумів, уточніть запит.')

    text = data['text'].strip(' .,;:!-()\n').lower()

    for r, message in QUICK_ANSWERS:
        if r.match(text):
            if isinstance(message, (list, tuple, set)):
                message = choice(message)
            return chat_response(data, message)

    for r, handler in CHATBOT_COMMANDS:
        if r.match(text):
            return handler(data)

    search = simple_search(data['text'])
    deepsearch = ''

    if search.found_total == 0:
        search = simple_search(data['text'], deepsearch=True)
        deepsearch = 'on'

    plural = ukr_plural(search.found_total, 'декларацію', 'декларації', 'декларацій')
    message = 'Знайдено {} {}'.format(search.found_total, plural)
    if search.found_total > 10:
        message += '\n\nПоказані перші 10'
    attachments = None

    if search.found_total:
        attachments = decl_list_to_chat_cards(search, data, settings, deepsearch)

    return chat_response(data, message, attachments=attachments)


@csrf_exempt
def messages(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Method Not Allowed')

    if len(request.body) < 100 or len(request.body) > 1000:
        return HttpResponseBadRequest('Bad Request')

    data = json.loads(request.body.decode('utf-8'))

    if not verify_jwt(request.META.get('HTTP_AUTHORIZATION', ' '), data):
        return HttpResponseForbidden('Forbidden')

    if data['type'] == 'conversationUpdate':
        send_greetings(data)

    elif data['type'] == 'message':
        search_reply(data)

    return HttpResponse('OK')
