from django.core.management.base import BaseCommand
from catalog.utils import replace_apostrophes
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

    def handle(self, *args, **options):
        all_decls = Declaration.search().query('match_all').scan()
        for decl in all_decls:
            print('Processing decl for {}'.format(decl.general.full_name))

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
                ],
                'output': decl.general.full_name
            }

            decl.ft_src = "\n".join(filter_only_interesting(decl.to_dict()))

            decl.save()
