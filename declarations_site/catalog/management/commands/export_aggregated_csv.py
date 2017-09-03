from csv import DictWriter
from elasticsearch_dsl.query import Q
from django.core.management.base import BaseCommand

from catalog.elastic_models import NACPDeclaration

AGGREGATED_FIELD_NAME = 'aggregated'


class Command(BaseCommand):
    help = 'Export aggregated values from NACP declarations '
    '(annual only with corrected declarations resolved by default) into CSV format'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            '--export_all',
            dest='export_all',
            default=False,
            action='store_true',
            help='Export all declarations (all types, both corrected and originals)',
        )

        parser.add_argument(
            'destination',
            help='Path to csv file',
        )

    def handle(self, *args, **options):
        to_export = NACPDeclaration.search().source(
            include=[AGGREGATED_FIELD_NAME]).query("exists", field=AGGREGATED_FIELD_NAME)

        if not options["export_all"]:
            to_export = to_export.query(
                "bool",
                must=[Q("term", intro__doc_type="Щорічна")],
                must_not=[Q("exists", field="original_declarations")]
            )

        w = None
        with open(options["destination"], "w") as fp:
            for i, d in enumerate(to_export.scan()):
                row = d[AGGREGATED_FIELD_NAME].to_dict()
                row['id'] = d.meta.id

                if not w:
                    w = DictWriter(fp, fieldnames=row.keys())
                    w.writeheader()

                w.writerow(row)
                if i % 10000 == 0 and i:
                    self.stdout.write("{} declarations exported".format(i))
