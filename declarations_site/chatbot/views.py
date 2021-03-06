import re
import json
from random import choice
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,
    HttpResponseNotAllowed)
from chatbot.utils import (chat_response, simple_search, verify_jwt, chat_last_message,
    create_subscription, find_subscription, list_subscriptions, load_notify, get_chat_login_link, TABLE_LINE)
from spotter.utils import load_declarations, reverse_qs, ukr_plural


def clean_botcmd_arg(data):
    text = data.get('text', '')[:150]

    if ' ' in text:
        _, text = text.split(' ', 1)
    else:
        text = chat_last_message(data, as_text=True)

    if text is None:
        return ''

    return text.strip()


def botcmd_subscribe(data):
    text = clean_botcmd_arg(data)

    if not text or is_bot_command(text):
        return chat_response(data, 'Спочатку зробіть запит')

    try:
        create_subscription(data, text)
    except ValueError as e:
        chat_response(data, 'Не вдалось створити підписку: {}'.format(e))
        return
    except Exception as e:
        chat_response(data, 'От халепа! Трапилась помилка при створені підписки: {}'.format(e))
        raise

    message = ""
    attachments = [
        {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "Створено підписку: {}".format(text),
                "subtitle": "Щоб переглянути всі підписки, оберіть:",
                "buttons": [
                    {
                        "type": "imBack",
                        "title": "Мої підписки",
                        "value": "підписки"
                    }
                ]
            }
        }
    ]
    chat_response(data, message, attachments=attachments)


def botcmd_unsubscribe(data):
    text = clean_botcmd_arg(data)

    if not text or is_bot_command(text):
        return chat_response(data, 'Спочатку зробіть запит')

    task = find_subscription(data, text)

    if not task:
        return chat_response(data, 'Завдання з таким запитом не знайдено')

    task.is_enabled = False
    task.is_deleted = True
    task.save()

    chat_response(data, 'Підписка відмінена, ви більше не будете отримувати повідомлень за цим запитом.')


def botcmd_list_subscribe(data):
    channel = data.get('channelId', '')
    attachments = []
    for task in list_subscriptions(data):
        plural = ukr_plural(task.found_total, 'декларацію', 'декларації', 'декларацій')
        # telegram fix
        if channel == 'telegram':
            query = task.id
        else:
            query = task.query or task.id
        att = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "За запитом: {}".format(task.query),
                "subtitle": "Знайдено {} {}".format(task.found_total, plural),
                "text": "Щоб відписатись він наступних повідомлень по цьому запиту, оберіть:",
                "buttons": [
                    {
                        "type": "imBack",
                        "title": "Відписатись",
                        "value": "відписатись {}".format(query)
                    }
                ]
            }
        }

        attachments.append(att)

    sbcount = len(attachments)
    splural = ukr_plural(sbcount, "підписка", "підписки", "підписок")
    message = "У вас {} {}".format(sbcount, splural)

    return chat_response(data, message, attachments=attachments)


def botcmd_list_newfound(data):
    cmd, args = data['text'].split(' ', 1)
    skip = 0

    if '/' in args:
        args, skip = args.split('/', 1)
        skip = int(skip)

    notify = load_notify(data, args)

    if notify and skip < notify.found_new:
        count = settings.CHATBOT_SERP_COUNT
        data['text'] = notify.task.query
        found_new = notify.found_new
        plural = ukr_plural(found_new, 'нову декларацію', 'нові декларації', 'нових декларацій')
        message = 'За підпискою: {}'.format(notify.task.query_title)
        message += '\n\nЗнайдено {} {}'.format(found_new, plural)
        message += '\n\nПоказані {} починаючи з {}'.format(count, skip + 1)
        message = TABLE_LINE + "\n\n{}\n\n".format(message) + TABLE_LINE
        new_decl = load_declarations(notify.new_ids[skip:])
        attachments = decl_list_to_chat_cards(new_decl, data, settings, notify.task.deepsearch,
            skip=skip, total=found_new, notify_id=notify.id)
        chat_response(data, message, attachments=attachments)
    else:
        message = 'Більше немає результатів.'
        chat_response(data, message)


def botcmd_next_searchpage(data):
    """load last query text and replace offset"""
    if re.search(r' /\d+$', data['text']):
        _, skip = data['text'].rsplit(' ', 1)
    else:
        skip = ''

    text = chat_last_message(data, as_text=True)

    if re.search(r' /\d+$', text):
        text, _ = text.rsplit(' ', 1)

    data['text'] = '{} {}'.format(text, skip)

    return search_reply(data)


def botcmd_login_url(data):
    login_link = settings.SITE_URL + get_chat_login_link(data)
    message = ""
    attachments = [
        {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "Перейти до кабінету на сайті",
                "text": "Посилання для входу на сайт діятиме протягом 15 хвилин",
                "buttons": [
                    {
                        "type": "openUrl",
                        "title": "Перейти на сайт",
                        "value": login_link
                    }
                ]
            }
        }
    ]
    return chat_response(data, message, attachments=attachments)


def botcmd_help(data):
    message = ("Вітаю, я бот для пошуку декларацій депутатів та чиновників.\n\n-\n\n" +
        "Мені можна відправити будь-який запит і я негайно знайду декларації. "+
        "Ще можна підписатись на оновлення і першим отримувати сповіщення про нові "+
        "декларації за вашим запитом. А ще я розумію команди: \n\n-\n\n" +
        "“підписатись” — моніторити останній запит, отримувати оновлення в чат,\n\n" +
        "“підписки” — показати список підписок моніторингу, там же можна відписатись.\n\n" +
        "“вхід” — перейти до власного кабінету на сайті декларацій.\n\n-\n\n" +
        "Щоб дізнатись більше, завітайте на наш сайт. Дякую, що користуєтесь.")

    attachments = [
        {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "buttons": [
                    {
                        "type": "imBack",
                        "title": "Мої підписки",
                        "value": "підписки"
                    },
                    {
                        "type": "openUrl",
                        "title": "Перейти на сайт",
                        "value": settings.SITE_URL
                    }
                ]
            }
        }
    ]
    return chat_response(data, message, attachments=attachments)


QUICK_ANSWERS = (
    (re.compile('\?$'), "Вітаю, я бот для пошуку декларацій депутатів та чиновників. Зробіть запит або почніть з команди 'довідка'. \n\n-\n\n"+
                        "Hello, I'm bot for search declarations of Ukrainian officials. Try search something or type 'help'."),
    (re.compile('(hi|hello)$'), "Hi, I'm bot for search declarations of Ukrainian officials. \n\n"+
                        "Sorry, I don't speak English, please ask me in Ukrainian."),
    (re.compile('(вітаю|привіт)$'), "Вітаю, я бот для пошуку декларацій. Зробіть будь-який запит або почніть з команди 'довідка'."),
    (re.compile('привет$'), 'Привет, я бот для поиска деклараций украинских чиновников. Я понимаю запросы только на украинском языке.'),
    (re.compile('дякую$'), ['Будь ласка.', 'Нема за що!', 'Користуйтесь на здоров\'я', 'Дякую, що користуєтесь.']),
    (re.compile('спасибо$'), ['Пожалуйста', 'Не за что', 'Чому не державною?']),
    (re.compile('слава україні'), 'Героям слава!')
)

CHATBOT_COMMANDS = (
    (re.compile('(підписат|монітор|подписат|монитор|/?sub)'), botcmd_subscribe),
    (re.compile('(відпис|отпис|/?unsub)'), botcmd_unsubscribe),
    (re.compile('(мої|підписки|подписки|/?list)'), botcmd_list_subscribe),
    (re.compile('(нові|новые|/?new) \d+'), botcmd_list_newfound),
    (re.compile('(наступні|следующие|/?next) \/\d+'), botcmd_next_searchpage),
    (re.compile('(вхід|вход|/?login)'), botcmd_login_url),
    (re.compile('(допомо|довідка|помощь|справка|/?help|/?info|/?start)'), botcmd_help),
)

NOT_FOUND_RESPONSES = (
    'Щоб дізнатись більше, напишіть "довідка"',
    'Спробуйте спростити запит.',
    'Ви точно шукаєте декларації, а не щось інше?',
    'Що сьогодні не знайшлось, знайдеться завтра.',
    'З часом навіть ваш сусід подасть декларацію.',
    'Пошук істини важливіше, ніж володіння нею.',
    'Простіше знайти знайому рибу в океані, ніж потрібну людину.',
    'Коли сам не знаєш, що шукаєш, пошук стає непростою справою.',
    'У пошуку хорошого життя завжди є небезпека опинитись в розшуку.',
    'Риба шукає, де глибше, але ти навряд чи риба.',
    'Той, хто шукає, обов\'язково знайде... але виключення теж бувають.',
    'What you seek is seeking you.',
    '...але пошук ведете у правильному напрямку.',
    'Якщо весь час шукати не залишиться часу щоб знаходити.',
    'Іноді ми самі не знаємо, що шукаємо, поки не знайдемо.',
    'Знайти розумних істот у космосі не легше ніж на землі.',
    'Я просто ще один маленький сервер, що щось шукає у темряві.',
    'Те, що легко знайти, не варто й шукати.',
    'Щоб знайти голку в копиці сіна, достатньо спалити його.',
    'Я наче геолог, який шукає-шукає, хоча нічого не загубив.',
    'В цих ваших інтернетах можна знайти все, чого не шукав.',
    'Цього разу я краще промовчу.',
)


def is_bot_command(text):
    for r, m in QUICK_ANSWERS + CHATBOT_COMMANDS:
        if r.match(text):
            return True


def send_greetings(data):
    # dont send greetings if chat already started
    message = chat_last_message(data, not_older_than=1)
    if message:
        return

    # send greetings to first not bot in membersAdded
    for member in data.get('membersAdded', []):
        if 'bot' in member.get('name', '').lower():
            continue
        data['from'] = {'id': data['conversation']['id']}
        message = ('Вітаю, яку декларацію ти шукаєш сьогодні? Щоб дізнатись більше напишіть "довідка".')
        chat_response(data, message)
        # send greetings only once
        break


def join_res(d, keys, sep=' '):
    """template like join dict values in signle string, safe for nonexists keys"""
    return sep.join([str(d[k]) for k in keys if k in d and d[k]])


def decl_list_to_chat_cards(decl_list, data, settings, deepsearch=False, skip=0, total=0, notify_id=None):
    attachments = []
    channel = data.get('channelId', '')
    count = settings.CHATBOT_SERP_COUNT

    if not total and hasattr(decl_list, 'found_total'):
        total = decl_list.found_total

    if decl_list:
        for found in decl_list:
            if 'date' in found.intro:
                found.intro.date = 'подана ' + str(found.intro.date)[:10]
            if 'corrected' in found.intro:
                if found.intro.corrected:
                    found.intro.corrected = 'Уточнена'
            url = settings.SITE_URL + reverse('details', args=[found.meta.id])
            if channel == 'telegram':
                # telegram bug: didn't accept button with command longer than ~ 30 chars
                name = join_res(found.general, ('last_name', 'name'), ' ')
                command_text = "підписатись {}".format(name)
            else:
                name = join_res(found.general, ('last_name', 'name', 'patronymic'), ' ')
                command_text = "підписатись {}".format(name)
            att = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": join_res(found.general, ('last_name', 'name', 'patronymic'), ' '),
                    "subtitle": join_res(found.intro, ('declaration_year', 'doc_type', 'corrected', 'date'), ', '),
                    "text": join_res(found.general.post, ('region', 'office', 'post'), ', '),
                    "buttons": [
                        {
                            "type": "imBack",
                            "title": "Підписатись за ПІБ",
                            "value": command_text,
                        },
                        {
                            "type": "openUrl",
                            "title": "Відкрити декларацію",
                            "value": url
                        }
                    ]
                }
            }

            attachments.append(att)

            if len(attachments) >= count:
                break

        if len(attachments) >= count and total - skip > count:
            deepsearch = 'on' if deepsearch else ''
            search_url = settings.SITE_URL + reverse_qs('search',
                qs={'q': data['text'], 'deepsearch': deepsearch})
            if len(search_url) > 250:
                search_url = settings.SITE_URL + reverse_qs('search')
            if notify_id:
                next_page = "нові {}/{}".format(notify_id, skip + count)
            else:
                next_page = "{} /{}".format(data['text'], skip + count)
            # telegram button length fix
            if channel == 'telegram' and len(data['text']) > 25:
                next_page = "наступні /{}".format(skip + count)
            att = {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": "Більше декларацій",
                    "buttons": [
                        {
                            "type": "imBack",
                            "title": "Наступні {} декларацій".format(count),
                            "value": next_page,
                        },
                        {
                            "type": "openUrl",
                            "title": "Перейти на сайт",
                            "value": search_url
                        }
                    ]
                }
            }

            attachments.append(att)

        # end for
    # end if

    task = find_subscription(data, data['text'])

    if not task:
        # telegram fix
        if channel == 'telegram':
            command_text = "підписатись"
        else:
            command_text = "підписатись {}".format(data['text'])
        att = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "Підписатись на оновлення",
                "text": "Отримуйте нові декларації по запиту: {}".format(data['text']),
                "buttons": [
                    {
                        "type": "imBack",
                        "title": "Підписатись",
                        "value": command_text,
                    }
                ]
            }
        }
        if total == 0:
            att["content"]["title"] = "Отримати коли з'явиться"
            att["content"]["buttons"].append({
                "type": "imBack",
                "title": "Допомога",
                "value": "допомога",
            })
    else:
        # telegram fix
        if channel == 'telegram':
            command_text = "відписатись {}".format(task.id)
        else:
            command_text = "відписатись {}".format(data['text'])
        att = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "Ви підписані на оновлення",
                "text": "Щоб відписатись він оновлень по цьому запиту, оберіть:",
                "buttons": [
                    {
                        "type": "imBack",
                        "title": "Відписатись",
                        "value": command_text,
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

    # deepsearch switch
    deepsearch = False
    if ' /' in text:
        for deep in (' /deep', ' /всюди'):
            if deep in data['text']:
                deepsearch = True
                data['text'] = data['text'].replace(deep, '')

    # pagination in format query /skip
    skip = 0
    count = settings.CHATBOT_SERP_COUNT
    if re.search(r' /\d+$', text):
        text, skip = data['text'].rsplit(' ', 1)
        data['text'] = text
        skip = int(skip[1:])

    search = simple_search(data['text'], deepsearch=deepsearch)

    # it found nothing try again with deepsearch
    if search.found_total == 0 and not deepsearch:
        deepsearch = True
        search = simple_search(data['text'], deepsearch=deepsearch)

    found_total = search.found_total
    plural = ukr_plural(found_total, 'декларацію', 'декларації', 'декларацій')
    message = 'Знайдено {} {}'.format(found_total, plural)

    if found_total == 0:
        message = 'За запитом "{}" декларацій не знайдено.'.format(data['text'])
        message += '\n\n-\n\n'
        message += choice(NOT_FOUND_RESPONSES)

    elif found_total > skip + count:
        if skip:
            message += '\n\nПоказано {} починаючи з {}'.format(count, skip + 1)
        else:
            message += '\n\nПоказано перші {}'.format(count)

    if found_total > 0:
        message = TABLE_LINE + "\n\n{}\n\n".format(message) + TABLE_LINE

    if found_total > 0 and skip > 0:
        search = search[skip:]

    attachments = decl_list_to_chat_cards(search, data, settings, deepsearch,
        skip=skip, total=found_total)

    return chat_response(data, message, attachments=attachments)


@csrf_exempt
def deauthorize(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Method Not Allowed')

    return HttpResponse('OK')


@csrf_exempt
def messages(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], 'Method Not Allowed')

    if len(request.body) < 100 or len(request.body) > 5000:
        return HttpResponseBadRequest('Bad Request')

    data = json.loads(request.body.decode('utf-8'))

    if not verify_jwt(request.META.get('HTTP_AUTHORIZATION', ' '), data):
        return HttpResponseForbidden('Forbidden')

    if data['type'] == 'conversationUpdate':
        send_greetings(data)

    elif data['type'] == 'message':
        search_reply(data)

    return HttpResponse('OK')
