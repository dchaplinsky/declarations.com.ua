from django_jinja import library
from django import template

register = template.Library()


@library.filter
def uk_plural(value, arg):
    args = arg.split(',')
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


@register.filter(name='uk_plural')
def uk_plural_django(value, arg):
    return uk_plural(value, arg)
