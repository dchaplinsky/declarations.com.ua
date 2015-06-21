import os
import re
import csv
import json

from copy import deepcopy
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch_dsl.filter import Term

from catalog.elastic_models import Declaration


DEFS_PATH = os.path.join(settings.BASE_DIR, 'catalog/data/mapping_defs.json')


class Command(BaseCommand):
    args = '<file_path>'
    help = ('Loads the CSV catalog of existing declarations '
            'into the persistence storage')

    REGIONS_REMAP = {
        'АРК': 'Кримська Автономна Республіка',
        'Загальнодержавний': 'Загальнодержавний регіон',
        'Київ': 'м. Київ',
    }

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        with open(DEFS_PATH, 'r') as defs_file:
            data = defs_file.read()
            # Remove comments from the file
            data = re.sub("#.*$", "", data, flags=re.MULTILINE)

            self.mapping_defs = json.loads(data)

    def recur_map(self, f, data):
        def step(k, v):
            if isinstance(v, str):
                return f(k, v)
            elif isinstance(v, (list, dict)):
                return self.recur_map(f, data[k])

        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = step(k, v)

        if isinstance(data, list):
            for k, v in enumerate(data):
                data[k] = step(k, v)

        return data

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a source file')

        with open(file_path, 'r', newline='', encoding='utf-8') as source:
            reader = csv.DictReader(source, delimiter=";")
            counter = 0
            Declaration.init()  # Apparently this is required to init mappings
            for row in reader:
                mapped = self.map_fields(row)

                res = Declaration.search().filter(
                    Term(general__last_name=mapped[
                        "general"]["last_name"].lower().split("-")) &
                    Term(general__name=mapped[
                        "general"]["name"].lower().split("-")) &
                    Term(intro__declaration_year=mapped[
                        "intro"]["declaration_year"])
                )

                if mapped["general"]["patronymic"]:
                    res = res.filter(Term(general__patronymic=mapped[
                        "general"]["patronymic"].lower()))

                res = res.execute()

                if res.hits:
                    mapped["id"] = res.hits[0]._id

                item = Declaration(**mapped)
                item.save()
                counter += 1
            self.stdout.write(
                'Loaded {} items to persistence storage'.format(counter))

    def map_fields(self, row):
        """Map input source field names to the internal names"""
        def mapping_func(key, value):
            if len(value) > 2 and value[0] == '%' and value[-1] == '%':
                # If it's in form "%<value>%", return the value
                return value[1:-1]

            row_value = row.get(value, '').replace(u"й", u"й").replace(
                u"ї", u"ї")

            if row_value in ('!notmatched', '!Пусто'):
                row_value = ''

            if key.endswith('_hidden') or key.endswith('_unclear'):
                return len(row_value) > 0
            else:
                return row_value

        return self.pre_process(self.recur_map(mapping_func,
                                deepcopy(self.mapping_defs)))

    def pre_process(self, rec):
        if rec['general']['full_name'] == 'Айварас Абромавичус':
            # This guy's a special case. Otherwise name and last name are mixed up, which affects search.
            rec['general']['name'] = 'Айварас'
            rec['general']['last_name'] = 'Абромавичус'
        else:
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

        rec["general"]["post"]["region"] = self.REGIONS_REMAP.get(
            rec["general"]["post"]["region"].strip(),
            rec["general"]["post"]["region"].strip())

        try:
            rec['declaration']['date'] = datetime.strptime(
                rec['declaration']['date'], '%m/%d/%Y').date()
        except ValueError:
            # Elasticsearch doesn't like dates in bad format
            rec['declaration']['date'] = None

        rec['declaration']['needs_scancopy_check'] = rec['declaration']['needs_scancopy_check'] != 'Ок'

        return rec
