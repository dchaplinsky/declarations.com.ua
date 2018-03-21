import re
import csv
import os.path
import dpath.util
from string import capwords

from elasticsearch.exceptions import TransportError
from translitua import (
    translit, ALL_RUSSIAN, ALL_UKRAINIAN, UkrainianKMU, RussianInternationalPassport)

from catalog.constants import VALID_RELATIONS
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


def replace_arg(request, key, value, secval=None):
    """Replaces arg value in current QUERY_STRING
    if it already set can be used second value
    (useful for switching sort asc/desc params)"""
    args = request.GET.copy()
    if secval and key in args and args[key] == value:
        args[key] = secval
    else:
        args[key] = value
    return args.urlencode()


def sort_flag(request, key, asc_value, desc_value):
    if key in request.GET:
        if request.GET[key] == asc_value:
            return "\u25B2"  # BLACK UP-POINTING TRIANGLE (U+25BC)
        if request.GET[key] == desc_value:
            return "\u25BC"  # BLACK DOWN-POINTING TRIANGLE (U+25BC)
    return ""


def concat_fields(resp, fields):
    out = list()
    for f in fields:
        out.extend(dpath.util.values(resp, f, '.'))
    return " ".join(map(str, out))


def keyword_for_sorting(keyword, maxlen=40):
    if is_cyr(keyword):
        keyword = keyword.upper().replace('I', 'І')
    return keyword.upper().replace('Є', 'ЖЄ').replace('І', 'ЙІ').replace('Ї', 'ЙЇ')[:maxlen]


def apply_search_sorting(search, sort=""):
    sort_keys = {
        'name':
            ('general.full_name_for_sorting', ),
        'name_desc':
            ('-general.full_name_for_sorting', ),
        'year':
            ('intro.declaration_year', ),
        'year_desc':
            ('-intro.declaration_year', ),
        'date':
            ('intro.date', ),
        'date_desc':
            ('-intro.date', ),
    }
    if sort and sort in sort_keys:
        fields = sort_keys[sort]
        search = search.sort(*fields)
    return search


def apply_term_filter(search, filter_value, field):
    if filter_value:
        filter_kw = {field: filter_value}
        search = search.filter("term", **filter_kw)
    return search


def apply_match_filter(search, filter_list, field, operator='or'):
    if filter_list:
        value = " ".join(filter_list)
        filter_kw = {field: {'query': value, 'operator': operator}}
        search = search.filter("match", **filter_kw)
    return search


def apply_search_filters(search, filters):
    if not filters:
        return search
    region_type = filters.get("region_type", "region")
    region_value = filters.get("region_value", "")
    if region_type and region_value:
        filters[region_type] = region_value
    search = apply_term_filter(search, filters.get("declaration_year", ""), "intro.declaration_year")
    search = apply_term_filter(search, filters.get("doc_type", ""), "intro.doc_type")
    search = apply_term_filter(search, filters.get("region", ""), "general.post.region.raw")
    search = apply_term_filter(search, filters.get("actual_region"), "general.post.actual_region.raw")
    search = apply_term_filter(search, filters.get("estate_region"), "estate.region.raw")
    search = apply_match_filter(search, filters.getlist("post_type"), "general.post.post_type")
    return search


QS_OPS = re.compile(r'(["*?:~(]| AND | OR | NOT | -\w)')
QS_NOT = re.compile(r'[/]')  # do not allow regex queries


def base_search_query(base_search, query, deepsearch, filters=None):
    if not query:
        search = base_search.query('match_all')
        search = apply_search_filters(search, filters)
        return search

    default_field = "_all" if deepsearch else "index_card"

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

    if nwords > 3 and deepsearch and not search.count():
        should_match = nwords - int(nwords > 6) - 1

        query_op["minimum_should_match"] = should_match
        query_op["operator"] = "or"

        search = base_search.query("match", **query_kw)
        search = apply_search_filters(search, filters)

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


def blacklist(dct, fields):
    return {
        k: v for k, v in dct.items() if k not in fields
    }


def parse_family_member(s):
    try:
        position, person = s.split(None, 1)
        if "-" in position:
            position, person = s.split("-", 1)

        position = position.strip(u" -—,.:").capitalize()
        person = person.strip(u" -—,")

        if position not in VALID_RELATIONS:
            raise ValueError

        for pos in VALID_RELATIONS:
            if person.capitalize().startswith(pos):
                raise ValueError

        return {
            "relations": position,
            "family_name": person
        }
    except ValueError:
        return {"raw": s}


class Transliterator(object):
    special_cases = {
        "Юлія": ["Julia", "Yulia"],
        "Юлия": ["Julia", "Yulia"],
        "Дмитро": ["Dmitry", "Dimitry"],
        "Дмитрий": ["Dmitry", "Dimitry"],
        "Євген": ["Eugene"],
        "Петро": ["Peter"],
        "Ірина": ["Irene"],
    }

    special_replacements = {
        "ий$": ["y", "i"],
        "ий\s": ["y ", "i "],
        "кс": ["x"],
    }

    def get_name(self, name_tuple):
        return " ".join(name_tuple).strip().replace("  ", " ")

    def replace_item(self, name_tuple, chunk, repl):
        r = [repl if x.lower() == chunk.lower() else x for x in name_tuple]
        return r

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

        original = [
            (person_last_name, person_first_name, person_patronymic)
        ]

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
            (l, f, p)

            for f in first_names
            for p in patronymics
            for l in last_names
        ]

        for n in original:
            name = self.get_name(n)

            if is_cyr(name):
                for ua_table in ALL_UKRAINIAN:
                    result.add(translit(name, ua_table))

                for sc_rex, replacements in self.special_replacements.items():
                    if re.search(sc_rex, name, flags=re.I | re.U):
                        for repl in replacements:
                            optional_n = re.sub(sc_rex, repl, name, flags=re.I | re.U)
                            result.add(translit(title(optional_n), UkrainianKMU))

                for sc, replacements in self.special_cases.items():
                    if sc in n:
                        for repl in replacements:
                            optional_n = self.replace_item(n, sc, repl)
                            result.add(translit(self.get_name(optional_n), UkrainianKMU))

        for n in translated:
            name = self.get_name(n)

            if not is_ukr(name):
                for ru_table in ALL_RUSSIAN:
                    result.add(translit(name, ru_table))

                for sc_rex, replacements in self.special_replacements.items():
                    if re.search(sc_rex, name, flags=re.I | re.U):
                        for repl in replacements:
                            optional_n = re.sub(sc_rex, repl, name, flags=re.I | re.U)
                            result.add(translit(title(optional_n), RussianInternationalPassport))

                for sc, replacements in self.special_cases.items():
                    if sc in n:
                        for repl in replacements:
                            optional_n = self.replace_item(n, sc, repl)
                            result.add(translit(self.get_name(optional_n), RussianInternationalPassport))

        return result | set(map(self.get_name, translated))


TRANSLITERATOR_SINGLETON = Transliterator()
