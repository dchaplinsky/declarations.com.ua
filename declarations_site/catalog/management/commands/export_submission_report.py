import sys
from tqdm import tqdm
from csv import DictWriter
import argparse
from datetime import date, datetime
from django.core.management.base import BaseCommand
from catalog.elastic_models import NACPDeclaration


class Command(BaseCommand):
    help = "Export submission report as CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
        )
        parser.add_argument("--year_since", type=int, default=2015)

    def handle(self, *args, **options):
        all_decls = (
            NACPDeclaration.search()
            .query("match_all")
            .source(
                [
                    "declaration.url",
                    "intro.date",
                    "intro.doc_type",
                    "nacp_orig.step_1",
                ]
            )
        )

        all_decls = all_decls.filter(
            "range",
            intro__date={
                "gte": date(options["year_since"], 1, 1),
                "lt": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            },
        )

        w = DictWriter(
            options["outfile"],
            fieldnames=[
                "id",
                "declaration.url",
                "intro.date",
                "intro.doc_type",
                "nacp_orig.step_1.postCategory",
                "nacp_orig.step_1.postType",
            ],
        )

        for decl in tqdm(all_decls.scan(), total=all_decls.count()):
            w.writerow(
                {
                    "id": decl.meta.id,
                    "declaration.url": decl.declaration.url,
                    "intro.date": decl.intro.date.date(),
                    "intro.doc_type": decl.intro.doc_type,
                    "nacp_orig.step_1.postCategory": getattr(
                        decl.nacp_orig.step_1, "postCategory", ""
                    ),
                    "nacp_orig.step_1.postType": getattr(
                        decl.nacp_orig.step_1, "postType", ""
                    ),
                }
            )
