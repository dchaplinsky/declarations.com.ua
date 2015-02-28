import os
import csv
import json

from operator import itemgetter

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from catalog.elastic_models import Declaration


DEFS_PATH = os.path.join(settings.BASE_DIR, 'catalog/data/mapping_defs.json')


class Command(BaseCommand):
    args = '<file_path>'
    help = 'Loads the catalog of declaration into the persistence storage'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        with open(DEFS_PATH) as defs_file:
            self.mapping_defs = json.load(defs_file)

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a source file')

        with open(file_path, 'r', newline='', encoding='utf-8') as source:
            reader = csv.DictReader(source)
            counter = 0
            for row in reader:
                item = Declaration(**self.map_fields(row))
                item.save()
                counter += 1
            self.stdout.write('Loaded {} items to persistence storage'.format(counter))

    def map_fields(self, row):
        """Map input source field names to the internal names"""
        mapped_row = map(lambda x: (self.mapping_defs.get(x[0]), x[1]), row.items())
        # Filter out empty values (not mapped or just empty from the source) and transform to dict
        return dict(filter(itemgetter(0), mapped_row))
