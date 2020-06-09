import jinja2
from django_jinja import library
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils import formats
from translitua import translit
from dateutil.parser import parse as dt_parse
from catalog.utils import parse_family_member


@library.global_function
def updated_querystring(request, params):
    """Updates current querystring with a given dict of params, removing
    existing occurrences of such params. Returns a urlencoded querystring."""
    original_params = request.GET.copy()
    for key in params:
        if key in original_params:
            original_params.pop(key)
    original_params.update(params)
    return original_params.urlencode()


@library.global_function
@jinja2.contextfunction
def context_or_settings(context, name):
    """If template context variable with `name` not set - get default
    value from django.settings"""
    if name in context:
        return context[name]
    return getattr(settings, "DEFAULT_" + name.upper())


ranges = [
    {"divider": 1e18, "suffix": "E"},
    {"divider": 1e15, "suffix": "P"},
    {"divider": 1e12, "suffix": "T"},
    {"divider": 1e9, "suffix": "G"},
    {"divider": 1e6, "suffix": "M"},
    {"divider": 1e3, "suffix": "k"},
]


@library.filter
def curformat(value, with_suffix=False):
    if value and value != "0":
        currency = ""
        if "$" in value:
            value = value.replace("$", "")
            currency = "USD "

        if "£" in value:
            value = value.replace("£", "")
            currency = "GBP "

        if "€" in value or "Є" in value:
            value = value.replace("€", "").replace("Є", "")
            currency = "EUR "

        try:
            num = float(value.replace(",", "."))
            formatted = "{}{:,.2f}".format(currency, num)

            if with_suffix:
                for order in ranges:
                    if num >= order["divider"]:
                        formatted = "{}{:,.2f}{}".format(
                            currency,
                            float(value.replace(",", ".")) / order["divider"],
                            order["suffix"],
                        )
                        break

            return formatted.replace(",", " ").replace(".", ",")
        except ValueError:
            return value
    else:
        return mark_safe('<i class="i-value-empty">—</i>')


@library.filter
def emptyformat(value):
    if value and value != "" and value != "0":
        return value
    else:
        return mark_safe('<i class="i-value-empty">—</i>')


@library.filter
def date(value):
    """Formats a date according to the given format."""
    if value in (None, ""):
        return ""

    if isinstance(value, str):
        value = dt_parse(value)

    arg = "DATE_FORMAT"
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        raise
        try:
            return format(value, arg)
        except AttributeError:
            return ""


@library.filter
def datetime(value):
    """Formats a date according to the given format."""
    if value in (None, ""):
        return ""

    if isinstance(value, str):
        value = dt_parse(value)

    if value.hour == 0 and value.minute == 0 and value.second == 0:
        arg = "DATE_FORMAT"
    else:
        arg = "DATETIME_FORMAT"
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        raise
        try:
            return format(value, arg)
        except AttributeError:
            return ""


@library.filter
def extract(value, key, default=0):
    return [v["aggregated_data"].get(key, default) for v in value]


@library.global_function
def parse_raw_family_string(family_raw):
    """Parses raw data in family field."""

    return map(parse_family_member, filter(None, family_raw.split(";")))


@library.filter
def translit_to_en(value):
    return translit(value)
