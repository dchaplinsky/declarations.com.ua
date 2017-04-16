import re
import hmac
import logging
from time import time
from datetime import timedelta
from unidecode import unidecode
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.db.models import Sum
from django.template.loader import render_to_string
from elasticsearch_dsl import Search
from catalog.constants import CATALOG_INDICES
from catalog.elastic_models import Declaration, NACPDeclaration
from catalog.utils import base_search_query
from spotter.models import TaskReport, NotifySend
from spotter.sender import send_mail

NO_ASCII_REGEX = re.compile(r'[^\x00-\x7F]+')
NO_SPECIAL_REGEX = re.compile(r'[^\w.@+_-]+', re.UNICODE)
MAX_SEARCH_LIMIT = 100000
ONE_SEARCH_LIMIT = 1000
LOAD_DECLS_LIMIT = 100

logger = logging.getLogger(__name__)


def clean_username(value):
    """Transliterate and clean username by removing any unsupported character"""
    if NO_ASCII_REGEX.search(value):
        value = unidecode(value)
    value = NO_ASCII_REGEX.sub('', value)
    value = NO_SPECIAL_REGEX.sub('', value)
    return value


def reverse_qs(viewname, qs=None, **kwargs):
    url = reverse(viewname, **kwargs)
    if qs:
        url += '?' + urlencode(qs)
    return url


def do_search(task):
    base_search = Search(index=CATALOG_INDICES)
    source = False
    sort = "_doc"

    search = base_search_query(base_search, task.query, task.deepsearch)
    search = search.sort(sort).source(source)

    if not hasattr(search, 'found_total'):
        search.found_total = search.count()

    return search


def merge_found(task, report):
    if task.found_ids:
        # remove possible '\r' from task_ids after edits in admin on Mac
        report_ids = set(report.found_ids)
        task_ids = set(task.found_ids)
        new_ids = report_ids.difference(task_ids)

        if not new_ids:
            return False

        report.found_new = len(new_ids)
        task.found_total = len(task_ids) + len(new_ids)
        report.new_ids = list(new_ids)
        task.found_ids.extend(report.new_ids)
    else:
        task.found_ids = report.found_ids
        task.found_total = report.found_total
        report.found_new = report.found_total
        report.new_ids = report.found_ids

    # check for first run
    if not task.last_run:
        report.found_new = 0
        report.new_ids = []

    return True


def get_found_week(task):
    week_ago = timezone.now() - timedelta(days=7)
    res = TaskReport.objects.filter(task=task,
        created__gt=week_ago).aggregate(Sum('found_new'))
    return res.get('found_new__sum', 0)


def create_report(task, search):
    report = TaskReport(task=task)
    found_total = search.found_total
    found_ids = list()
    limit = ONE_SEARCH_LIMIT
    start = 0

    while start < found_total and start < MAX_SEARCH_LIMIT:
        end = start + limit
        response = search[start:end].execute()
        found_ids.extend([hit.meta.id for hit in response])
        start = end

    if start >= MAX_SEARCH_LIMIT:
        logger.error("Max found limit exceed for user %s query %s", task.user, task.query)

    if found_ids:
        report.found_total = len(found_ids)
        report.found_ids = found_ids
        merge_found(task, report)

    report.save()

    task.found_week = get_found_week(task)
    task.last_run = timezone.now()
    task.save()

    return report


def first_run(task):
    search = do_search(task)
    if search.found_total >= MAX_SEARCH_LIMIT:
        return None
    report = create_report(task, search)
    return report


def load_declarations(new_ids, limit=LOAD_DECLS_LIMIT):
    decl_list = list()
    fields = ['meta.id', 'general.*', 'intro.declaration_year']

    if len(new_ids) > limit:
        logger.error("load new_ids %d limit %d exceed", len(new_ids), limit)
        new_ids = new_ids[:limit]

    decl_list = NACPDeclaration.mget(
        new_ids,
        raise_on_error=False,
        missing='skip',
        _source=fields)

    if not decl_list:
        decl_list = []

    if len(decl_list) < len(new_ids):
        add_list = Declaration.mget(
            new_ids,
            raise_on_error=False,
            missing='skip',
            _source=fields)
        if add_list:
            decl_list.extend(add_list)

    if len(decl_list) < len(new_ids):
        logger.error("load new_ids %d docs not found", len(new_ids) - len(decl_list))

    return decl_list


def get_verification_hmac(user, email, time):
    key = settings.SECRET_KEY
    msg = '{user.id}{user.username}{email}{time}'.format(user=user, email=email, time=time)
    mac = hmac.new(key.encode('utf8'), msg.encode('utf8'))
    return mac.hexdigest()


def get_verified_email(request):
    args = {
        'user': request.user,
        'time': request.GET.get('time', 0),
        'email': request.GET.get('email', '')
    }
    mac = request.GET.get('mac', '')
    try:
        if time() - float(args['time']) > 86400:
            raise ValueError('too late')
        if mac != get_verification_hmac(**args):
            raise ValueError('bad mac')
    except (TypeError, ValueError):
        return None
    return args['email']


def send_confirm_email(request, email):
    args = {
        'email': email,
        'time': time(),
    }
    args['mac'] = get_verification_hmac(request.user, **args)
    context = {
        'email': email,
        'link': reverse_qs('confirm_email', args),
        'site_url': settings.EMAIL_SITE_URL,
    }
    from_email = settings.FROM_EMAIL
    subject = render_to_string("email_confirm_subject.txt", context).strip()
    message = render_to_string("email_confirm_message.txt", context)
    msghtml = render_to_string("email_confirm_message.html", context)
    try:
        res = send_mail(subject, message, from_email, [email],
            html_message=msghtml)
    except Exception as e:
        logger.error("send_mail %s failed with error: %s", email, e)
        res = False
    return bool(res)


def send_newtask_notify(task):
    context = {
        'query': task.query,
        'site_url': settings.EMAIL_SITE_URL,
    }
    from_email = settings.FROM_EMAIL
    subject = render_to_string("email_newtask_subject.txt", context).strip()
    message = render_to_string("email_newtask_message.txt", context)
    msghtml = render_to_string("email_newtask_message.html", context)
    try:
        res = send_mail(subject, message, from_email, [task.user.email],
            html_message=msghtml)
    except Exception as e:
        logger.error("send_mail %s failed with error: %s", task.user.email, e)
        res = False
    return bool(res)


def send_found_notify(notify):
    context = {
        'query': notify.task.query,
        'decl_list': load_declarations(notify.new_ids),
        'found_new': notify.found_new,
        'site_url': settings.EMAIL_SITE_URL,
    }
    from_email = settings.FROM_EMAIL
    subject = render_to_string("email_found_subject.txt", context).strip()
    message = render_to_string("email_found_message.txt", context)
    msghtml = render_to_string("email_found_message.html", context)
    try:
        notify.error = send_mail(subject, message, from_email, [notify.email],
            html_message=msghtml)
    except Exception as e:
        logger.error("send_mail %s failed with error: %s", notify.email, e)
        notify.error = str(e)
    return notify.error


def create_notify(task, report):
    notify = NotifySend(task=task, email=task.user.email, found_new=report.found_new,
        new_ids=list(report.new_ids))
    send_found_notify(notify)
    notify.save()
    return notify
