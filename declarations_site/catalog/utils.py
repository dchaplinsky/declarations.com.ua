import re
import csv
import os.path
from string import capwords

from translitua import translit, ALL_RUSSIAN, ALL_UKRAINIAN
from django.conf import settings


def is_cyr(name):
    return re.search("[а-яіїєґ]+", name.lower(), re.UNICODE) is not None


def is_ukr(name):
    return re.search("['іїєґ]+", name.lower(), re.UNICODE) is not None


def title(s):
    chunks = s.split()
    chunks = map(lambda x: capwords(x, u"-"), chunks)
    return u" ".join(chunks)


def replace_apostrophes(s):
    return s.replace("`", "'").replace("’", "'")


def base_search_query(base_search, query, deepsearch):
    if deepsearch:
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

    if query:
        search = base_search.query(
            "multi_match",
            query=query,
            type="cross_fields",
            operator="and",
            fields=fields
        )

        num_words = len(re.findall(r'\w{4,}', query))

        if num_words > 2 and not search.count():
            should_match = num_words - 2 if num_words > 4 else num_words - 1

            search = base_search.query(
                "multi_match",
                query=query,
                type="cross_fields",
                operator="or",
                minimum_should_match=should_match,
                fields=fields
            )
    else:
        search = base_search.query('match_all')

    return search


def parse_fullname(person_name):
    # Extra care for initials (especialy those without space)
    person_name = re.sub("\s+", " ",
                         person_name.replace(".", ". ").replace('\xa0', " "))

    chunks = person_name.strip().split(" ")

    last_name = ""
    first_name = ""
    patronymic = ""

    if len(chunks) == 2:
        last_name = title(chunks[0])
        first_name = title(chunks[1])
    elif len(chunks) > 2:
        last_name = title(" ".join(chunks[:-2]))
        first_name = title(chunks[-2])
        patronymic = title(chunks[-1])

    return last_name, first_name, patronymic


class Transliterator(object):
    def __init__(self, *args, **kwargs):
        self.ru_translations = {}

        with open(os.path.join(
                settings.BASE_DIR, "catalog/data/ua2ru.csv"), "r") as fp:
            r = csv.DictReader(fp)
            for l in r:
                self.ru_translations[l["term"].lower()] = list(
                    filter(None, [l["translation"], l["alt_translation"]]))

        return super(Transliterator, self).__init__(*args, **kwargs)

    def transliterate(self, person_last_name, person_first_name,
                      person_patronymic):
        first_names = []
        last_names = []
        patronymics = []

        original = ["{} {} {}".format(
            person_last_name, person_first_name, person_patronymic
        ).strip().replace("  ", " ")]

        result = set()

        if (person_first_name.lower() in self.ru_translations and
                is_cyr(person_first_name)):
            first_names = self.ru_translations[person_first_name.lower()]
        else:
            first_names = [person_first_name]

        if (person_last_name.lower() in self.ru_translations and
                is_cyr(person_last_name)):
            last_names = self.ru_translations[person_last_name.lower()]
        else:
            last_names = [person_last_name]

        if (person_patronymic.lower() in self.ru_translations and
                is_cyr(person_patronymic)):
            patronymics = self.ru_translations[person_patronymic.lower()]
        else:
            patronymics = [person_patronymic]

        translated = [
            "{} {} {}".format(l, f, p).strip().replace("  ", " ")
            for f in first_names
            for p in patronymics
            for l in last_names
        ]

        for n in original:
            if is_cyr(n):
                # TODO: also replace double ж, х, ц, ч, ш with single chars
                for ua_table in ALL_UKRAINIAN:
                    result.add(translit(n, ua_table))

        for n in translated:
            if not is_ukr(n):
                for ru_table in ALL_RUSSIAN:
                    result.add(translit(n, ru_table))

        return result | set(translated)


TRANSLITERATOR_SINGLETON = Transliterator()
