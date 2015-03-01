import os
import re
import csv
import json

from copy import deepcopy

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from catalog.elastic_models import Declaration


DEFS_PATH = os.path.join(settings.BASE_DIR, 'catalog/data/mapping_defs.json')


class Command(BaseCommand):
    args = '<file_path>'
    help = ('Loads the CSV catalog of existing declarations '
            'into the persistence storage')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        with open(DEFS_PATH) as defs_file:
            data = defs_file.read()
            # Remove comments from the file
            data = re.sub("#.*$", "", data, flags=re.MULTILINE)

            self.mapping_defs = json.loads(data)

    def recur_map(self, f, data):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = f(v)
                elif isinstance(v, (list, dict)):
                    data[k] = self.recur_map(f, data[k])

        if isinstance(data, list):
            for k, v in enumerate(data):
                if isinstance(v, str):
                    data[k] = f(v)
                elif isinstance(v, (list, dict)):
                    data[k] = self.recur_map(f, data[k])

        return data

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a source file')

        with open(file_path, 'r', newline='', encoding='cp1251') as source:
            reader = csv.DictReader(source, delimiter=";")
            counter = 0
            for row in reader:
                item = Declaration(**self.map_fields(row))
                item.save()
                counter += 1
            self.stdout.write(
                'Loaded {} items to persistence storage'.format(counter))

    def map_fields(self, row):
        """Map input source field names to the internal names"""

        return self.pre_process(self.recur_map(lambda v: row.get(v, ""),
                                deepcopy(self.mapping_defs)))

    def pre_process(self, rec):
        chunks = rec["general"]["last_name"].split(u" ")

        if len(chunks) == 2:
            rec["general"]["last_name"] = chunks[0]
            rec["general"]["name"] = chunks[1]
        else:
            rec["general"]["last_name"] = u" ".join(chunks[:-2])
            rec["general"]["name"] = chunks[-2]
            rec["general"]["patronymic"] = chunks[-1]

        return rec
