import re
import os.path
from operator import or_
from functools import reduce
from datetime import date

from django.conf import settings
from django.urls import reverse
from django.db.models.functions import ExtractYear
from django.db.models import Sum, Count
from django.template.loader import render_to_string

from elasticsearch_dsl import (
    DocType,
    Object,
    Keyword,
    MetaField,
    Text,
    Completion,
    Nested,
    Date,
    Boolean,
    Search,
    Double,
    Index,
    analyzer,
    tokenizer,
)

from elasticsearch_dsl.query import Q
import jmespath


from procurements.models import Transactions
from .constants import (
    CATALOG_INDICES,
    BANK_EDRPOUS,
    INCOME_TYPES,
    MONETARY_ASSETS_TYPES,
    OLD_DECLARATION_INDEX,
    NACP_DECLARATION_INDEX,
    NUMBER_OF_SHARDS,
    NUMBER_OF_REPLICAS,
    NACP_SELECTORS_TO_TRANSLATE,
    PAPER_SELECTORS_TO_TRANSLATE
)


from .utils import parse_fullname, blacklist
from .templatetags.catalog import parse_raw_family_string
from .converters import PaperToNACPConverter, ConverterError
from .translator import HTMLTranslator


class NoneAwareDate(Date):
    """Elasticsearch DSL Date field chokes on None values and parses empty
    strings as current date, hence the workaround.
    TODO: move this upstream in some form."""

    def _to_python(self, data):
        if data is None:
            return data
        return super(NoneAwareDate, self)._to_python(data)


namesAutocompleteAnalyzer = analyzer(
    "namesAutocompleteAnalyzer",
    tokenizer=tokenizer(
        "autocompleteTokenizer",
        type="edge_ngram",
        min_gram=1,
        max_gram=25,
        token_chars=["letter", "digit"],
    ),
    filter=["lowercase"],
)

namesAutocompleteSearchAnalyzer = analyzer(
    "namesAutocompleteSearchAnalyzer",
    tokenizer=tokenizer("whitespace"),

    filter=[
        "lowercase"
    ]
)


class AbstractDeclaration(object):
    def infocard(self):
        raise NotImplemented()

    def raw_source(self):
        raise NotImplemented()

    def unified_source(self):
        raise NotImplemented()

    def related_entities(self):
        raise NotImplemented()

    def _is_change_form(self):
        raise NotImplemented

    def related_documents(self):
        return [
            document.api_response(fields=["related_entities", "guid", "aggregated_data"])
            for document in self.similar_declarations(limit=100, return_full_body=True)
            if not document._is_change_form()
        ]

    def guid(self):
        return self.meta.id

    def prepare_translations(self, language, infocard_only=False):
        assert self.CONTENT_SELECTORS, "You should define CONTENT_SELECTORS first"

        if language == "en":
            if infocard_only:
                self.translator = HTMLTranslator(
                    html=None,
                    selectors=[],
                    extra_phrases=[
                        self.general.post.post,
                        self.general.post.office,
                        self.general.post.region,
                        getattr(self.general.post, "actual_region", ""),
                        self.intro.doc_type
                    ]
                )
            else:
                self.translator = HTMLTranslator(
                    self.raw_html(),
                    selectors=self.CONTENT_SELECTORS,
                    extra_phrases=[
                        self.general.post.post,
                        self.general.post.office,
                        self.general.post.region,
                        getattr(self.general.post, "actual_region", ""),
                        self.intro.doc_type
                    ],
                )

    def raw_en_html(self):
        assert hasattr(self, "translator"), "You should call prepare_translations first"
        return self.translator.get_translated_html()

    def _full_name(self, language):
        name = "{} {} {}".format(
            self.general.last_name, self.general.name, self.general.patronymic
        )

        if language == "en":
            assert hasattr(
                self, "translator"
            ), "You should call prepare_translations first"

            phrase = self.translator.translate(name, just_transliterate=True)
            return phrase["translation"]
        else:
            return name

    def _translate_one_field(self, field, language):
        if field:
            if language == "en":
                assert hasattr(
                    self, "translator"
                ), "You should call prepare_translations first"

                phrase = self.translator.translate(field)
                return phrase["translation"]
            else:
                return field
        else:
            return ""

    def _position(self, language):
        return self._translate_one_field(self.general.post.post, language)

    def _office(self, language):
        return self._translate_one_field(self.general.post.office, language)

    def _region(self, language):
        return self._translate_one_field(self.general.post.region, language)

    def _actual_region(self, language):
        return self._translate_one_field(self.general.post.actual_region, language)

    def _declaration_type(self, language):
        return self._translate_one_field(self.intro.doc_type, language)

    def api_response(self, fields=None):
        all_fields = [
            "guid",
            "infocard",
            "raw_source",
            "unified_source",
            "related_entities"
        ]

        if fields is None:
            fields = all_fields
        else:
            fields = [
                f for f in fields if f in set(all_fields + ["guid", "aggregated_data", "related_documents"])
            ]

        return {f: getattr(self, f)() for f in fields}

    def similar_declarations(self, language=None, limit=12, return_full_body=False):
        fields = [
            "general.last_name",
            "general.name",
            "general.patronymic",
            "general.full_name",
        ]

        s = (
            Search(index=CATALOG_INDICES)
            .query(
                "multi_match",
                query=self.general.full_name,
                operator="and",
                fields=fields,
            )
            .query(~Q("term", _id=self.meta.id))
        )

        if return_full_body:
            s = s.doc_type(NACPDeclaration, Declaration)
            docs = s[:limit].execute()

            if language is not None:
                for d in docs:
                    d.prepare_translations(language, infocard_only=True)
        else:
            docs = s[:limit].execute()

        return docs

    def family_declarations(self, language=None, limit=12, return_full_body=False):
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
                    ],
                )
            )

        if subqs:
            s = s.query(reduce(or_, subqs)).query(~Q("term", _id=self.meta.id))

            if return_full_body:
                s = s.doc_type(NACPDeclaration, Declaration)
                docs = s[:limit].execute()

                if language is not None:
                    for d in docs:
                        d.prepare_translations(language, infocard_only=True)
            else:
                docs = s[:limit].execute()

            return docs
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
                getattr(self.general, "family_raw", "")
            ):
                if "family_name" in member:
                    yield member["family_name"]


declarations_idx = Index(OLD_DECLARATION_INDEX)
declarations_idx.settings(
    number_of_shards=NUMBER_OF_SHARDS, number_of_replicas=NUMBER_OF_REPLICAS
)
declarations_idx.analyzer(namesAutocompleteAnalyzer)
declarations_idx.analyzer(namesAutocompleteSearchAnalyzer)


@declarations_idx.doc_type
class Declaration(DocType, AbstractDeclaration):
    """Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""

    persons = Text(analyzer="ukrainian", copy_to="all")
    countries = Text(analyzer="ukrainian", copy_to="all")
    companies = Text(analyzer="ukrainian", copy_to="all")
    names_autocomplete = Text(
        analyzer="namesAutocompleteAnalyzer",
        search_analyzer="namesAutocompleteSearchAnalyzer",
        fields={"raw": Text(index=True)},
        term_vector="with_positions_offsets",
    )

    all = Text(analyzer="ukrainian")

    general = Object(
        properties={
            "full_name_suggest": Completion(preserve_separators=False),
            "full_name": Text(index=True, analyzer="ukrainian"),
            "full_name_for_sorting": Keyword(
                index=True, ignore_above=100
            ),  # only for sorting purposes
            "name": Text(index=True, analyzer="ukrainian"),
            "patronymic": Text(index=True, analyzer="ukrainian"),
            "last_name": Text(index=True, analyzer="ukrainian"),
            "family_raw": Text(index=True, analyzer="ukrainian"),
            "family": Nested(
                properties={
                    "name": Text(index=True, analyzer="ukrainian"),
                    "relations": Keyword(index=False),
                    "inn": Keyword(index=False),
                }
            ),
            "post_raw": Text(index=True, analyzer="ukrainian"),
            "post": Object(
                properties={
                    "region": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                    "office": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                    "post": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                }
            ),
            "addresses": Nested(
                properties={
                    "place": Text(index=False),
                    "place_hidden": Boolean(index=False),
                    "place_district": Text(index=False),
                    "place_district_hidden": Boolean(index=False),
                    "place_city": Text(index=False),
                    "place_city_hidden": Boolean(index=False),
                    "place_city_type": Keyword(index=False),
                    "place_city_type_hidden": Boolean(index=False),
                    "place_address": Text(index=False),
                    "place_address_hidden": Boolean(index=False),
                    "place_address_type": Keyword(index=False),
                }
            ),
        }
    )
    declaration = Object(
        properties={
            "date": NoneAwareDate(),
            "notfull": Boolean(index=False),
            "notfull_lostpages": Keyword(index=False),
            "additional_info": Boolean(index=False),
            "additional_info_text": Text(index=False),
            "needs_scancopy_check": Boolean(index=False),
        }
    )
    intro = Object(
        properties={
            "declaration_year": Keyword(index=True),
            "doc_type": Keyword(index=True),
            "date": NoneAwareDate(index=True),
        }
    )
    ft_src = Text(index=True, analyzer="ukrainian", copy_to="all")

    # concatinated from set of fields for regular search (not deepsearch mode)
    index_card = Text(index=True, analyzer="ukrainian")

    INDEX_CARD_FIELDS = [
        "general.last_name",
        "general.name",
        "general.patronymic",
        "general.full_name",
        "general.post.post",
        "general.post.office",
        "general.post.region",
        "general.post.actual_region",
        "intro.declaration_year",
        "intro.doc_type",
        "declaration.source",
        "declaration.url",
    ]

    CONTENT_SELECTORS = PAPER_SELECTORS_TO_TRANSLATE

    INCOME_SINGLE_PROPERTIES = {
        "value": Keyword(index=False),
        "value_unclear": Boolean(index=False),
        "comment": Text(index=False),
        "family": Keyword(index=False),
        "family_unclear": Boolean(index=False),
        "family_comment": Text(index=False),
    }
    INCOME_LIST_PROPERTIES = {
        "country": Keyword(index=False),
        "country_comment": Text(index=False),
        "cur": Keyword(index=False),
        "cur_units": Keyword(index=False),
        "uah_equal": Keyword(index=False),
    }
    income = Object(
        properties={
            "5": Object(properties=INCOME_SINGLE_PROPERTIES),
            "6": Object(properties=INCOME_SINGLE_PROPERTIES),
            "7": Object(properties=INCOME_SINGLE_PROPERTIES),
            "8": Object(properties=INCOME_SINGLE_PROPERTIES),
            "9": Object(properties=INCOME_SINGLE_PROPERTIES),
            "10": Object(properties=INCOME_SINGLE_PROPERTIES),
            "11": Object(properties=INCOME_SINGLE_PROPERTIES),
            "12": Object(properties=INCOME_SINGLE_PROPERTIES),
            "13": Object(properties=INCOME_SINGLE_PROPERTIES),
            "14": Object(properties=INCOME_SINGLE_PROPERTIES),
            "15": Object(properties=INCOME_SINGLE_PROPERTIES),
            "16": Object(properties=INCOME_SINGLE_PROPERTIES),
            "17": Object(properties=INCOME_SINGLE_PROPERTIES),
            "18": Object(properties=INCOME_SINGLE_PROPERTIES),
            "19": Object(properties=INCOME_SINGLE_PROPERTIES),
            "20": Object(properties=INCOME_SINGLE_PROPERTIES),
            "21": Nested(properties=INCOME_LIST_PROPERTIES),
            "22": Nested(properties=INCOME_LIST_PROPERTIES),
        }
    )

    ESTATE_PROPERTIES = {
        "region": Text(index=False),
        "address": Text(index=False),
        "space": Keyword(index=False),
        "space_units": Keyword(index=False),
        "space_comment": Text(index=False),
        "costs": Keyword(index=False),
        "costs_comment": Text(index=False),
        "costs_rent": Keyword(index=False),
        "costs_rent_comment": Text(index=False),
        "costs_property": Keyword(index=False),
        "costs_property_comment": Text(index=False),
    }
    estate = Object(
        properties={
            "23": Nested(properties=ESTATE_PROPERTIES),
            "24": Nested(properties=ESTATE_PROPERTIES),
            "25": Nested(properties=ESTATE_PROPERTIES),
            "26": Nested(properties=ESTATE_PROPERTIES),
            "27": Nested(properties=ESTATE_PROPERTIES),
            "28": Nested(properties=ESTATE_PROPERTIES),
            "29": Nested(properties=ESTATE_PROPERTIES),
            "30": Nested(properties=ESTATE_PROPERTIES),
            "31": Nested(properties=ESTATE_PROPERTIES),
            "32": Nested(properties=ESTATE_PROPERTIES),
            "33": Nested(properties=ESTATE_PROPERTIES),
            "34": Nested(properties=ESTATE_PROPERTIES),
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
        "brand_info_unclear": Boolean(index=False),
    }
    vehicle = Object(
        properties={
            "35": Nested(properties=VEHICLE_PROPERTIES),
            "36": Nested(properties=VEHICLE_PROPERTIES),
            "37": Nested(properties=VEHICLE_PROPERTIES),
            "38": Nested(properties=VEHICLE_PROPERTIES),
            "39": Nested(properties=VEHICLE_PROPERTIES),
            "40": Nested(properties=VEHICLE_PROPERTIES),
            "41": Nested(properties=VEHICLE_PROPERTIES),
            "42": Nested(properties=VEHICLE_PROPERTIES),
            "43": Nested(properties=VEHICLE_PROPERTIES),
            "44": Nested(properties=VEHICLE_PROPERTIES),
        }
    )

    BANKS_PROPERTIES = {
        "sum": Keyword(index=False),
        "sum_hidden": Boolean(index=False),
        "sum_units": Keyword(index=False),
        "sum_comment": Text(index=False),
        "sum_foreign": Keyword(index=False),
        "sum_foreign_units": Keyword(index=False),
        "sum_foreign_comment": Text(index=False),
    }
    banks = Object(
        properties={
            "45": Nested(properties=BANKS_PROPERTIES),
            "46": Nested(properties=BANKS_PROPERTIES),
            "47": Nested(properties=BANKS_PROPERTIES),
            "48": Nested(properties=BANKS_PROPERTIES),
            "49": Nested(properties=BANKS_PROPERTIES),
            "50": Nested(properties=BANKS_PROPERTIES),
            "51": Nested(properties=BANKS_PROPERTIES),
            "52": Nested(properties=BANKS_PROPERTIES),
            "53": Nested(properties=BANKS_PROPERTIES),
        }
    )

    LIABILITIES_PROPERTIES = {
        "sum": Keyword(index=False),
        "sum_comment": Text(index=False),
        "sum_units": Keyword(index=False),
        "sum_foreign": Keyword(index=False),
        "sum_foreign_comment": Text(index=False),
    }
    liabilities = Object(
        properties={
            "54": Nested(properties=LIABILITIES_PROPERTIES),
            "55": Nested(properties=LIABILITIES_PROPERTIES),
            "56": Nested(properties=LIABILITIES_PROPERTIES),
            "57": Nested(properties=LIABILITIES_PROPERTIES),
            "58": Nested(properties=LIABILITIES_PROPERTIES),
            "59": Nested(properties=LIABILITIES_PROPERTIES),
            "60": Nested(properties=LIABILITIES_PROPERTIES),
            "61": Nested(properties=LIABILITIES_PROPERTIES),
            "62": Nested(properties=LIABILITIES_PROPERTIES),
            "63": Nested(properties=LIABILITIES_PROPERTIES),
            "64": Nested(properties=LIABILITIES_PROPERTIES),
        }
    )

    def raw_source(self):
        src = self.to_dict()
        return blacklist(src, ["ft_src", "index_card", "translator"])

    def infocard(self):
        return {
            "first_name": self.general.name,
            "patronymic": self.general.patronymic,
            "last_name": self.general.last_name,
            "office": self.general.post.office,
            "position": self.general.post.post,
            "source": getattr(self.declaration, "source", getattr(self, "source", "")),
            "id": self.meta.id,
            "url": settings.SITE_URL
            + reverse("details", kwargs={"declaration_id": self.meta.id}),
            "document_type": self.intro.doc_type,
            "is_corrected": False,
            "declaration_year": getattr(self.intro, "declaration_year"),
            "created_date": getattr(
                self.intro, "date", getattr(self.declaration, "date", "")
            ),
        }

    def related_entities(self):
        return {
            "people": {"family": list(self.get_family_members())},
            "documents": {"corrected": [], "originals": []},
            "companies": {"owned": [], "related": [], "all": []},
        }

    def unified_source(self):
        try:
            doc = self.to_dict()
            doc["id"] = self.meta.id
            converter = PaperToNACPConverter(doc)
            return converter.convert()
        except ConverterError:
            return None

    def _is_change_form(self):
        return False

    def aggregated_data(self):
        return self.aggregated

    # Temporary solution to provide enough aggregated data
    # to make it possible to compare old and new declarations
    # TODO: REPLACE ME
    @property
    def aggregated(self):
        if hasattr(self, "_aggregated"):
            return self._aggregated

        def to_float(doc, key):
            try:
                return float(str(getattr(doc, key, "0") or "0").replace(",", "."))
            except ValueError:
                return 0.

        def get_exchange_rate(year, curr):
            rates = {
                "2011": {"USD": 7.98, "EUR": 10.29, "RUB": 0.250},  # As on 2011/12/30
                "2012": {"USD": 7.99, "EUR": 10.53, "RUB": 0.263},  # As on 2012/12/29
                "2013": {"USD": 7.99, "EUR": 11.04, "RUB": 0.244},  # As on 2013/12/30
                "2014": {"USD": 15.76, "EUR": 19.23, "RUB": 0.303},  # As on 2014/12/29
                "2015": {"USD": 24.00, "EUR": 26.22, "RUB": 0.329},  # As on 2015/12/31
                "2016": {  # As on 2016/12/31
                    "USD": 27.1908,
                    "EUR": 28.4226,
                    "RUB": 0.4511,
                },
                "2017": {  # As on 2017/12/31
                    "USD": 28.0672,
                    "EUR": 33.4954,
                    "RUB": 0.4870,
                },
            }

            if year not in rates:
                return

            if curr not in rates[year]:
                return

            return rates[year][curr]

        def to_space(space):
            areas_koef = {"га": 10000, "cоток": 100, "соток": 100, "м²": 1}

            units = getattr(space, "space_units", "")

            return to_float(space, "space") * areas_koef.get(units, 1)

        resp = {
            "incomes.presents.all": 0,
            "incomes.family": 0,
            "incomes.declarant": 0,
            "assets.cash.total": 0,
            "assets.family": 0,
            "assets.declarant": 0,
            "incomes.total": 0,
            "assets.total": 0,
            "expenses.total": 0,
            "liabilities.total": 0,
            "estate.family_land": 0,
            "estate.declarant_land": 0,
            "estate.family_other": 0,
            "estate.declarant_other": 0,
            "vehicles.all_names": "",
        }

        if hasattr(self, "income"):
            resp["incomes.declarant"] = to_float(self.income["5"], "value")
            resp["incomes.family"] = to_float(self.income["5"], "family")
            resp["incomes.presents.all"] = to_float(
                self.income["11"], "value"
            ) + to_float(self.income["11"], "family")

            resp["incomes.total"] = resp["incomes.declarant"] + resp["incomes.family"]

        if hasattr(self, "liabilities"):
            for field in [
                "54",
                "55",
                "56",
                "57",
                "58",
                "59",
                "60",
                "61",
                "62",
                "63",
                "64",
            ]:
                if hasattr(self.liabilities, field):
                    resp["liabilities.total"] += to_float(
                        getattr(self.liabilities, field), "sum"
                    )

        if hasattr(self, "banks"):
            for d_key, k in (("45", "declarant"), ("51", "family")):
                for a in getattr(self.banks, d_key, []):
                    try:
                        currency = getattr(a, "sum_units", "UAH") or "UAH"
                        amount = to_float(a, "sum")
                        if currency == "грн":
                            currency = "UAH"

                        if currency != "UAH":
                            rate = get_exchange_rate(
                                str(self.intro.declaration_year), currency
                            )
                            if rate is None:
                                continue

                            amount *= rate

                        resp["assets.{}".format(k)] += amount
                    except ValueError:
                        continue

            resp["assets.total"] = resp["assets.family"] + resp["assets.declarant"]

        vehicles = []
        if hasattr(self, "vehicle"):
            for field in [
                "34",
                "35",
                "36",
                "37",
                "38",
                "39",
                "40",
                "41",
                "42",
                "43",
                "44",
            ]:
                car_infos = getattr(self.vehicle, field, [])
                for car_info in car_infos:
                    vehicles.append(
                        "{} {}".format(
                            car_info["brand"], car_info["brand_info"]
                        ).replace(";", "")
                    )

            resp["vehicles.all_names"] += ";".join(vehicles)

        if hasattr(self, "estate"):
            for d_key, k in (
                ("24", "declarant_other"),
                ("30", "family_other"),
                ("25", "declarant_other"),
                ("31", "family_other"),
                ("26", "declarant_other"),
                ("32", "family_other"),
                ("27", "declarant_other"),
                ("33", "family_other"),
                ("28", "declarant_other"),
                ("34", "family_other"),
            ):

                estate_infos = getattr(self.estate, d_key, [])

                for space in estate_infos:
                    resp["estate.{}".format(k)] += to_space(space)

            for d_key, k in (("23", "declarant_land"), ("29", "family_land")):

                estate_infos = getattr(self.estate, d_key, [])

                for space in estate_infos:
                    resp["estate.{}".format(k)] += to_space(space)

        self._aggregated = resp
        return resp


    def raw_html(self):
        doc = render_to_string("decl_form.jinja", {"declaration": self})

        return doc

    class Meta:
        pass
        # commenting it out for now to not to ruin existing index
        # doc_type = "paper_declaration_doctype"


nacp_declarations_idx = Index(NACP_DECLARATION_INDEX)
nacp_declarations_idx.settings(
    number_of_shards=NUMBER_OF_SHARDS, number_of_replicas=NUMBER_OF_REPLICAS
)

nacp_declarations_idx.analyzer(namesAutocompleteAnalyzer)
nacp_declarations_idx.analyzer(namesAutocompleteSearchAnalyzer)


@nacp_declarations_idx.doc_type
class NACPDeclaration(DocType, AbstractDeclaration):
    """NACP Declaration document.
    Assumes there's a dynamic mapping with all fields not indexed by default."""

    persons = Text(analyzer="ukrainian", copy_to="all")
    countries = Text(analyzer="ukrainian", copy_to="all")
    companies = Text(analyzer="ukrainian", copy_to="all")
    names_autocomplete = Text(
        analyzer="namesAutocompleteAnalyzer",
        search_analyzer="namesAutocompleteSearchAnalyzer",
        fields={"raw": Text(index=True)},
        term_vector="with_positions_offsets",
    )

    all = Text(analyzer="ukrainian")

    general = Object(
        properties={
            "full_name": Text(index=True, analyzer="ukrainian"),
            "full_name_for_sorting": Keyword(
                index=True, ignore_above=100
            ),  # only for sorting purposes
            "name": Text(index=True, analyzer="ukrainian"),
            "patronymic": Text(index=True, analyzer="ukrainian"),
            "last_name": Text(index=True, analyzer="ukrainian"),
            "post": Object(
                properties={
                    "actual_region": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                    "region": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                    "office": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                    "post_type": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                    "post": Text(
                        index=True,
                        analyzer="ukrainian",
                        fields={"raw": Keyword(index=True)},
                    ),
                }
            ),
        }
    )
    declaration = Object(properties={"date": NoneAwareDate()})
    estate = Object(
        properties={
            "region": Text(
                index=True, analyzer="ukrainian", fields={"raw": Keyword(index=True)}
            )
        }
    )
    intro = Object(
        properties={
            "declaration_year": Keyword(index=True),
            "declaration_year_to": NoneAwareDate(),
            "declaration_year_from": NoneAwareDate(),
            "doc_type": Keyword(index=True),
            "date": NoneAwareDate(index=True),
        }
    )

    ft_src = Text(index=True, analyzer="ukrainian", copy_to="all")
    nacp_orig = Object(include_in_all=False, enabled=False)

    # concatinated from set of fields for regular search (not deepsearch mode)
    index_card = Text(index=True, analyzer="ukrainian")

    INDEX_CARD_FIELDS = [
        "general.last_name",
        "general.name",
        "general.patronymic",
        "general.full_name",
        "general.post.post",
        "general.post.office",
        "general.post.region",
        "general.post.actual_region",
        "intro.declaration_year",
        "intro.doc_type",
        "declaration.source",
        "declaration.url",
    ]

    CONTENT_SELECTORS = NACP_SELECTORS_TO_TRANSLATE

    def raw_html(self):
        fname = os.path.join(
            settings.NACP_DECLARATIONS_PATH,
            self.meta.id[5:7],
            os.path.basename(self.declaration.basename) + ".html",
        )

        try:
            with open(fname, "r") as fp:
                d = fp.read()
        except FileNotFoundError:
            return "<h2>Вибачте, декларація тимчасово відсутня, але ми вже працюємо над вирішенням проблеми</h2>"

        m = re.search(r"<\/style>(.*)</body>", d)
        declaration_html = m.group(1)

        # OH LORD, THAT'S NOT WHAT I'VE BEEN TAUGHT IN UNIVERSITY
        doc = declaration_html.replace(
            "</div></div></div><header><h2>", "</div></div><header><h2>"
        )
        # MY ASS IS ON FIRE
        doc = re.sub(r"</table>\s*<header>", "</table></div><header>", doc)

        companies = self._all_companies()

        codes = [c.lstrip("0") for c in companies if c.isdigit() and 4 < len(c) < 9]

        for c in codes:
            if c:
                full_code = c.rjust(8, "0")
                doc = re.sub(
                    r"\b0*{}\b".format(c),
                    ' <a href="https://ring.org.ua/edr/uk/company/{}" target="_blank">{}</a>'.format(
                        full_code, full_code
                    ),
                    doc,
                )

        return doc

    af_paths = [
        jmespath.compile("step_7.*.emitent_ua_company_code"),
        jmespath.compile("step_7.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_8.*.corporate_rights_company_code"),
        jmespath.compile("step_8.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_9.*.beneficial_owner_company_code"),
    ]

    def _is_change_form(self):
        return self.intro.doc_type and self.intro.doc_type == "Форма змін"

    def _affiliated_companies(self, src=None):
        # For now
        if self._is_change_form():
            return []

        results = []
        if src is None:
            src = self.nacp_orig.to_dict()

        for path in self.af_paths:
            results += path.search(src) or []

        return set(filter(None, results))

    rl_paths = {
        "step_11": jmespath.compile("step_11.*"),
        "step_12": jmespath.compile("step_12.*"),
    }

    def _related_companies(self, src=None):
        # For now
        if self._is_change_form():
            return []

        results = []
        if src is None:
            src = self.nacp_orig.to_dict()

        for section in self.rl_paths["step_11"].search(src) or []:
            try:
                section = section or {}
                obj_type = section.get("objectType", "").lower()
                other_obj_type = section.get("otherObjectType", "").lower()

                if obj_type in INCOME_TYPES or other_obj_type in INCOME_TYPES:
                    results += [section.get("source_ua_company_code", "")]
            except AttributeError:
                pass

        for section in self.rl_paths["step_12"].search(src) or []:
            try:
                section = section or {}
                obj_type = section.get("objectType", "").lower()

                if obj_type in MONETARY_ASSETS_TYPES:
                    results += [section.get("organization_ua_company_code", "")]
            except AttributeError:
                pass

        return set(filter(None, results))

    ac_paths = [
        jmespath.compile("step_2.*.source_ua_company_code[]"),
        jmespath.compile("step_3.*.beneficial_owner_company_code[]"),
        jmespath.compile("step_3.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_4.*.addition_company_code[]"),
        jmespath.compile("step_4.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_4.undefined.rights[].*.ua_company_code[]"),
        jmespath.compile("step_5.*.emitent_ua_company_code[]"),
        jmespath.compile("step_5.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_6.*.corporate_rights_company_code[]"),
        jmespath.compile("step_6.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_10.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_11.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_11.*.rights[].*.ua_company_name[]"),
        jmespath.compile("step_12.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_13.*.emitent_ua_company_code[]"),
        jmespath.compile("step_13.*.emitent_ua_company_name[]"),
        jmespath.compile("step_13.*.guarantor[].*.guarantor_ua_company_code[]"),
        jmespath.compile(
            "step_13.*.guarantor_realty[].*.realty_rights_ua_company_code[]"
        ),
        jmespath.compile(
            "step_13.*.guarantor_realty[].*.realty_rights_ua_company_code[]"
        ),
        jmespath.compile("step_15.*.emitent_ua_company_code[]"),
        jmespath.compile("step_16.org.*.reestrCode[]"),
        jmespath.compile("step_16.part_org.*.reestrCode[]"),
        jmespath.compile("step_7.*.emitent_ua_company_code"),
        jmespath.compile("step_7.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_8.*.corporate_rights_company_code"),
        jmespath.compile("step_8.*.rights[].*.ua_company_code[]"),
        jmespath.compile("step_9.*.beneficial_owner_company_code"),
        jmespath.compile("step_11.*.source_ua_company_code"),
        jmespath.compile("step_12.*.organization_ua_company_code"),
    ]

    def _all_companies(self, src=None):
        # For now
        if self._is_change_form():
            return []

        results = []
        if src is None:
            src = self.nacp_orig.to_dict()

        for path in self.ac_paths:
            results += path.search(src) or []

        return set(filter(None, results))

    def related_companies(self, affiliated_only=True):
        """
        Prepares data to use with procurement dataset
        """
        src = self.nacp_orig.to_dict()

        res = self._affiliated_companies(src)
        if not affiliated_only:
            res += self._related_companies(src)

        res = filter(None, map(lambda x: x.strip().lstrip("0"), set(res)))

        return list(set(res) - BANK_EDRPOUS)

    def get_procurement_earnings_by_year(self, affiliated_only=True):
        # Safety valve against transactions with malformed dates
        next_year_dt = date(date.today().year + 1, 1, 1)

        return (
            Transactions.objects.select_related("seller")
            .filter(
                seller__code__in=self.related_companies(affiliated_only),
                date__lt=next_year_dt,
            )
            .annotate(year=ExtractYear("date"))
            .values("year")
            .annotate(count=Count("pk"), sum_uah=Sum("volume_uah"))
        )

    def get_procurement_earnings_by_company(self, affiliated_only=True):
        # Safety valve against transactions with malformed dates
        next_year_dt = date(date.today().year + 1, 1, 1)

        return (
            Transactions.objects.select_related("seller")
            .filter(
                seller__code__in=self.related_companies(affiliated_only),
                date__lt=next_year_dt,
            )
            .values("seller__code", "seller__pk", "seller__name")
            .annotate(count=Count("pk"), sum_uah=Sum("volume_uah"))
        )

    def infocard(self):
        return {
            "first_name": self.general.name,
            "patronymic": self.general.patronymic,
            "last_name": self.general.last_name,
            "office": self.general.post.office,
            "position": self.general.post.post,
            "source": self.declaration.source,
            "id": self.meta.id,
            "url": settings.SITE_URL
            + reverse("details", kwargs={"declaration_id": self.meta.id}),
            "document_type": self.intro.doc_type,
            "is_corrected": self.intro.corrected,
            "created_date": self.intro.date,
            "declaration_year": getattr(self.intro, "declaration_year"),
        }

    def raw_source(self):
        return {
            "url": "https://public-api.nazk.gov.ua/v1/declaration/%s"
            % self.meta.id.replace("nacp_", "")
        }

    def related_entities(self):
        src = self.nacp_orig.to_dict()
        owned_companies = self._affiliated_companies(src)
        related_companies = self._related_companies(src)
        all_companies = self._all_companies(src)

        return {
            "people": {"family": list(self.get_family_members())},
            "documents": {
                "corrected": list(getattr(self, "corrected_declarations", []) or []),
                "originals": list(getattr(self, "original_declarations", []) or []),
            },
            "companies": {
                "owned": list(owned_companies),
                "related": list(related_companies),
                "all": list(all_companies),
            },
        }

    def unified_source(self):
        return self.nacp_orig.to_dict()

    def aggregated_data(self):
        if hasattr(self, "aggregated"):
            return self.aggregated.to_dict()
        else:
            return {}

    class Meta:
        doc_type = "nacp_declaration_doctype"
