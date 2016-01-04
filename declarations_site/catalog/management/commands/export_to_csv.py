import re
import sys
import dpath.util
from csv import DictWriter
import argparse
from django.core.management.base import BaseCommand
from catalog.elastic_models import Declaration


class FilterException(Exception):
    pass


class Command(BaseCommand):
    help = 'Checks if we have all sources of the declarations'

    office_list = {
        "[Пп]резидента?": "офіс президента",
        " суд": "суд",
        "Верховна Рада": "парламент",
        " ?[пП]рокуратура": "прокуратура",
        " юстиції": "юстиція",
        "ДАІ": "міліція",
        "КМУ": "кабмін",
        " служба": "держслужба",
        " інспекція": "держслужба",
        " агентство": "держслужба",
        "Державне управління справами": "офіс президента",
        " комітет": "держслужба",
        "Збройні сили": "безпека",
        "Кабінет міністрів": "кабмін",
        "МВС": "міліція",
        "Міністерство ": "міністерство",
        " Мінкульту": "міністерство",
        " комісія": "держкомісія",
        "Національний банк": "Нацбанк",
        " ?адміністрація": "адміністрація",
        "Обласна рада": "облрада",
        "Районна [^ ]+ рада": "райрада",
        "Служба безпеки": "безпека",
        "управління державного майна": "фонд",
        "Фонд ": "фонд",
        "[Вв]нутрішніх": "міліція",
        'міська рада': 'міська рада'
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--field', nargs='*', default=["declaration.url"])
        parser.add_argument(
            '--from', default=0, type=int)
        parser.add_argument(
            '--to', default=None, type=int)
        parser.add_argument(
            '--outfile', nargs='?', type=argparse.FileType('w'),
            default=sys.stdout)

    def classify_office(self, res):
        for office_re in self.office_list:
            if re.search(office_re, res[0], flags=re.I):
                return self.office_list[office_re]

        return 'інше'

    def apply_operation(self, res, operation):
        def floatify(val):
            if val is None:
                val = ""

            return float(val.replace(",", ".") or 0)

        chunks = operation.split(":")
        flt = chunks[0]

        if flt == "sum":
            return sum(map(floatify, res))
        elif flt == "count":
            return len(res)
        elif flt == "classify_office":
            return self.classify_office(res)
        elif flt == "count_nonempty":
            return len(list(filter(None, res)))
        elif flt == "join":
            if len(chunks) != 2:
                raise FilterException(
                    "filter %s requires exactly 1 param" % flt)

            return chunks[1].join(res)
        else:
            raise FilterException("Unknown filter %s" % flt)

    def fetch_field(self, doc, expr):
        chunks = expr.split("|", 2)
        path = chunks[0]
        operation = chunks[1] if len(chunks) > 1 else ""

        if not path:
            return ""

        try:
            res = dpath.util.values(doc, path, separator='.')
        except KeyError:
            res = []

        if operation:
            res = self.apply_operation(res, operation)

        if isinstance(res, (list, tuple)):
            return ", ".join(map(str, res))
        else:
            return res

    def handle(self, *args, **options):
        all_decls = Declaration.search().query('match_all')
        if options["to"] is not None:
            all_decls = all_decls[options["from"]:options["to"]].execute()
        elif options["from"]:
            all_decls = all_decls[options["from"]:].execute()
        else:
            all_decls = all_decls.scan()

        w = DictWriter(
            options["outfile"], fieldnames=["_id"] + options["field"])

        w.writeheader()

        for decl in all_decls:
            decl_dict = decl.to_dict()

            row = {
                field: self.fetch_field(decl_dict, field)
                for field in options["field"]
            }

            row["_id"] = decl.meta.id

            w.writerow(row)
