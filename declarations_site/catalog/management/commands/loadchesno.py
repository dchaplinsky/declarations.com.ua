import json

from pprint import pprint
from copy import deepcopy
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from catalog.elastic_models import Declaration
from catalog.data.mapping_chesno import MAPPING, SubDocument


class Command(BaseCommand):
    args = '<file_path>'
    help = ('Loads the JSON catalog of existing declarations from CHESNO.ua'
            'into the persistence storage')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.mapping_defs = MAPPING

    def recur_map(self, resolver_func, mapping_data, source_data):
        def step(k, v):
            if isinstance(v, str):
                return resolver_func(k, v, source_data)
            elif isinstance(v, (list, dict)):
                return self.recur_map(resolver_func, mapping_data[k],
                                      source_data)
            elif isinstance(v, SubDocument):
                return [
                    self.recur_map(resolver_func, deepcopy(v.mapping), sub_d)
                    for sub_d in resolver_func(k, v.path_prefix, source_data)]

        if isinstance(mapping_data, dict):
            for k, v in mapping_data.items():
                mapping_data[k] = step(k, v)

        if isinstance(mapping_data, list):
            for k, v in enumerate(mapping_data):
                mapping_data[k] = step(k, v)

        return mapping_data

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a source file')

        with open(file_path, 'r', newline='', encoding='utf-8') as source:
            decls = json.load(source)

            counter = 0
            Declaration.init()  # Apparently this is required to init mappings
            for row in decls:
                pprint(self.map_fields(row))
                # item = Declaration(**self.map_fields(row))

                # item.save()
                # counter += 1
            self.stdout.write(
                'Loaded {} items to persistence storage'.format(counter))

    def map_fields(self, row):
        """Map input source field names to the internal names"""
        def get_by_path(val, path):
            path = [int(p) if p.isdigit() else p for p in path.split("/")]

            for p in path:
                try:
                    val = val[p]
                except (KeyError, IndexError):
                    return ""

            return val

        def mapping_func(key, path, document):
            if len(path) > 2 and path[0] == '%' and path[-1] == '%':
                # If it's in form "%<path>%", return the path
                return path[1:-1]

            row_value = get_by_path(document, path)

            if isinstance(row_value, str):
                row_value = row_value.replace(u"й", u"й").replace(u"ї", u"ї")

            return row_value

        return self.pre_process(self.recur_map(mapping_func,
                                deepcopy(self.mapping_defs),
                                row))

    def pre_process(self, rec):
        name_chunks = rec["general"]["full_name"].split(u" ")

        if len(name_chunks) == 2:
            rec["general"]["last_name"] = name_chunks[0]
            rec["general"]["name"] = name_chunks[1]
        else:
            rec["general"]["last_name"] = u" ".join(name_chunks[:-2])
            rec["general"]["name"] = name_chunks[-2]
            rec["general"]["patronymic"] = name_chunks[-1]

        rec["general"]["full_name_suggest"] = {
            "input": [
                u" ".join([rec["general"]["last_name"], rec["general"]["name"],
                           rec["general"]["patronymic"]]),
                u" ".join([rec["general"]["name"],
                           rec["general"]["patronymic"],
                           rec["general"]["last_name"]]),
                u" ".join([rec["general"]["name"],
                           rec["general"]["last_name"]])
            ],
            "output": rec["general"]["full_name"]
        }

        rec["_id"] = "chesno_{}".format(rec["_id"])

        return rec
