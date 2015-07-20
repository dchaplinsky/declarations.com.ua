import json

from copy import deepcopy

from django.core.management.base import BaseCommand, CommandError

from elasticsearch_dsl.filter import Term

from catalog.elastic_models import Declaration
from catalog.data.mapping_chesno import MAPPING, SubDocument, NumericOperation, JoinOperation
from catalog.templatetags.catalog import parse_family_member


class Command(BaseCommand):
    args = '<file_path>'
    help = ('Loads the JSON catalog of existing declarations from CHESNO.ua'
            'into the persistence storage')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.mapping_defs = MAPPING

    def recur_map(self, resolver_func, mapping_data, source_data):
        def step(k, v):
            if isinstance(v, (list, dict)):
                return self.recur_map(resolver_func, mapping_data[k],
                                      source_data)
            elif isinstance(v, SubDocument):
                return [
                    self.recur_map(resolver_func, deepcopy(v.mapping), sub_d)
                    for sub_d in
                    resolver_func(v.path_prefix, source_data) or []]
            else:
                return resolver_func(v, source_data)

        if isinstance(mapping_data, dict):
            for k, v in mapping_data.items():
                mapping_data[k] = step(k, v)

        if isinstance(mapping_data, list):
            for k, v in enumerate(mapping_data):
                mapping_data[k] = step(k, v)

        return mapping_data

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a source file')

        with open(file_path, 'r', newline='', encoding='utf-8') as source:
            decls = json.load(source)

            counter = 0
            Declaration.init()  # Apparently this is required to init mappings
            for row in decls:
                if "fields" not in row["details"]:
                    continue

                mapped = self.map_fields(row)
                res = Declaration.search().filter(
                    Term(general__last_name=mapped[
                        'general']['last_name'].lower().split('-')) &
                    Term(general__name=mapped[
                        'general']['name'].lower().split('-')) &
                    Term(intro__declaration_year=int(mapped['intro']['declaration_year']))
                )

                if mapped['general']['patronymic']:
                    res = res.filter(Term(general__patronymic=mapped[
                        'general']['patronymic'].lower()))

                self.stdout.write(
                    "Checking %s (%s)" % (
                        mapped['general']['full_name'],
                        mapped['intro']['declaration_year']))

                res = res.execute()

                if not res.hits:
                    item = Declaration(**mapped)
                    item.save()

                    counter += 1
                else:
                    self.stdout.write(
                        "%s (%s) already exists" % (
                            mapped['general']['full_name'],
                            mapped['intro']['declaration_year']))

            self.stdout.write(
                'Loaded {} items to persistence storage'.format(counter))

    def map_fields(self, row):
        """Map input source field names to the internal names"""
        def get_by_path(val, path):
            path = [int(p) if p.isdigit() else p for p in path.split("/")]

            for p in path:
                try:
                    val = val[p]
                except (KeyError, IndexError):
                    return ""

            return val

        def mapping_func(path, document):
            if len(path) > 2 and path[0] == '%' and path[-1] == '%':
                # If it's in form "%<path>%", return the path
                return path[1:-1]

            if isinstance(path, NumericOperation):
                row_value = str(path.operation(
                    float(sub_d[path.field])
                    for sub_d in mapping_func(path.path_prefix, document)
                    if sub_d[path.field]
                ))
            elif isinstance(path, JoinOperation):
                row_value = path.separator.join(
                    mapping_func(path, document) for path in path.paths
                )
            else:
                row_value = get_by_path(document, path)

            if isinstance(row_value, str):
                row_value = row_value.replace(u"й", u"й").replace(u"ї", u"ї")
            elif isinstance(row_value, float):
                row_value = str(row_value)

            return row_value

        return self.pre_process(self.recur_map(mapping_func,
                                deepcopy(self.mapping_defs),
                                row))

    def pre_process(self, rec):
        # We screwed a bit with pre-processing those data from Chesno
        rec["general"]["post"]["region"] = "Загальнодержавний регіон"

        # This guy's really lucky.
        # Everyone's getting his last name wrong and everyone's testing the code on his declaration.

        if rec['general']['last_name'] == 'Абромавічус':
            rec['general']['last_name'] = 'Абромавичус'
            rec['general']['full_name'] = 'Айварас Абромавичус'

        rec['general']['full_name_suggest'] = {
            'input': [
                u' '.join([rec['general']['last_name'], rec['general']['name'],
                           rec['general']['patronymic']]),
                u' '.join([rec['general']['name'],
                           rec['general']['patronymic'],
                           rec['general']['last_name']]),
                u' '.join([rec['general']['name'],
                           rec['general']['last_name']])
            ],
            'output': rec['general']['full_name']
        }
        for i, family_member in enumerate(rec['general']['family']):
            parsed = parse_family_member(family_member['family_name'])
            if 'raw' in parsed:
                rec['general']['family_raw'] = parsed['raw']
            else:
                rec['general']['family'][i] = parsed

        rec['_id'] = 'chesno_{}'.format(rec['_id'])
        if rec['declaration']['url']:
            rec['declaration']['url'] = 'http://www.chesno.org{}'.format(rec['declaration']['url'])
        else:
            rec['declaration']['url'] = rec['declaration']['link']
            rec['declaration'].pop('link')
        rec['declaration']['date'] = None

        return rec
