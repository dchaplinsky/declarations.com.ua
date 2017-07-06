from django_jinja import library
from django import template
from spotter.utils import ukr_plural

register = template.Library()


@library.filter
def uk_plural(value, args):
    args = args.split(',')
    return ukr_plural(value, *args)


@register.filter(name='uk_plural')
def uk_plural_django(value, args):
    args = args.split(',')
    return uk_plural(value, *args)
