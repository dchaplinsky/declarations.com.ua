import re
import os.path
from django.conf import settings
from elasticsearch_dsl import DocType, Object, String, Completion, Nested, Date, Boolean


class NoneAwareDate(Date):
    """Elasticsearch DSL Date field chokes on None values and parses empty
    strings as current date, hence the workaround.
    TODO: move this upstream in some form."""
    def _to_python(self, data):
        if data is None:
            return data
        return super(NoneAwareDate, self)._to_python(data)


class Declaration(DocType):
    """Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""
    general = Object(
        properties={
            'full_name_suggest': Completion(preserve_separators=False),
            'full_name': String(index='analyzed'),
            'name': String(index='analyzed'),
            'patronymic': String(index='analyzed'),
            'last_name': String(index='analyzed'),
            'family_raw': String(index='analyzed'),
            'family': Nested(
                properties={
                    'name': String(index='analyzed'),
                    'relations': String(index='no'),
                    'inn': String(index='no')
                }
            ),
            'post_raw': String(index='analyzed'),
            'post': Object(
                properties={
                    'region': String(index='not_analyzed'),
                    'office': String(index='not_analyzed'),
                    'post': String(index='analyzed')
                }
            ),
            'addresses': Nested(
                properties={
                    'place': String(index='no'),
                    'place_hidden': Boolean(index='no'),
                    'place_district': String(index='no'),
                    'place_district_hidden': Boolean(index='no'),
                    'place_city': String(index='no'),
                    'place_city_hidden': Boolean(index='no'),
                    'place_city_type': String(index='no'),
                    'place_city_type_hidden': Boolean(index='no'),
                    'place_address': String(index='no'),
                    'place_address_hidden': Boolean(index='no'),
                    'place_address_type': String(index='no')
                }
            )
        }
    )
    declaration = Object(
        properties={
            'date': NoneAwareDate(),
            'notfull': Boolean(index='no'),
            'notfull_lostpages': String(index='no'),
            'additional_info': Boolean(index='no'),
            'additional_info_text': String(index='no'),
            'needs_scancopy_check': Boolean(index='no')
        }
    )
    intro = Object(
        properties={
            'declaration_year': String(index="not_analyzed")
        }
    )

    INCOME_SINGLE_PROPERTIES = {
        'value': String(index='no'),
        'value_unclear': Boolean(index='no'),
        'comment': String(index='no'),
        'family': String(index='no'),
        'family_unclear': Boolean(index='no'),
        'family_comment': String(index='no')
    }
    INCOME_LIST_PROPERTIES = {
        'country': String(index='no'),
        'country_comment': String(index='no'),
        'cur': String(index='no'),
        'cur_units': String(index='no'),
        'uah_equal': String(index='no')
    }
    income = Object(
        properties={
            '5': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '6': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '7': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '8': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '9': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '10': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '11': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '12': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '13': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '14': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '15': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '16': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '17': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '18': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '19': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '20': Object(
                properties=INCOME_SINGLE_PROPERTIES
            ),
            '21': Nested(
                properties=INCOME_LIST_PROPERTIES
            ),
            '22': Nested(
                properties=INCOME_LIST_PROPERTIES
            )
        }
    )

    ESTATE_PROPERTIES = {
        'region': String(index='no'),
        'address': String(index='no'),
        'space': String(index='no'),
        'space_units': String(index='no'),
        'space_comment': String(index='no'),
        'costs': String(index='no'),
        'costs_comment': String(index='no'),
        'costs_rent': String(index='no'),
        'costs_rent_comment': String(index='no'),
        'costs_property': String(index='no'),
        'costs_property_comment': String(index='no')
    }
    estate = Object(
        properties={
            '23': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '24': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '25': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '26': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '27': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '28': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '29': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '30': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '31': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '32': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '33': Nested(
                properties=ESTATE_PROPERTIES
            ),
            '34': Nested(
                properties=ESTATE_PROPERTIES
            )
        }
    )

    VEHICLE_PROPERTIES = {
        "brand": String(index='no'),
        "brand_info": String(index='no'),
        "year": String(index='no'),
        "sum": String(index='no'),
        "sum_comment": String(index='no'),
        "sum_rent": String(index='no'),
        "sum_rent_comment": String(index='no'),
        "brand_hidden": Boolean(index='no'),
        "brand_info_hidden": Boolean(index='no'),
        "brand_info_unclear": Boolean(index='no')
    }
    vehicle = Object(
        properties={
            '35': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '36': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '37': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '38': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '39': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '40': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '41': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '42': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '43': Nested(
                properties=VEHICLE_PROPERTIES
            ),
            '44': Nested(
                properties=VEHICLE_PROPERTIES
            )
        }
    )

    BANKS_PROPERTIES = {
        'sum': String(index='no'),
        'sum_hidden': Boolean(index='no'),
        'sum_units': String(index='no'),
        'sum_comment': String(index='no'),
        'sum_foreign': String(index='no'),
        'sum_foreign_units': String(index='no'),
        'sum_foreign_comment': String(index='no')
    }
    banks = Object(
        properties={
            '45': Nested(
                properties=BANKS_PROPERTIES
            ),
            '46': Nested(
                properties=BANKS_PROPERTIES
            ),
            '47': Nested(
                properties=BANKS_PROPERTIES
            ),
            '48': Nested(
                properties=BANKS_PROPERTIES
            ),
            '49': Nested(
                properties=BANKS_PROPERTIES
            ),
            '50': Nested(
                properties=BANKS_PROPERTIES
            ),
            '51': Nested(
                properties=BANKS_PROPERTIES
            ),
            '52': Nested(
                properties=BANKS_PROPERTIES
            ),
            '53': Nested(
                properties=BANKS_PROPERTIES
            ),
        }
    )

    LIABILITIES_PROPERTIES = {
        'sum': String(index='no'),
        'sum_comment': String(index='no'),
        'sum_units': String(index='no'),
        'sum_foreign': String(index='no'),
        'sum_foreign_comment': String(index='no')
    }
    liabilities = Object(
        properties={
            '54': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '55': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '56': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '57': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '58': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '59': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '60': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '61': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '62': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '63': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
            '64': Nested(
                properties=LIABILITIES_PROPERTIES
            ),
        }
    )

    class Meta:
        index = 'declarations_v2'


class NACPDeclaration(DocType):
    """NACP Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""
    general = Object(
        properties={
            'full_name_suggest': Completion(preserve_separators=False),
            'full_name': String(index='analyzed'),
            'name': String(index='analyzed'),
            'patronymic': String(index='analyzed'),
            'last_name': String(index='analyzed'),
            'post': Object(
                properties={
                    'region': String(index='not_analyzed'),
                    'office': String(index='not_analyzed'),
                    'post': String(index='analyzed')
                }
            )
        }
    )
    declaration = Object(
        properties={
            'date': NoneAwareDate(),
        }
    )
    intro = Object(
        properties={
            'declaration_year': String(index="not_analyzed"),
            'declaration_year_to': NoneAwareDate(),
            'declaration_year_from': NoneAwareDate(),
            'doc_type': String(index='not_analyzed'),
        }
    )

    def raw_html(self):
        fname = os.path.join(
            settings.NACP_DECLARATIONS_PATH,
            self.meta.id[5:7],
            os.path.basename(self.declaration.basename) + ".html")

        with open(fname, "r") as fp:
            d = fp.read()
        m = re.search("<\/style>(.*)</body>", d)
        declaration_html = m.group(1)

        return declaration_html.replace("</div></div></div><header><h2>", "</div></div><header><h2>")

    class Meta:
        index = 'nacp_declarations'
