from django.core.management.base import BaseCommand

from elasticsearch_dsl.connections import connections

from catalog.constants import (
    CATALOG_INDICES, CATALOG_INDEX_SETTINGS, OLD_DECLARATION_INDEX,
    NACP_DECLARATION_INDEX, NACP_DECLARATION_NEW_FORMAT_INDEX
)

from catalog.elastic_models import (
    declarations_idx, nacp_declarations_idx, nacp_declarations_new_format_idx
)


class Command(BaseCommand):
    help = 'Creates ElasticSearch indices with proper settings'

    def add_arguments(self, parser):
        parser.add_argument('indices', nargs='+', choices=CATALOG_INDICES + (NACP_DECLARATION_NEW_FORMAT_INDEX, ))

    def handle(self, *args, **options):
        for index in options['indices']:
            if index == OLD_DECLARATION_INDEX:
                idx = declarations_idx
            elif index == NACP_DECLARATION_INDEX:
                idx = nacp_declarations_idx
            elif index == NACP_DECLARATION_NEW_FORMAT_INDEX:
                idx = nacp_declarations_new_format_idx

            es = connections.get_connection('default')
            if es.indices.exists(index=index):
                self.stdout.write('Index "{}" already exists, not creating.'.format(index))
                return

            idx.create()
            es.indices.put_settings(index=index, body=CATALOG_INDEX_SETTINGS)
            self.stdout.write('Created index "{}".'.format(index))
