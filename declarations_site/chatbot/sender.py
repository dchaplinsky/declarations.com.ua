import json
from django.conf import settings


def send_to_chat(notify, context):
    from chatbot.views import chat_response, decl_list_to_chat_cards
    from chatbot.utils import ukr_plural

    plural = ukr_plural(context['found_new'], 'нову декларацію', 'нові декларації', 'нових декларацій')
    message = 'За запитом "{}" знайдено {} {}'.format(context['query'], context['found_new'], plural)
    if context['found_new'] > 10:
        message += '\n\nПоказані перші 10'

    data = json.loads(notify.task.chat_data)
    data['text'] = context['query']

    deepsearch = 'on' if notify.task.deepsearch else ''
    attachments = decl_list_to_chat_cards(context['decl_list'], data, settings, deepsearch)
    chat_response(data, message, attachments=attachments, auto_reply=True)
