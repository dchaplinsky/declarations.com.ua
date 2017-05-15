import re
import sys
import json
import argparse
from django.core.management.base import BaseCommand
from elasticsearch_dsl import Search
from catalog.constants import CATALOG_INDICES
from catalog.elastic_models import Declaration, NACPDeclaration


class Command(BaseCommand):
    help = 'Export all the declarations into machinereadable format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sections', nargs='*',
            choices=["infocard", "raw_source", "unified_source",
                     "related_entities"],
            default=["infocard", "raw_source", "unified_source",
                     "related_entities"],
        )
        parser.add_argument(
            '--from', default=0, type=int)
        parser.add_argument(
            '--to', default=None, type=int)
        parser.add_argument(
            '--outfile', nargs='?', type=argparse.FileType('w'),
            default=sys.stdout)

    def handle(self, *args, **options):
        all_decls = Search(index=CATALOG_INDICES).doc_type(
            NACPDeclaration, Declaration).query('match_all')

        if options["to"] is not None:
            all_decls = all_decls[options["from"]:options["to"]].execute()
        elif options["from"]:
            all_decls = all_decls[options["from"]:].execute()
        else:
            all_decls = all_decls.scan()

        for i, decl in enumerate(all_decls):
            decl_json = decl.api_response(options["sections"])
            options["outfile"].write(json.dumps(decl_json) + "\n")

            if i and i % 1000 == 0:
                self.stdout.write("Exported %s declarations" % i)
