import re
import json
from csv import DictReader
from parsel import Selector
import os.path
import glob2
from dateutil.parser import parse as dt_parse
from multiprocessing import Pool

from django.core.management.base import BaseCommand, CommandError

from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from catalog.elastic_models import NACPDeclaration
from catalog.utils import replace_apostrophes, title


class BadJSONData(Exception):
    pass


class BadHTMLData(Exception):
    pass


def parse_guid_from_fname(json_fname):
    m = re.search("([0-9\-a-z]{36})", os.path.basename(json_fname))

    if m:
        return m.group(1), json_fname
    else:
        return False


class DeclarationStaticObj(object):
    declaration_types = {
        "1": "Щорічна",
        "2": "Перед звільненням",
        "3": "Після звільнення",
        "4": "Кандидата на посаду"
    }

    region_types = {
        "1.2.1": "Кримська Автономна Республіка",
        "1.2.5": "Вінницька область",
        "1.2.7": "Волинська область",
        "1.2.12": "Дніпропетровська область",
        "1.2.14": "Донецька область",
        "1.2.18": "Житомирська область",
        "1.2.21": "Закарпатська область",
        "1.2.23": "Запорізька область",
        "1.2.26": "Івано-Франківська область",
        "1.2.80": "м. Київ",
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

    region_regexps = [
        (r'автономн(?:а|ая|ої|ой) республ[и|і]к[а|и] кр[и|ы]м', 'Кримська Автономна Республіка'),
        (r'^севастополь / укра[ї|и]на$', 'Кримська Автономна Республіка'),
        (r'^севастополь$', 'Кримська Автономна Республіка'),
        (r'^с[и|і]мферополь / укра[ї|и]на$', 'Кримська Автономна Республіка'),
        (r'^с[и|і]мферополь$', 'Кримська Автономна Республіка'),
        (r'^в[і|и]нниць?к(?:а|ая|ої|ой) обл', 'Вінницька область'),
        (r'^в[і|и]нниц[а|я] / укра[ї|и]на$', 'Вінницька область'),
        (r'^в[і|и]нниц[а|я]$', 'Вінницька область'),
        (r'вол[и|ы]нсь?к(?:а|ої|ая|ой) обл', 'Волинська область'),
        (r'^луць?к / укра[ї|и]на$', 'Волинська область'),
        (r'^луць?к$', 'Волинська область'),
        (r'дн[і|е]про(?:петро)?всь?к(?:а|ої|ая|ой) обл', 'Дніпропетровська область'),
        (r'^дн[і|е]про(?:петро)?всь?к / укра[и|ї]на$', 'Дніпропетровська область'),
        (r'^дн[і|е]про(?:петро)?всь?к$', 'Дніпропетровська область'),
        (r'^дн[і|е]про?$', 'Дніпропетровська область'),
        (r'донець?к(?:а|ої|ая|ой) обл', 'Донецька область'),
        (r'^донець?к / укра[и|ї]на$', 'Донецька область'),
        (r'^донець?к$', 'Донецька область'),
        (r'житомирсь?к(?:а|ої|ая|ой) обл', 'Житомирська область'),
        (r'^житомир / укра[и|ї]на$', 'Житомирська область'),
        (r'^житомир$', 'Житомирська область'),
        (r'закарпатсь?к(?:а|ої|ая|ой) обл', 'Закарпатська область'),
        (r'^ужгород / укра[и|ї]на$', 'Закарпатська область'),
        (r'^ужгород$', 'Закарпатська область'),
        (r'запор(?:ізьк|ожск)(?:а|ої|ая|ой) обл', 'Запорізька область'),
        (r'^(?:запоріжжя|запорожье) / укра[и|ї]на$', 'Запорізька область'),
        (r'^запоріжжя|запорожье$', 'Запорізька область'),
        (r'франк[і|о]всь?к(?:а|ої|ая|ой) обл', 'Івано-Франківська область'),
        (r'^[і|и]вано-франк[і|о]всь?к / укра[и|ї]на$', 'Івано-Франківська область'),
        (r'^[і|и]вано-франк[і|о]всь?к$', 'Івано-Франківська область'),
        (r'ки[ї|е]всь?к(?:а|ої|ая|ой) обл', 'Київська область'),
        (r'^ки[ї|е]всь?ка область/ки[ї|е]в / укра[и|ї]на$', 'м. Київ'),
        (r'^ки[ї|е]в / укра[и|ї]на$', 'м. Київ'),
        (r'^ки[ї|е]в$', 'м. Київ'),
        (r'к[і|и]ровоградсь?к(?:а|ої|ая|ой) обл', 'Кіровоградська область'),
        (r'кропивниць?к(?:а|ої|ая|ой) обл', 'Кіровоградська область'),
        (r'^к[і|и]ровоград / укра[и|ї]на$', 'Кіровоградська область'),
        (r'^к[і|и]ровоград$', 'Кіровоградська область'),
        (r'^кропивниць?кий / укра[и|ї]на$', 'Кіровоградська область'),
        (r'лугансь?к(?:а|ої|ая|ой) обл', 'Луганська область'),
        (r'^лугансь?к / укра[и|ї]на$', 'Луганська область'),
        (r'^лугансь?к$', 'Луганська область'),
        (r'льв[і|о]всь?к(?:а|ої|ая|ой) обл', 'Львівська область'),
        (r'^льв[і|о]в / укра[и|ї]на$', 'Львівська область'),
        (r'^льв[і|о]в$', 'Львівська область'),
        (r'[м|н]икола[ї|е]всь?к(?:а|ої|ая|ой) обл', 'Миколаївська область'),
        (r'^[м|н]икола[ї|е]в / укра[и|ї]на$', 'Миколаївська область'),
        (r'^[м|н]икола[ї|е]в$', 'Миколаївська область'),
        (r'одес[с|ь]к(?:а|ої|ая|ой) обл', 'Одеська область'),
        (r'^одесс?а / укра[и|ї]на$', 'Одеська область'),
        (r'^одесс?а$', 'Одеська область'),
        (r'полтавсь?к(?:а|ої|ая|ой) обл', 'Полтавська область'),
        (r'^полтава / укра[и|ї]на$', 'Полтавська область'),
        (r'^полтава$', 'Полтавська область'),
        (r'р[і|о]вненсь?к(?:а|ої|ая|ой) обл', 'Рівненська область'),
        (r'^р[і|о]вн[е|о] / укра[и|ї]на$', 'Рівненська область'),
        (r'^р[і|о]вн[е|о]$', 'Рівненська область'),
        (r'сумсь?к(?:а|ої|ая|ой) обл', 'Сумська область'),
        (r'^сум[и|ы] / укра[и|ї]на$', 'Сумська область'),
        (r'^сум[и|ы]$', 'Сумська область'),
        (r'терноп[і|о]льсь?к(?:а|ої|ая|ой) обл', 'Тернопільська область'),
        (r'^терноп[і|о]ль / укра[и|ї]на$', 'Тернопільська область'),
        (r'^терноп[і|о]ль$', 'Тернопільська область'),
        (r'харь?к[і|о]всь?к(?:а|ої|ая|ой) обл', 'Харківська область'),
        (r'^харь?к[і|о]в / укра[и|ї]на$', 'Харківська область'),
        (r'^харь?к[і|о]в$', 'Харківська область'),
        (r'херсонсь?к(?:а|ої|ая|ой) обл', 'Херсонська область'),
        (r'^херсон / укра[и|ї]на$', 'Херсонська область'),
        (r'^херсон$', 'Херсонська область'),
        (r'хмельниць?к(?:а|ої|ая|ой) обл', 'Хмельницька область'),
        (r'^хмельниць?кий / укра[и|ї]на$', 'Хмельницька область'),
        (r'^хмельниць?кий$', 'Хмельницька область'),
        (r'черкас[ь|с]к(?:а|ої|ая|ой) обл', 'Черкаська область'),
        (r'^черкас(?:и|сы) / укра[и|ї]на$', 'Черкаська область'),
        (r'^черкас(?:и|сы)$', 'Черкаська область'),
        (r'черн[і|о]в[е|и]ць?к(?:а|ої|ая|ой) обл', 'Чернівецька область'),
        (r'^черн[і|о]вц[і|ы] / укра[и|ї]на$', 'Чернівецька область'),
        (r'^черн[і|о]вц[і|ы]$', 'Чернівецька область'),
        (r'черн[і|и]г[і|о]всь?к(?:а|ої|ая|ой) обл', 'Чернігівська область'),
        (r'^черн[і|и]г[і|о]в / укра[и|ї]на$', 'Чернігівська область'),
        (r'^черн[і|и]г[і|о]в$', 'Чернігівська область')
    ]

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

        try:
            with open(json_fname, "r") as fp:
                data = json.load(fp)

            with open(html_fname, "r") as fp:
                raw_html = fp.read()
                html = Selector(raw_html)
        except ValueError:
            print(
                "File {} or it's HTML counterpart cannot be parsed".format(json_fname))
            return None
        except FileNotFoundError:
            print(
                "File {} or it's HTML counterpart cannot be found".format(json_fname))
            return None

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
            region_html = html.css(
                "fieldset:contains('Зареєстроване місце проживання') .person-info:contains('Місто')::text"
            ).extract()
            if len(region_html) > 1:
                for pattern, region in cls.region_regexps:
                    if re.search(pattern, region_html[1].strip().lower().replace('м.', '')):
                        resp["general"]["post"]["region"] = region
                        break

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
    chunk_size = 1000
    help = ('Loads the JSONs of declarations downloaded from NACP '
            'into the persistence storage')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.es = connections.get_connection()

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

    def handle(self, *args, **options):
        try:
            base_dir = options['file_path']
            corrected_file = options['corrected_file']
        except IndexError:
            raise CommandError(
                'First argument must be a path to source files and second is file name of CSV with corrected declarations')

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
            self.stdout.write("Obtaining uuids of already indexed documents")

            s = NACPDeclaration.search().source([])
            existing_guids = set(
                h.meta.id.replace("nacp_", "") for h in s.scan())
            self.stdout.write("{} uuids are currently in index".format(
                len(existing_guids)))

            incoming_files = dict(
                filter(
                    None,
                    my_tiny_pool.map(parse_guid_from_fname, self.jsons)
                )
            )

            incoming_guids = set(incoming_files.keys())

            self.stdout.write("{} uuids are found in input folder".format(
                len(incoming_guids)))

            self.jsons = [
                incoming_files[k] for k in incoming_guids - existing_guids
            ]

            self.stdout.write("{} uuids left after the filtering".format(
                len(self.jsons)))

        for ix in range(0, len(self.jsons), self.chunk_size):
            chunk = self.jsons[ix:ix + self.chunk_size]

            result = list(
                filter(
                    None,
                    my_tiny_pool.map(DeclarationStaticObj.parse, chunk)
                )
            )

            counter += len(result)

            bulk(self.es, result)

            if ix:
                self.stdout.write(
                    'Loaded {} items to persistence storage'.format(ix))

        self.stdout.write(
            'Finished loading {} items to persistence storage'.format(counter))
