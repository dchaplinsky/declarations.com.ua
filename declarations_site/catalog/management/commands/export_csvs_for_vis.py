import json
import re
from csv import DictWriter
from collections import defaultdict
from datetime import datetime

from django.core.management.base import BaseCommand

from elasticsearch_dsl.query import Q

from catalog.elastic_models import NACPDeclaration
from catalog.utils import title

AGGREGATED_FIELD_NAME = 'aggregated'

ORDER_BY = ['estate.total_land', 'assets.total', 'incomes.total', 'estate.total_other']


CATEGORY_MAP = {
    "Поліція": 'a',
    'Місцеві адміністрації та ради': 'b',
    'Фонд державного майна': 'c',
    'Кабмін, міністерства та підлеглі органи': 'd',
    "Інспектори": 'e',
    'Інші державні служби, комісії, і т.п.': 'f',
    'Без категорії': 'g',
    'Прокуратура': 'h',
    'Парламент': 'j',
    "Слідчі": 'k',
    'Пенсійний фонд': 'l',
    "Тюрми": 'm',
    "Лікарі": 'n',
    'Суд': 'p',
    'НБУ': 'q',
    'Адміністрація / Секретаріат Президента': 'r',
    'Державний комітет телебачення і радіомовлення': 's',
    'Мер': 't',
    'НАБУ': 'u',
    'Ректор': 'v',
    'Антимонопольний комітет': 'w',
    'Рахункова палата': 'x',
    'ЦВК': 'y',
    'Вища рада юстиції': 'z',
    'СБУ': 'o',
    'НАЗК': 'z2'
}

GROUPS_TO_EXPORT = [
    "p",  # 'Suddi'
    "h",  # 'Prokurory'
    "b",  # 'miscevaVlada'
    "j",  # 'centralnaVlada'
    "n",  # 'likari'
    "e",  # 'inspectory'
]

POSITION_MAP = {
    "Ректор": [re.compile("\sректор"), " ректора"],
    "Лікарі": ['лікар'],
    "Тюрми": ['колоні', 'тюрм', "тюрьм", "колони"],
    'Прокуратура': ["прокурор", "прокурат", "пркур", "прокрор", "прокруор"],
    "Поліція": ["поліц"],
    "Слідчі": ["следователь", "слідчий", "детектив", "слідчого", "поліці", "оперуповноважений"],
    'Парламент': [
        "апарат верховної ради україни", "верховна рада україни", "верховна рада", "народний депутат",
        "народный депутат"
    ],
    "Мер": ["міський голова"],
    "Суд": [
        "судя", "суду", "судя", "судья", "голова суду",
        re.compile("суд$"), re.compile("суд,\s"), re.compile("суд\s"),
        re.compile("голова\s.*суду"), re.compile("голова\s.*суда")
    ],
    'Кабмін, міністерства та підлеглі органи': ["міністерств", re.compile("міністр(?!(ац|ат))"), ],
    "Інспектори": ["інспектор", "інспекц"],
    "Місцеві адміністрації та ради": [
        'сільськ', "селищ", 'районної ради', "сільський голова", "обласний голова", "районний голова"
    ],
}

REGIONS_MAP = {
    'Харківська область': 1,
    'Львівська область': 2,
    'Чернівецька область': 3,
    'Донецька область': 4,
    '!не визначено': 5,
    'м. Київ': 6,
    'Миколаївська область': 7,
    'Дніпропетровська область': 8,
    'Житомирська область': 9,
    'Рівненська область': 10,
    'Одеська область': 11,
    'Київська область': 12,
    'Закарпатська область': 13,
    'Запорізька область': 14,
    'Черкаська область': 15,
    'Чернігівська область': 16,
    'Сумська область': 17,
    'Волинська область': 18,
    'Івано-Франківська область': 19,
    'Херсонська область': 20,
    'Хмельницька область': 21,
    'Тернопільська область': 22,
    'Полтавська область': 23,
    'Кіровоградська область': 24,
    'Луганська область': 25,
    'Вінницька область': 26,
    'Кримська Автономна Республіка': 27
}


class Command(BaseCommand):
    help = 'Export aggregated values from NACP declarations '
    'into CSV format for visualisation made by Andriy Ulin '

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'destination',
            help='Data dir',
        )

        parser.add_argument(
            '--year', nargs='*', type=int,
            choices=range(2015, datetime.now().year + 1),
            default=range(2015, datetime.now().year + 1),
        )

    def get_raw_data(self, year, order_by, limit=10000):
        to_export = NACPDeclaration.search().source(
            include=[AGGREGATED_FIELD_NAME]).query("exists", field=AGGREGATED_FIELD_NAME)

        to_export = to_export.query(
            "bool",
            must=[
                Q("term", intro__doc_type="Щорічна"),
                Q("term", intro__declaration_year=year)
            ],
            must_not=[
                Q("exists", field="corrected_declarations"),
                Q("term", **{"{}__outlier".format(AGGREGATED_FIELD_NAME): True})
            ]
        ).sort(
            {'aggregated.{}'.format(order_by): {"order": "desc"}}
        )[:limit]

        # print(json.dumps(to_export.to_dict(), indent=4, ensure_ascii=False))
        res = []

        for d in to_export.execute():
            row = d[AGGREGATED_FIELD_NAME].to_dict()
            row["id"] = d._id
            res.append(row)

        return res

    def define_profession_group(self, group):
        group = group.lower()

        for k, v in POSITION_MAP.items():
            for chunk in v:
                if isinstance(chunk, str) and chunk.lower() in group:
                    return k
                else:
                    if re.search(chunk, group):
                        return k

    def categorize(self, data):
        name_post = data["name_post"].replace(data["name"], "").strip(", ")
        organization_group = data.get("organization_group", "")

        if not organization_group or organization_group in [
                'Без категорії',
                '!не визначено',
                'Кабмін, міністерства та підлеглі органи',
                'Інші державні служби, комісії, і т.п.',
                'Місцеві адміністрації та ради']:

            organization_group = self.define_profession_group(name_post) or organization_group
            organization_group = CATEGORY_MAP[organization_group]

        return {
            "incomes": round(float(data['incomes.total'])),
            "land": round(float(data['estate.total_land'])),
            "apartments": round(float(data['estate.total_other'])),
            "assets": round(float(data['assets.total'])),
            "cash": round(float(data['assets.cash.total'])),
            "vehicles_names": "/".join(data['vehicles.all_names'].split(';')),
            "organization_group": organization_group,
            "name": title(data["name"]),
            "region": REGIONS_MAP[data["region"]],
            "name_post": name_post,
            "id": data["id"],
        }

    def trim(self, data, data_in_each_group=100, data_in_all_groups=300):
        res = []
        counts = defaultdict(int)

        for d in data:
            res.append(d)

            if d["organization_group"] in GROUPS_TO_EXPORT:
                counts[d["organization_group"]] += 1

            if (counts and min(counts.values()) >= data_in_each_group and
                    len(res) >= data_in_all_groups):
                break

        print(counts)
        return res

    def handle(self, *args, **options):
        for year in options["year"]:
            for order in ORDER_BY:
                data = self.get_raw_data(year, order, 30000)
                categorized = [self.categorize(d) for d in data]
                trimmed = self.trim(categorized)
                print(len(trimmed))

                import json
                print(json.dumps(categorized[0], ensure_ascii=False, indent=4))
