from django_jinja import library
from django import template
from spotter import utils

register = template.Library()


@library.filter
def uk_plural(value, args):
    args = args.split(',')
    return utils.ukr_plural(value, *args)


@register.filter(name='uk_plural')
def uk_plural_django(value, args):
    args = args.split(',')
    return utils.ukr_plural(value, *args)
