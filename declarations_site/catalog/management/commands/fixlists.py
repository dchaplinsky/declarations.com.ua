from django.core.management.base import BaseCommand

from catalog.elastic_models import Declaration


class Command(BaseCommand):
    help = 'Removes empty list items from previous versions of vulyk import'

    def handle(self, *args, **options):
        all_decls = Declaration.search().query('match_all').scan()
        for decl in all_decls:
            print('Processing decl for {}'.format(decl.general.full_name))
            for parent, field_key in self._decl_list_fields(decl):
                field = getattr(parent, field_key, None)
                if field:
                    filtered_field = list(filter(self._values_filter, field))
                    setattr(parent, field_key, filtered_field)
            decl.save()

    def _values_filter(self, field):
        return any([v for k, v in field._d_.items() if not k.endswith('_units')])

    def _decl_list_fields(self, decl):
        return [(decl.general, 'family'), (decl.income, '21'), (decl.income, '22'), (decl.income, '23'),
                (decl.estate, '24'), (decl.estate, '25'), (decl.estate, '26'), (decl.estate, '27'), (decl.estate, '28'),
                (decl.estate, '29'), (decl.estate, '30'), (decl.estate, '31'), (decl.estate, '32'), (decl.estate, '33'),
                (decl.estate, '34'), (decl.vehicle, '35'), (decl.vehicle, '36'), (decl.vehicle, '37'),
                (decl.vehicle, '38'), (decl.vehicle, '39'), (decl.vehicle, '40'), (decl.vehicle, '41'),
                (decl.vehicle, '42'), (decl.vehicle, '43'), (decl.vehicle, '44'), (decl.general, 'addresses')]
