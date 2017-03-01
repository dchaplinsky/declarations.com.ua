import re
import sys
import json
from csv import DictReader
from parsel import Selector
import os.path
import glob2
from dateutil.parser import parse as dt_parse
from multiprocessing import Pool

from django.core.management.base import BaseCommand, CommandError

from elasticsearch.helpers import bulk
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from catalog.elastic_models import NACPDeclaration
from catalog.utils import replace_apostrophes, title


class BadJSONData(Exception):
    pass


class BadHTMLData(Exception):
    pass


class DeclarationStaticObj(object):
    declaration_types = {
        "1": "Щорічна",
        "2": "Перед звільненням",
        "3": "Після звільнення",
        "4": "Кандидата на посаду"
    }

    region_types = {
        "1.2.1": "Автономна Республіка Крим",
        "1.2.5": "Вінницька область",
        "1.2.7": "Волинська область",
        "1.2.12": "Дніпропетровська область",
        "1.2.14": "Донецька область",
        "1.2.18": "Житомирська область",
        "1.2.21": "Закарпатська область",
        "1.2.23": "Запорізька область",
        "1.2.26": "Івано-Франківська область",
        "1.2.80": "Київ",
        "1.2.32": "Київська область",
        "1.2.35": "Кіровоградська область",
        "1.2.46": "Львівська область",
        "1.2.44": "Луганська область",
        "1.2.48": "Миколаївська область",
        "1.2.51": "Одеська область",
        "1.2.53": "Полтавська область",
        "1.2.56": "Рівненська область",
        "1.2.85": "Севастополь",
        "1.2.59": "Сумська область",
        "1.2.61": "Тернопільська область",
        "1.2.63": "Харківська область",
        "1.2.65": "Херсонська область",
        "1.2.68": "Хмельницька область",
        "1.2.71": "Черкаська область",
        "1.2.73": "Чернівецька область",
        "1.2.74": "Чернігівська область"
    }

    region_mapping = {
        "автономна республіка крим": "Кримська Автономна Республіка",
        "м.сімферополь": "Кримська Автономна Республіка",
        "вінницька область": "Вінницька область",
        "м.вінниця": "Вінницька область",
        "волинська область": "Волинська область",
        "м.луцьк": "Волинська область",
        "дніпропетровська область": "Дніпропетровська область",
        "днепропетровская область": "Дніпропетровська область",
        "м.дніпро": "Дніпропетровська область",
        "кривий ріг": "Дніпропетровська область",
        "донецька область": "Донецька область",
        "донецкая область": "Донецька область",
        "м.донецьк": "Донецька область",
        "маріуполь": "Донецька область",
        "житомирская область": "Житомирська область",
        "житомирська область": "Житомирська область",
        "м.житомир": "Житомирська область",
        "закарпатська область": "Закарпатська область",
        "закарпатская область": "Закарпатська область",
        "ужгород": "Закарпатська область",
        "м.ужгород": "Закарпатська область",
        "запорізька область": "Запорізька область",
        "м.запоріжжя": "Запорізька область",
        "запорожская область": "Запорізька область",
        "івано-франківська область": "Івано-Франківська область",
        "м.івано-франківськ": "Івано-Франківська область",
        "київ": "м. Київ",
        "киев": "м. Київ",
        "м.київ": "м. Київ",
        "київська область": "Київська область",
        "кіровоградська область": "Кіровоградська область",
        "м.кропивницький": "Кіровоградська область",
        "кировоградская область": "Кіровоградська область",
        "львівська область": "Львівська область",
        "львовская область": "Львівська область",
        "м.львів": "Львівська область",
        "луганська область": "Луганська область",
        "луганская область": "Луганська область",
        "м.луганськ": "Луганська область",
        "миколаївська область": "Миколаївська область",
        "николаевская область": "Миколаївська область",
        "николаевская область": "Миколаївська область",
        "м.миколаїв": "Миколаївська область",
        "одеська область": "Одеська область",
        "одесса": "Одеська область",
        "м.одеса": "Одеська область",
        "одесская область": "Одеська область",
        "полтава": "Полтавська область",
        "полтавська область": "Полтавська область",
        "полтавська область": "Полтавська область",
        "полтавская область": "Полтавська область",
        "м.полтава": "Полтавська область",
        "рівненська область": "Рівненська область",
        "ровенская область": "Рівненська область",
        "м.рівне": "Рівненська область",
        "рівне": "Рівненська область",
        "севастополь": "Кримська Автономна Республіка",
        "сумська область": "Сумська область",
        "м.суми": "Сумська область",
        "м.тернопіль": "Тернопільська область",
        "тернопільська область": "Тернопільська область",
        "м.харків": "Харківська область",
        "харківська область": "Харківська область",
        "харьковская область": "Харківська область",
        "м.херсон": "Херсонська область",
        "херсонська область": "Херсонська область",
        "м.хмельницький": "Хмельницька область",
        "хмельницька область": "Хмельницька область",
        "хмельницкая область": "Хмельницька область",
        "м.черкаси": "Черкаська область",
        "черкаська область": "Черкаська область",
        "чернівецька область": "Чернівецька область",
        "чернівці": "Чернівецька область",
        "м.чернівці": "Чернівецька область",
        "чернігів": "Чернігівська область",
        "м.чернігів": "Чернігівська область",
        "чернігівська область": "Чернігівська область",
        "черниговская область": "Чернігівська область",
        "алчевськ": "Луганська область",
    }

    dangerous_chunks = [
        "onchange",
        "onclick",
        "onmouseover",
        "onmouseout",
        "onkeydown",
        "onload",
        "<img",
        "<scri"
    ]
    corrected = set()

    @staticmethod
    def parse_date(s):
        return dt_parse(s, dayfirst=True)

    @staticmethod
    def extract_textual_data(decl):
        res = decl.css(
            "*:not(td)>span.block::text, *:not(td)>span.border::text, td *::text").extract()

        res += decl.css(
            "fieldset:contains('Зареєстроване місце проживання') .person-info:contains('Місто')::text").extract()

        res = filter(None, map(lambda x: x.strip().strip("\xa0"), res))
        res = filter(lambda x: not x.endswith(":"), res)
        res = filter(lambda x: not x.startswith("["), res)
        res = filter(lambda x: not x.endswith("]"), res)

        # Very special case
        res = filter(lambda x: not x.startswith("Загальна площа (м"), res)

        return res

    @classmethod
    def _parse_me(cls, base_fname):
        json_fname = "{}.json".format(base_fname)
        html_fname = "{}.html".format(base_fname)
        resp = {
            "intro": {},
            "declaration": {}
        }

        with open(json_fname, "r") as fp:
            data = json.load(fp)

        with open(html_fname, "r") as fp:
            raw_html = fp.read()
            html = Selector(raw_html)

        id_ = data.get("id")
        created_date = data.get("created_date")

        raw_html_lowered = raw_html.lower()
        for chunk in cls.dangerous_chunks:
            if chunk in raw_html_lowered:
                raise BadHTMLData("Dangerous fragment found: {}, {}".format(
                    id_, base_fname))

        try:
            data = data["data"]
        except KeyError:
            raise BadJSONData("API brainfart: {}, {}".format(id_, base_fname))

        if "step_0" not in data:
            raise BadJSONData("Bad header format: {}, {}".format(id_, base_fname))

        resp["_id"] = "nacp_{}".format(id_)
        resp["nacp_src"] = "\n".join(cls.extract_textual_data(html))
        resp["nacp_orig"] = data
        resp["declaration"]["url"] = "https://public.nazk.gov.ua/declaration/{}".format(id_)
        resp["declaration"]["source"] = "NACP"
        resp["declaration"]["basename"] = os.path.basename(base_fname)

        resp["intro"]["corrected"] = id_ in cls.corrected
        resp["intro"]["date"] = cls.parse_date(created_date)

        if "declarationType" not in data["step_0"] or "changesYear" in data["step_0"]:
            resp["intro"]["doc_type"] = "Форма змін"

            if "changesYear" in data["step_0"]:
                resp["intro"]["declaration_year"] = int(data["step_0"]["changesYear"])
        else:
            resp["intro"]["doc_type"] = cls.declaration_types[data["step_0"]["declarationType"]]
            if "declarationYearTo" in data["step_0"]:
                resp["intro"]["declaration_year_to"] = cls.parse_date(data["step_0"]["declarationYearTo"])

            if "declarationYearFrom" in data["step_0"]:
                resp["intro"]["declaration_year_from"] = cls.parse_date(data["step_0"]["declarationYearFrom"])
                resp["intro"]["declaration_year"] = resp["intro"]["declaration_year_from"].year

            if "declarationYear1" in data["step_0"]:
                resp["intro"]["declaration_year"] = int(data["step_0"]["declarationYear1"])

            if "declarationYear3" in data["step_0"]:
                resp["intro"]["declaration_year"] = int(data["step_0"]["declarationYear3"])

            if "declarationYear4" in data["step_0"]:
                resp["intro"]["declaration_year"] = int(data["step_0"]["declarationYear4"])


        resp["general"] = {
            "last_name": replace_apostrophes(title(data["step_1"]["lastname"])),
            "name": replace_apostrophes(title(data["step_1"]["firstname"])),
            "patronymic": replace_apostrophes(title(data["step_1"]["middlename"])),
            "full_name": replace_apostrophes("{} {} {}".format(
                title(data["step_1"]["lastname"]),
                title(data["step_1"]["firstname"]),
                title(data["step_1"]["middlename"]),
            )),
            "post": {
                "post": replace_apostrophes(data["step_1"].get("workPost", "")),
                "office": replace_apostrophes(data["step_1"].get("workPlace", "")),
                "region": replace_apostrophes(cls.region_types.get(data["step_1"].get("actual_region", ""), "")),
            }
        }

        if "step_2" in data:
            family = data["step_2"]

            if isinstance(family, dict):
                resp["general"]["family"] = []

                for member in family.values():
                    if not isinstance(member, dict):
                        continue

                    resp["general"]["family"].append({
                        "family_name": replace_apostrophes("{} {} {}".format(
                            title(member.get("lastname", "")),
                            title(member.get("firstname", "")),
                            title(member.get("middlename", "")),
                        )),

                        "relations": member.get("subjectRelation", "")
                    })

        resp['general']['full_name_suggest'] = [
            {
                'input': resp['general']['full_name'],
                'weight': 5
            },
            {
                'input': ' '.join(
                    [
                        resp['general']['name'],
                        resp['general']['patronymic'],
                        resp['general']['last_name']
                    ]
                ),
                'weight': 3
            },
            {
                'input': ' '.join(
                    [
                        resp['general']['name'],
                        resp['general']['last_name']
                    ]
                ),
                'weight': 3
            }
        ]

        if not resp["general"]["post"]["region"]:
            region_html = html.css("fieldset:contains('Зареєстроване місце проживання') .person-info:contains('Місто')::text").extract()
            if len(region_html) > 1:
                chunks = region_html[1].split("/")
                if len(chunks) > 1:
                    resp["general"]["post"]["region"] = chunks[-2].strip()
                else:
                    pass

        if resp["general"]["post"]["region"].lower() in cls.region_mapping:
            resp["general"]["post"]["region"] = cls.region_mapping[resp["general"]["post"]["region"].lower()]
        else:
            resp["general"]["post"]["region"] = ""

        return NACPDeclaration(**resp).to_dict(True)

    @classmethod
    def parse(cls, fname):
        try:
            return cls._parse_me(fname.replace(".json", ""))
        except BadJSONData as e:
            print("{}: on file {}".format(e, fname))
            return None


class Command(BaseCommand):
    number_of_processes = 8
    chunk_size = 100
    help = ('Loads the JSONs of declarations downloaded from NACP '
            'into the persistence storage')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.es = connections.get_connection()

        s = NACPDeclaration.search().source([])
        self.existing_ids = [h.meta.id.replace("nacp_", "") for h in s.scan()]

    def add_arguments(self, parser):
        parser.add_argument('file_path')
        parser.add_argument('corrected_file')

        parser.add_argument(
            '--update_all_docs',
            action='store_true',
            dest='update_all_docs',
            default=False,
            help='Reload all docs into index',
        )

    def check_if_document_present(self, json_fname):
        m = re.search("([0-9\-a-z]{36})", os.path.basename(json_fname))

        if m:
            return m.group(1) not in self.existing_ids
        else:
            return False


    def handle(self, *args, **options):
        try:
            base_dir = options['file_path']
            corrected_file = options['corrected_file']
        except IndexError:
            raise CommandError(
                'First argument must be a path to source files and second is file name of CSV with corrected declarations')

        if hasattr(sys.stdin, 'isatty') and not sys.stdin.isatty():
            self.stdout.write(
                "To import something you need to run this command in TTY."
            )
            return

        self.stdout.write("Gathering JSON documents from {}".format(base_dir))
        self.jsons = list(glob2.glob(os.path.join(base_dir, "**/*.json")))
        self.stdout.write("Gathered {} JSON documents".format(len(self.jsons)))

        corrected = set()
        with open(corrected_file, "r") as fp:
            r = DictReader(fp)
            for l in r:
                corrected.add(l["uuid"])

        DeclarationStaticObj.corrected = corrected

        NACPDeclaration.init()
        counter = 0

        my_tiny_pool = Pool(self.number_of_processes)

        if not options["update_all_docs"]:
            self.jsons = list(
                filter(
                    lambda x: self.check_if_document_present(x), self.jsons))

        for ix in range(0, len(self.jsons), self.chunk_size):
            chunk = self.jsons[ix:ix + self.chunk_size]

            result = list(
                filter(None, my_tiny_pool.map(DeclarationStaticObj.parse, chunk)))
            counter += len(result)

            bulk(self.es, result)

            if ix:
                self.stdout.write(
                    'Loaded {} items to persistence storage'.format(ix))

        self.stdout.write(
            'Finished loading {} items to persistence storage'.format(counter))
