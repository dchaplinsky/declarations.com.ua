from elasticsearch_dsl import Mapping, Text
from django.core.management.base import BaseCommand
from catalog.elastic_models import Declaration


class Command(BaseCommand):
    help = 'Generate index_card for full text search in declaration content'

    def handle(self, *args, **options):
        # add index_card mapping if not exists
        index = 'declarations_v2'
        doc_type = 'declaration'

        m = Mapping.from_es(index, doc_type)
        d = m.to_dict()[doc_type]

        # apply migration
        if 'index_card' not in d['properties']:
            print('Update mapping: add index_card field')
            m.field('index_card', Text(index=True, analyzer='ukrainian'))
            # monkey patching: disable broken _collect_analysis
            m._collect_analysis = lambda: {}
            m.save(index)

        all_decls = Declaration.search().query('match_all').scan()
        for decl in all_decls:
            print('Processing decl for {}'.format(decl.general.full_name))

            card_fields = [
                "general.last_name",
                "general.name",
                "general.patronymic",
                "general.full_name",
                "general.post.post",
                "general.post.office",
                "general.post.region",
                "intro.declaration_year",
                "intro.doc_type",
                "declaration.source",
                "declaration.url"
            ]
            index_card = ""

            for path in card_fields:
                head = decl
                for p in path.split('.'):
                    head = getattr(head, p, "")
                    if not head:
                        break
                index_card += str(head or "") + " "

            decl.index_card = index_card.strip()

            decl.save()
