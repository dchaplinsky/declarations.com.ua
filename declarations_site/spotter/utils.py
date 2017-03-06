import re
import logging
from datetime import timedelta
from unidecode import unidecode
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from django.template.loader import render_to_string
from elasticsearch_dsl import Search
from elasticsearch.exceptions import NotFoundError
from catalog.constants import CATALOG_INDICES
from catalog.elastic_models import Declaration, NACPDeclaration
from spotter.models import TaskReport, NotifySend
from spotter.sender import send_mail

NO_ASCII_REGEX = re.compile(r'[^\x00-\x7F]+')
NO_SPECIAL_REGEX = re.compile(r'[^\w.@+_-]+', re.UNICODE)
MAX_REPORT_LIMIT = 100000
ONE_SEARCH_LIMIT = 1000

logger = logging.getLogger(__name__)


def clean_username(value):
    """Transliterate and clean username by removing any unsupported character"""
    if NO_ASCII_REGEX.search(value):
        value = unidecode(value)
    value = NO_ASCII_REGEX.sub('', value)
    value = NO_SPECIAL_REGEX.sub('', value)
    return value


def do_search(task):
    if task.deepsearch:
        fields = ["_all"]
    else:
        fields = [
            "general.last_name",
            "general.name",
            "general.patronymic",
            "general.full_name",
            "general.post.post",
            "general.post.office",
            "general.post.region",
            "intro.declaration_year",
            "intro.doc_type",
            "declaration.source",
            "declaration.url",
        ]

    base_search = Search(index=CATALOG_INDICES)
    source = False

    search = base_search.query(
        "multi_match",
        query=task.query,
        type="cross_fields",
        operator="and",
        fields=fields
    ).source(source)

    if not search.count():
        search = base_search.query(
            "multi_match",
            query=task.query,
            type="cross_fields",
            operator="or",
            minimum_should_match="2",
            fields=fields
        ).source(source)

    return search


def merge_found(task, report, first_run=False):
    if task.found_ids:
        # remove possible '\r' from task_ids after edits in admin on Mac
        task.found_ids = task.found_ids.replace("\r", "").strip()
        report_ids = report.found_ids.split("\n")
        task_ids = set(task.found_ids.split("\n"))
        new_ids = list()

        for r in report_ids:
            if r not in task_ids:
                new_ids.append(r)

        if not new_ids:
            return False

        report.found_new = len(new_ids)
        task.found_total = len(task_ids) + len(new_ids)
        task.found_week += len(new_ids)
        report.new_ids = "\n".join(new_ids)
        task.found_ids += "\n" + report.new_ids
    else:
        task.found_ids = report.found_ids
        task.found_total = report.found_total
        report.found_new = report.found_total
        report.new_ids = report.found_ids

    if first_run:
        report.found_new = 0
        report.new_ids = ""

    return True


def get_found_week(task):
    week_ago = timezone.now() - timedelta(days=7)
    res = TaskReport.objects.filter(task=task,
        create_date__gt=week_ago).aggregate(Sum('found_new'))
    return res.get('found_new__sum', 0)


def create_report(task, search, first_run=False):
    report = TaskReport(task=task)
    found_total = search.count()
    found_ids = list()
    limit = ONE_SEARCH_LIMIT
    start = 0

    while start < found_total and start < MAX_REPORT_LIMIT:
        end = start + limit
        response = search[start:end].execute()
        found_ids.extend([hit.meta.id for hit in response])
        start = end

    if start >= MAX_REPORT_LIMIT:
        logger.error("Max found limit exceed for user %s query %s", task.user, task.query)

    if found_ids:
        report.found_total = len(found_ids)
        report.found_ids = "\n".join(found_ids)
        merge_found(task, report, first_run)

    report.save()

    task.found_week = get_found_week(task)
    task.last_run = timezone.now()
    task.save()

    return report


def first_run(task):
    search = do_search(task)
    report = create_report(task, search, first_run=True)
    return report


def load_declarations(new_ids, limit=100):
    decl_list = list()
    for declaration_id in new_ids.split("\n"):
        declaration_id = declaration_id.strip()
        if not declaration_id:
            continue

        try:
            declaration = NACPDeclaration.get(id=declaration_id)
        except NotFoundError:
            declaration = Declaration.get(id=declaration_id)

        decl_list.append(declaration)

        if len(decl_list) >= limit:
            logger.error("load_declarations limit exceed")
            break

    return decl_list


def send_newtask_notify(task):
    context = {
        'query': task.query,
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


def create_notify(task, report):
    notify = NotifySend(task=task, email=task.user.email, new_ids=report.new_ids)
    context = {
        'query': task.query,
        'decl_list': load_declarations(notify.new_ids),
        'found_new': report.found_new,
    }
    from_email = settings.FROM_EMAIL
    subject = render_to_string("email_found_subject.txt", context).strip()
    message = render_to_string("email_found_message.txt", context)
    msghtml = render_to_string("email_found_message.html", context)

    try:
        notify.status = send_mail(subject, message, from_email, [notify.email],
            html_message=msghtml)
    except Exception as e:
        logger.error("send_mail %s failed with error: %s", notify.email, e)
        notify.status = str(e)

    notify.save()
    return notify
