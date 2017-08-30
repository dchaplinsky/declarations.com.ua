from django.core.management.base import BaseCommand

from catalog.constants import CATALOG_INDICES
from catalog.elastic_models import Declaration, NACPDeclaration


class Command(BaseCommand):
    help = 'Update intro.doc_type if not set'

    def add_arguments(self, parser):
        parser.add_argument('indices', nargs='+', choices=CATALOG_INDICES)

    def handle(self, *args, **options):
        for index in options['indices']:
            if index == 'declarations_v2':
                doc_type = Declaration
            elif index == 'nacp_declarations':
                doc_type = NACPDeclaration

            all_decls = doc_type.search().query('match_all').scan()
            updated = 0
            for decl in all_decls:
                if not getattr(decl.intro, 'doc_type', None):
                    setattr(decl.intro, 'doc_type', "Щорічна")
                    decl.save()
                    updated += 1
                    if updated % 100 == 0:
                        self.stdout.write("Updated {} docs\n".format(updated))

            self.stdout.write(self.style.SUCCESS(
                "For index {} updated {} documents\n".format(index, updated)))
