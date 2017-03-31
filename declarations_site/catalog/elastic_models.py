import re
import json
import os.path
from operator import or_
from functools import reduce

from django.conf import settings
from django.db.models.functions import ExtractYear
from django.db.models import Sum, Count

from elasticsearch_dsl import DocType, Object, Keyword, Text, Completion, Nested, Date, Boolean, Search
from elasticsearch_dsl.query import Q
import dpath.util

from procurements.models import Transactions
from .constants import CATALOG_INDICES, BANK_EDRPOUS
from .utils import parse_fullname
from .templatetags.catalog import parse_raw_family_string


class NoneAwareDate(Date):
    """Elasticsearch DSL Date field chokes on None values and parses empty
    strings as current date, hence the workaround.
    TODO: move this upstream in some form."""
    def _to_python(self, data):
        if data is None:
            return data
        return super(NoneAwareDate, self)._to_python(data)


class RelatedDeclarationsMixin:
    def similar_declarations(self):
        s = Search(index=CATALOG_INDICES)\
            .query(
                'multi_match',
                query=self.general.full_name,
                operator='and',
                fields=[
                    'general.last_name',
                    'general.name',
                    'general.patronymic',
                    'general.full_name',
                ])\
            .query(~Q('term', _id=self.meta.id))

        return s[:12].execute()

    def family_declarations(self):
        def filter_silly_names(name):
            if not name:
                return False

            last_name, first_name, patronymic = parse_fullname(name)

            if len(first_name) == 1 or first_name.endswith("."):
                return False

            if len(patronymic) == 1 or patronymic.endswith("."):
                return False

            return True

        s = Search(index=CATALOG_INDICES)
        family_members = self.get_family_members()
        subqs = []

        for name in filter(filter_silly_names, family_members):
            subqs.append(
                Q(
                    "multi_match",
                    query=name,
                    operator="and",
                    fields=[
                        "general.last_name",
                        "general.name",
                        "general.patronymic",
                        "general.full_name",
                    ]
                ))

        if subqs:
            s = s.query(reduce(or_, subqs)).query(~Q('term', _id=self.meta.id))
            return s[:12].execute()
        else:
            return None

    def get_family_members(self):
        """
        Should return list of family member names
        """
        family = getattr(self.general, "family", None)
        if family:
            for member in family:
                if hasattr(member, "family_name"):
                    yield member.family_name
        else:
            for member in parse_raw_family_string(
                    getattr(self.general, "family_raw", "")):
                if "family_name" in member:
                    yield member["family_name"]


class Declaration(DocType, RelatedDeclarationsMixin):
    """Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""
    general = Object(
        properties={
            'full_name_suggest': Completion(preserve_separators=False),
            'full_name': Text(index=True, analyzer='ukrainian'),
            'name': Text(index=True, analyzer='ukrainian'),
            'patronymic': Text(index=True, analyzer='ukrainian'),
            'last_name': Text(index=True, analyzer='ukrainian'),
            'family_raw': Text(index=True, analyzer='ukrainian'),
            'family': Nested(
                properties={
                    'name': Text(index=True, analyzer='ukrainian'),
                    'relations': Keyword(index=False),
                    'inn': Keyword(index=False)
                }
            ),
            'post_raw': Text(index=True, analyzer='ukrainian'),
            'post': Object(
                properties={
                    'region': Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)}),
                    'office': Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)}),
                    'post': Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)})
                }
            ),
            'addresses': Nested(
                properties={
                    'place': Text(index=False),
                    'place_hidden': Boolean(index=False),
                    'place_district': Text(index=False),
                    'place_district_hidden': Boolean(index=False),
                    'place_city': Text(index=False),
                    'place_city_hidden': Boolean(index=False),
                    'place_city_type': Keyword(index=False),
                    'place_city_type_hidden': Boolean(index=False),
                    'place_address': Text(index=False),
                    'place_address_hidden': Boolean(index=False),
                    'place_address_type': Keyword(index=False)
                }
            )
        }
    )
    declaration = Object(
        properties={
            'date': NoneAwareDate(),
            'notfull': Boolean(index=False),
            'notfull_lostpages': Keyword(index=False),
            'additional_info': Boolean(index=False),
            'additional_info_text': Text(index=False),
            'needs_scancopy_check': Boolean(index=False)
        }
    )
    intro = Object(
        properties={
            'declaration_year': Keyword(index=True)
        }
    )
    ft_src = Text(index=True, analyzer='ukrainian')

    INCOME_SINGLE_PROPERTIES = {
        'value': Keyword(index=False),
        'value_unclear': Boolean(index=False),
        'comment': Text(index=False),
        'family': Keyword(index=False),
        'family_unclear': Boolean(index=False),
        'family_comment': Text(index=False)
    }
    INCOME_LIST_PROPERTIES = {
        'country': Keyword(index=False),
        'country_comment': Text(index=False),
        'cur': Keyword(index=False),
        'cur_units': Keyword(index=False),
        'uah_equal': Keyword(index=False)
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
        'region': Text(index=False),
        'address': Text(index=False),
        'space': Keyword(index=False),
        'space_units': Keyword(index=False),
        'space_comment': Text(index=False),
        'costs': Keyword(index=False),
        'costs_comment': Text(index=False),
        'costs_rent': Keyword(index=False),
        'costs_rent_comment': Text(index=False),
        'costs_property': Keyword(index=False),
        'costs_property_comment': Text(index=False)
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
        "brand": Text(index=False),
        "brand_info": Text(index=False),
        "year": Keyword(index=False),
        "sum": Keyword(index=False),
        "sum_comment": Text(index=False),
        "sum_rent": Keyword(index=False),
        "sum_rent_comment": Text(index=False),
        "brand_hidden": Boolean(index=False),
        "brand_info_hidden": Boolean(index=False),
        "brand_info_unclear": Boolean(index=False)
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
        'sum': Keyword(index=False),
        'sum_hidden': Boolean(index=False),
        'sum_units': Keyword(index=False),
        'sum_comment': Text(index=False),
        'sum_foreign': Keyword(index=False),
        'sum_foreign_units': Keyword(index=False),
        'sum_foreign_comment': Text(index=False)
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
        'sum': Keyword(index=False),
        'sum_comment': Text(index=False),
        'sum_units': Keyword(index=False),
        'sum_foreign': Keyword(index=False),
        'sum_foreign_comment': Text(index=False)
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


class NACPDeclaration(DocType, RelatedDeclarationsMixin):
    """NACP Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""
    general = Object(
        properties={
            'full_name_suggest': Completion(preserve_separators=False),
            'full_name': Text(index=True, analyzer='ukrainian'),
            'name': Text(index=True, analyzer='ukrainian'),
            'patronymic': Text(index=True, analyzer='ukrainian'),
            'last_name': Text(index=True, analyzer='ukrainian'),
            'post': Object(
                properties={
                    'region': Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)}),
                    'office': Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)}),
                    'post': Text(index=True, analyzer='ukrainian', fields={'raw': Keyword(index=True)})
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
            'declaration_year': Keyword(index=True),
            'declaration_year_to': NoneAwareDate(),
            'declaration_year_from': NoneAwareDate(),
            'doc_type': Keyword(index=True),
        }
    )
    nacp_src = Text(index=True, analyzer='ukrainian')
    nacp_orig = Object(include_in_all=False, enabled=False)

    def raw_html(self):
        fname = os.path.join(
            settings.NACP_DECLARATIONS_PATH,
            self.meta.id[5:7],
            os.path.basename(self.declaration.basename) + ".html")

        with open(fname, "r") as fp:
            d = fp.read()
        m = re.search("<\/style>(.*)</body>", d)
        declaration_html = m.group(1)

        # OH LORD, THAT'S NOT WHAT I'VE BEEN TAUGHT IN UNIVERSITY
        doc = declaration_html.replace(
            "</div></div></div><header><h2>",
            "</div></div><header><h2>"
        )
        # MY ASS IS ON FIRE
        doc = re.sub(
            "</table>\s*<header>",
            "</table></div><header>",
            doc
        )
        return doc

    def affiliated_companies(self):
        paths = [
            "step_7.*.emitent_ua_company_code",
            "step_7.*.rights.*.ua_company_code",
            "step_8.*.corporate_rights_company_code",
            "step_8.*.rights.*.ua_company_code",
            "step_9.*.beneficial_owner_company_code",
            
            # For now
            "step_11.*.rights.*.ua_company_code",
            "step_11.*.source_ua_company_code",
            "step_12.*.organization_ua_company_code",
            "step_12.*.rights.*.ua_company_code",
        ]

        src = self.nacp_orig.to_dict()
        results = []
        for path in paths:
            results += dpath.util.values(
                src, path, separator='.')


        # for section in dpath.util.values(
        #         src, "step_11.*", separator='.'):

        #     obj_type = section.get("objectType").lower()
        #     print(obj_type)
            # ".rights.*.ua_company_code",
            # "step_11.*.source_ua_company_code",

            # "step_12.*.organization_ua_company_code",
            # "step_12.*.rights.*.ua_company_code",


        results = filter(
            None,
            map(lambda x: x.strip().lstrip("0"), set(results))
        )

        return list(set(results) - BANK_EDRPOUS)

    def get_procurement_earnings_by_year(self):
        return Transactions.objects. \
            select_related("seller"). \
            filter(seller__code__in=self.affiliated_companies()). \
            annotate(year=ExtractYear('date')). \
            values("year"). \
            annotate(count=Count("pk"), sum_uah=Sum("volume_uah"))

    def get_procurement_earnings_by_company(self):
        return Transactions.objects. \
            select_related("seller"). \
            filter(seller__code__in=self.affiliated_companies()). \
            values("seller__code", "seller__pk", "seller__name"). \
            annotate(count=Count("pk"), sum_uah=Sum("volume_uah"))

    class Meta:
        index = 'nacp_declarations'
