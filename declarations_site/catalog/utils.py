import re
import csv
import os.path
from string import capwords

from elasticsearch.exceptions import TransportError
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


def apply_term_filter(search, filters, key, field):
    value = filters.get(key, "")
    if value:
        filter_kw = {field: value}
        search = search.filter("term", **filter_kw)
    return search


def apply_search_filters(search, filters):
    search = apply_term_filter(search, filters, "declaration_year", "intro.declaration_year")
    search = apply_term_filter(search, filters, "doc_type", "intro.doc_type")
    return search


QS_OPS = re.compile(r'(["*?:~(]| AND | OR | NOT | -\w)')
QS_NOT = re.compile(r'[/]')  # do not allow regex queries


def base_search_query(base_search, query, deepsearch, filters):
    if not query:
        search = base_search.query('match_all')
        search = apply_search_filters(search, filters)
        return search

    default_field = "_all" if deepsearch else "ft_src"

    # try Lucene syntax query first
    if QS_OPS.search(query) and not QS_NOT.search(query):
        query_kw = {
            "analyze_wildcard": True,
            "allow_leading_wildcard": False,
            "default_field": default_field,
            "default_operator": "and",
            "query": query
        }

        search = base_search.query("query_string", **query_kw)
        search = apply_search_filters(search, filters)

        try:
            if search.count():
                return search
        except TransportError:
            # if Lucene query fail return to regular
            pass

        # before pass to match_query remove all unnecessary chars
        query = re.sub(r'["*?:~()[\]/]', '', query)

    query_op = {"query": query, "operator": "and"}
    query_kw = {default_field: query_op}

    search = base_search.query("match", **query_kw)
    search = apply_search_filters(search, filters)

    nwords = len(re.findall(r'\w{4,}', query))

    if nwords > 2 and not filters and not search.count():
        should_match = nwords - int(nwords > 4) - 1

        query_op["minimum_should_match"] = should_match
        query_op["operator"] = "or"

        search = base_search.query("match", **query_kw)

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
