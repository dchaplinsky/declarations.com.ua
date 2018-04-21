import csv
import sys

from datetime import date
from collections import defaultdict

from django.utils.six.moves import input
from django.core.management.base import BaseCommand, CommandError

from elasticsearch_dsl import Q
from catalog.elastic_models import Declaration


class Command(BaseCommand):
    args = '<file_path> <prefix>'
    help = ('Loads the CSV catalog of clean vulyk declarations '
            'into the persistence storage')

    REGIONS_REMAP = {
        'ukraine': 'Загальнодержавний регіон',
        'kiev': 'м. Київ',
        '1': 'Івано-Франківська область',
        '2': 'Вінницька область',
        '3': 'Волинська область',
        '4': 'Дніпропетровська область',
        '5': 'Донецька область',
        '6': 'Житомирська область',
        '7': 'Закарпатська область',
        '8': 'Запорізька область',
        '9': 'Кіровоградська область',
        '10': 'Київська область',
        '11': 'Кримська Автономна Республіка',
        'Sevostopol': 'м. Севастополь',
        'Sevastopol': 'м. Севастополь',
        '12': 'Луганська область',
        '13': 'Львівська область',
        '14': 'Миколаївська область',
        '15': 'Одеська область',
        '16': 'Полтавська область',
        '17': 'Рівненська область',
        '18': 'Сумська область',
        '19': 'Тернопільська область',
        '20': 'Харківська область',
        '21': 'Херсонська область',
        '22': 'Хмельницька область',
        '23': 'Черкаська область',
        '24': 'Чернівецька область',
        '25': 'Чернігівська область'
    }

    RELATIONS_REMAP = {
        'spouse': 'Подружжя',
        'parents': 'Батьки',
        'children': 'Дитина',
        'grandchildren': 'Онук/Онука',
        'brother/sister': 'Брат/Сестра',
        'other': 'Інше'
    }

    SPACE_UNITS_REMAP = {
        'meters': 'м²',
        'gectars': 'га',
        'sotok': 'соток'
    }

    PLACE_TYPE_REMAP = {
        'city': 'Місто',
        'pgt': 'СМТ',
        'village': 'Село'
    }

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('file_path')
        parser.add_argument('prefix')

    def _group_column(self, rec):
        name = 'group'
        if '# group' in rec:
            name = '# group'
        elif 'Group' in rec:
            name = 'Group'
        return name

    def handle(self, *args, **options):
        try:
            file_path = options["file_path"]
            id_prefix = options["prefix"]
        except IndexError:
            raise CommandError(
                'First argument must be a source file and second is a id prefix')

        if hasattr(sys.stdin, 'isatty') and not sys.stdin.isatty():
            self.stdout.write(
                "To import something you need to run this command in TTY."
            )
            return

        groups = defaultdict(list)
        with open(file_path, 'r', newline='', encoding='utf-8') as source:
            reader = csv.DictReader(source, delimiter='\t')
            counter = 0
            for row in reader:
                status_col = 'Status' if 'Status' in row else 'Статус'
                if row[status_col] == '' or row[status_col] == 'Ок':
                    groups[row[self._group_column(row)]].append(row)
                    counter += 1

            self.stdout.write(
                'Read {} valid rows from the input file'.format(counter))

        Declaration.init()  # Apparently this is required to init mappings
        declarations = map(self.merge_group, groups.values())
        counter = 0
        for declaration in declarations:
            mapped = self.map_fields(declaration, id_prefix)

            res = Declaration.search().query(
                Q('terms', general__last_name=mapped['general']['last_name'].lower().split("-")) &
                Q('terms', general__name=mapped['general']['name'].lower().split("-")) &
                Q('term', intro__declaration_year=mapped['intro']['declaration_year'])
            )

            if mapped['general']['patronymic']:
                res = res.query('term', general__patronymic=mapped['general']['patronymic'].lower())

            res = res.execute()

            if res.hits:
                self.stdout.write(
                    "Person\n%s (%s, %s, %s, %s)\n%s\nalready exists" % (
                        mapped['general']['full_name'],
                        mapped['general']['post']['post'],
                        mapped['general']['post']['office'],
                        mapped['general']['post']['region'],
                        mapped['intro']['declaration_year'],
                        mapped['declaration']['url']))

                for i, hit in enumerate(res.hits):
                    self.stdout.write(
                        "%s: %s (%s, %s, %s, %s), %s\n%s" % (
                            i + 1,
                            hit['general']['full_name'],
                            hit['general']['post']['post'],
                            hit['general']['post']['office'],
                            hit['general']['post']['region'],
                            hit['intro']['declaration_year'],
                            hit._id,
                            hit['declaration']['url'])
                    )

                msg = (
                    "Select one of persons above to replace, or press [s] " +
                    "to skip current record or [c] to create new (default): ")

                r = input(msg).lower() or "c"
                if r == "s":
                    self.stdout.write("Ok, skipping")
                    continue

                if r.isdigit() and int(r) <= len(res.hits):
                    r = int(r) - 1
                    mapped['_id'] = res.hits[r]._id
                    self.stdout.write(
                        "Ok, replacing %s" % res.hits[r]._id)
                else:
                    self.stdout.write("Ok, adding new record")
            else:
                self.stdout.write(
                    "%s (%s) created" % (
                        mapped['general']['full_name'],
                        mapped['intro']['declaration_year']))

            item = Declaration(**mapped)
            item.save()
            counter += 1
        self.stdout.write(
            'Loaded {} items to persistence storage'.format(counter))

    def merge_group(self, group):
        merged_decl = group[0]
        toggle_keys = filter(lambda x: x.endswith('_hidden') or x.endswith('_unclear'), merged_decl.keys())
        for key in toggle_keys:
            if any([d[key] == 'on' for d in group]):
                merged_decl[key] = 'on'
        return merged_decl

    def map_fields(self, row, id_prefix):
        '''Map input source field names to the internal names'''
        def mapping_func(key, value):
            row_value = value.replace(u'й', u'й').replace(u'ї', u'ї').strip()

            if row_value == 'nodata':
                row_value = ''

            if key.endswith('_hidden') or key.endswith('_unclear'):
                row_value = len(row_value) > 0
            elif key in ('place', 'region'):
                row_value = self.REGIONS_REMAP.get(row_value, '')
            elif key == 'relations':
                row_value = self.RELATIONS_REMAP.get(row_value, '')
            elif key.endswith('_units') and key != 'space_units':
                row_value = row_value.upper()
            elif key == 'place_city_type':
                row_value = self.PLACE_TYPE_REMAP.get(row_value, '')
            elif key == 'space_units':
                row_value = self.SPACE_UNITS_REMAP.get(row_value, '')

            return row_value

        def flatten_map_record(record):
            def list_filter(field):
                return any([v['__value__'] for k, v in field.items() if not k.endswith('_units')])

            def step(key, value):
                if isinstance(value, dict):
                    if any(map(lambda x: x.startswith('0'), value.keys())):
                        # Flatten the dicts for 0-indexed keys into a list of values but only if there's at least
                        # one value in the list item's inner dict.
                        return [flatten_map_record(v) for k, v in sorted(value.items()) if list_filter(v)]
                    elif '__value__' in value:
                        # While we're at it why not map some values
                        return mapping_func(key, value['__value__'])
                    else:
                        return flatten_map_record(value)
                else:
                    return value

            if isinstance(record, dict):
                for k, v in record.items():
                    record[k] = step(k, v)

            return record

        # First let's automatically convert dotted column names into a nested dict structure where applicable
        record = {}
        for key, value in row.items():
            key_parts = key.split('.')
            if key_parts[0] == 'answer':
                # This pass uses a reference to last dict in order to build nested dict-only structure
                sub_record = record
                for part in key_parts[1:]:
                    sub_record = sub_record.setdefault(part, {})
                # Last dict reference is a key to an actual value, store it for later flattening
                sub_record['__value__'] = value
            elif key in ('task.data.link', 'group', '# group', 'Group'):
                # Useful technical fields
                record[key] = value
        # Now, we know there are list-like dict items so we need to flatten them and map values too
        record = flatten_map_record(record)

        return self.pre_process(record, id_prefix)

    def pre_process(self, rec, id_prefix):
        # Mr. Abromavičius strikes again!
        if rec['general']['last_name'] == 'Абромавічус':
            rec['general']['last_name'] = 'Абромавичус'
            rec['general']['full_name'] = 'Айварас Абромавичус'
        else:
            rec['general']['full_name'] = ' '.join(
                [rec['general']['last_name'], rec['general']['name'], rec['general']['patronymic']])
        rec['general']['full_name_suggest'] = {
            'input': [
                rec['general']['full_name'],
                u' '.join([rec['general']['name'],
                           rec['general']['patronymic'],
                           rec['general']['last_name']]),
                u' '.join([rec['general']['name'],
                           rec['general']['last_name']])
            ]
        }

        for family_member in rec['general']['family']:
            family_member['family_name'] = family_member.pop('name')
        rec['general']['family_raw'] = ''

        try:
            rec['declaration']['date'] = date(
                int(rec['declaration']['date_year']), int(rec['declaration']['date_month']),
                int(rec['declaration']['date_day']))
        except ValueError:
            # Elasticsearch doesn't like dates in bad format
            rec['declaration']['date'] = None
        for key in ('date_year', 'date_year_hidden', 'date_year_unclear',
                    'date_month', 'date_month_hidden', 'date_month_unclear',
                    'date_day', 'date_day_hidden', 'date_day_unclear'):
            rec['declaration'].pop(key, None)

        rec['declaration']['url'] = rec.pop('task.data.link').replace(' ', '')
        rec['_id'] = 'vulyk_{}_{}'.format(id_prefix, rec.pop(self._group_column(rec)))
        rec['source'] = 'VULYK'

        return rec
