import sys
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Text, Keyword
from django.core.management.base import BaseCommand
from catalog.utils import replace_apostrophes, concat_fields, keyword_for_sorting
from catalog.elastic_models import Declaration


def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, [key] + pre):
                    yield d
            elif isinstance(value, (list, tuple)):
                for v in value:
                    for d in dict_generator(v, [key] + pre):
                        yield d
            else:
                yield value
    else:
        yield indict


def filter_only_interesting(src):
    return list(
        filter(lambda x: isinstance(x, str) and x and x.lower() not in
               ["uah", "м²", "usd", "vulyk", "0", "", "грн", "eur",
                "приховано", "chesno", "га", "місто"] and not
               x.startswith("http"),
               dict_generator(src)))


class Command(BaseCommand):
    help = 'Replace apostrophes in names with correct ones, enable full text search in declaration content'

    def apply_migrations(self):
        # add index_card mapping if not exists
        index = 'declarations_v2'
        doc_type = 'declaration'

        es = Elasticsearch()
        mapping = es.indices.get_mapping(index=index, doc_type=doc_type)
        properties = mapping[index]['mappings'][doc_type]['properties']

        if 'index_card' not in properties:
            sys.stdout.write('Update mapping: add index_card\n')
            index_card_properties = {
                'properties': {
                    'index_card': Text(index=True, analyzer='ukrainian').to_dict()
                }
            }
            es.indices.put_mapping(index=index, doc_type=doc_type, body=index_card_properties)

        if 'full_name_for_sorting' not in properties['general']['properties']:
            sys.stdout.write('Update mapping: add full_name_for_sorting\n')
            full_name_properties = {
                'properties': {
                    'general': {
                        'properties': {
                            'full_name_for_sorting': Keyword(index=True, ignore_above=100).to_dict()
                        }
                    }
                }
            }
            es.indices.put_mapping(index=index, doc_type=doc_type, body=full_name_properties)

    def handle(self, *args, **options):
        self.apply_migrations()
        all_decls = Declaration.search().query('match_all').scan()
        for decl in all_decls:
            sys.stdout.write('Processing decl for {}\n'.format(decl.general.full_name))
            sys.stdout.flush()

            decl.general.full_name = replace_apostrophes(decl.general.full_name)
            decl.general.name = replace_apostrophes(decl.general.name)
            decl.general.last_name = replace_apostrophes(decl.general.last_name)
            decl.general.patronymic = replace_apostrophes(decl.general.patronymic)
            decl.general.full_name_suggest = {
                'input': [
                    decl.general.full_name,
                    ' '.join([decl.general.name,
                              decl.general.patronymic,
                              decl.general.last_name]),
                    ' '.join([decl.general.name,
                              decl.general.last_name])
                ]
            }

            decl.ft_src = "\n".join(filter_only_interesting(decl.to_dict()))

            decl.general.full_name_for_sorting = keyword_for_sorting(decl.general.full_name)
            decl.index_card = concat_fields(decl.to_dict(),
                                            Declaration.INDEX_CARD_FIELDS)

            decl.save()
