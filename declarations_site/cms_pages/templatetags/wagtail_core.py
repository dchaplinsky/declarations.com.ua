from django.utils.safestring import mark_safe
from django_jinja import library
from wagtail.wagtailcore.rich_text import expand_db_html


@library.filter
def richtext(value):
    if value is not None:
        html = expand_db_html(value)
    else:
        html = ''

    return mark_safe(html)
