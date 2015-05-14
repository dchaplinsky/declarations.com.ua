from django_jinja import library
from django.utils.safestring import mark_safe


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


@library.filter
def curformat(value):
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
            return '{}{:,.2f}'.format(
                currency,
                float(value.replace(',', '.'))).replace(
                    ',', ' ').replace('.', ',')
        except ValueError:
            return value
    else:
        return mark_safe('<i class="i-value-empty">—</i>')

@library.filter
def emptyformat(value):
    if value and value != "" and value !="0":
        return value
    else:
        return mark_safe('<i class="i-value-empty">—</i>')


VALID_POSITIONS = [
    "Син",
    "Дружина",
    "Чоловік",
    "Донька",
    "Дочка",
    "Мати",
    "Батько",
    "Жінка",
    "Брат",
    "Сестра",
    "Теща",
    "Онук",
    "Мама",
    "Невістка",
    "Племінник",
    "Баба",
    "Пасинок",
    "Дитина",
    "Матір",
    "Онука",
    "Зять",
    "Діти",
    "Свекор",
    "Бабуся",
    "Племінниця",
    "Донечка",
    "Тесть",
    "Внучка",
    "Сын",
    "Чоловик",
    "Співмешканець",
    "Супруга",
    "Допька",
    "Дружіна",
    "Падчерка",
    "Внук",
    "Свекруха",
    "Мать",
    "Доч",
    "Батьки",
    "Тітка",
    "Співмешканака",
    "Онучка",
    "Тато",
    "Жена",
]


def parse_family_member(s):
    try:
        position, person = s.split(None, 1)
        if "-" in position:
            position, person = s.split("-", 1)

        position = position.strip(u" -—,.:").capitalize()
        person = person.strip(u" -—,")

        if position not in VALID_POSITIONS:
            raise ValueError

        for pos in VALID_POSITIONS:
            if person.capitalize().startswith(pos):
                print("%s %s" % (person, pos))
                raise ValueError

        return {
            "relations": position,
            "family_name": person
        }
    except ValueError:
        return {"raw": s}


@library.global_function
def parse_raw_family_string(family_raw):
    """Parses raw data in family field."""

    return map(parse_family_member, filter(None, family_raw.split(";")))
