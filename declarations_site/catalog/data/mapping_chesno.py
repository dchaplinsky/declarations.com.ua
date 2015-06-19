from collections import namedtuple

SubDocument = namedtuple("SubDocument", ["path_prefix", "mapping"])
NumericOperation = namedtuple("NumericOperation", ["path_prefix", "field", "operation"])
JoinOperation = namedtuple("JoinOperation", ["paths", "separator"])

MAPPING = {
    "_id": "details/person_id",
    "intro": {
        "isnotdeclaration": "",
        "declaration_year": "details/year"
    },
    "general": {
        "full_name": "full_name",
        "last_name": "last_name",
        "name": "first_name",
        "patronymic": "second_name",

        "name_hidden": "",
        "name_unclear": "",
        "last_name_hidden": "",
        "last_name_unclear": "",
        "patronymic_hidden": "",
        "patronymic_unclear": "",

        "inn": "",
        "addresses": [
            {
                "place": "",
                "place_district": "",
                "place_city": "",
                "place_city_type": "",
                "place_address": "",
                "place_address_type": ""
            }
        ],
        "addresses_raw": "",
        "addresses_raw_hidden": "",
        "post": {
            "region": "",
            "office": "",
            "post": ""
        },
        "post_raw": "office/position",

        "family": SubDocument(
            "details/fields/4.0/items",
            {
                "relations": "",
                "family_name": "family_member",
                "inn": ""
            }
        ),
        "family_raw": ""
    },

    "income": {
        "5": {
            "value": "details/fields/5.0/items/0/value",
            "comment": "",
            "family": "details/fields/5.1/items/0/value",
            "family_comment": ""
        },
        "6": {
            "value": "details/fields/6.0/items/0/value",
            "comment": "",
            "family": "details/fields/6.1/items/0/value",
            "family_comment": ""
        },
        "7": {
            "value": "details/fields/7.0/items/0/value",
            "comment": "",
            "family": "details/fields/7.1/items/0/value",
            "family_comment": "",
            "source_name": "details/fields/7.0/items/0/comment"
        },
        "8": {
            "value": "details/fields/8.0/items/0/value",
            "comment": "",
            "family": "details/fields/8.1/items/0/value",
            "family_comment": ""
        },
        "9": {
            "value": "details/fields/9.0/items/0/value",
            "comment": "",
            "family": "details/fields/9.1/items/0/value",
            "family_comment": ""
        },
        "10": {
            "value": "details/fields/10.0/items/0/value",
            "comment": "",
            "family": "details/fields/10.1/items/0/value",
            "family_comment": ""
        },
        "11": {
            "value": "details/fields/11.0/items/0/value",
            "comment": "",
            "family": "details/fields/11.1/items/0/value",
            "family_comment": ""
        },
        "12": {
            "value": "details/fields/12.0/items/0/value",
            "comment": "",
            "family": "details/fields/12.1/items/0/value",
            "family_comment": ""
        },
        "13": {
            "value": "details/fields/13.0/items/0/value",
            "comment": "",
            "family": "details/fields/13.1/items/0/value",
            "family_comment": ""
        },
        "14": {
            "value": "details/fields/14.0/items/0/value",
            "comment": "",
            "family": "details/fields/14.1/items/0/value",
            "family_comment": ""
        },
        "15": {
            "value": "details/fields/15.0/items/0/value",
            "comment": "",
            "family": "details/fields/15.1/items/0/value",
            "family_comment": ""
        },
        "16": {
            "value": "details/fields/16.0/items/0/value",
            "comment": "",
            "family": "details/fields/16.1/items/0/value",
            "family_comment": ""
        },
        "17": {
            "value": "details/fields/17.0/items/0/value",
            "comment": "",
            "family": "details/fields/17.1/items/0/value",
            "family_comment": ""
        },
        "18": {
            "value": "details/fields/18.0/items/0/value",
            "comment": "",
            "family": "details/fields/18.1/items/0/value",
            "family_comment": ""
        },
        "19": {
            "value": "details/fields/19.0/items/0/value",
            "comment": "",
            "family": "details/fields/19.1/items/0/value",
            "family_comment": ""
        },
        "20": {
            "value": "details/fields/20.0/items/0/value",
            "comment": "",
            "family": "details/fields/20.1/items/0/value",
            "family_comment": ""
        },
        "21": SubDocument(
            "details/fields/21.0/items",
            {
                "country": "",
                "country_comment": "",
                "cur": "",
                "uah_equal": "value"
            }
        ),
        "22": SubDocument(
            "details/fields/22.0/items",
            {
                "country": "",
                "country_comment": "",
                "cur": "",
                "uah_equal": "value"
            }
        )
    },
    "estate": {
        "23": SubDocument(
            "details/fields/23.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs": "purchase",
                "costs_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "24": SubDocument(
            "details/fields/24.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs": "purchase",
                "costs_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "25": SubDocument(
            "details/fields/25.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs": "purchase",
                "costs_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "26": SubDocument(
            "details/fields/26.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs": "purchase",
                "costs_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "27": SubDocument(
            "details/fields/27.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs": "purchase",
                "costs_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "28": SubDocument(
            "details/fields/28.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs": "purchase",
                "costs_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "29": SubDocument(
            "details/fields/29.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs_property": "purchase",
                "costs_property_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "30": SubDocument(
            "details/fields/30.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs_property": "purchase",
                "costs_property_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "31": SubDocument(
            "details/fields/31.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs_property": "purchase",
                "costs_property_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "32": SubDocument(
            "details/fields/32.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs_property": "purchase",
                "costs_property_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "33": SubDocument(
            "details/fields/33.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs_property": "purchase",
                "costs_property_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        ),
        "34": SubDocument(
            "details/fields/34.0/items",
            {
                "location_raw": "comment",
                "region": "",
                "address": "",
                "space": "value",
                "space_units": "",
                "space_comment": "",
                "costs_property": "purchase",
                "costs_property_comment": "",
                "costs_rent": "rent",
                "costs_rent_comment": ""
            }
        )
    },
    "vehicle": {
        "35": SubDocument(
            "details/fields/35.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "36": SubDocument(
            "details/fields/36.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "37": SubDocument(
            "details/fields/37.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "38": SubDocument(
            "details/fields/38.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "39": SubDocument(
            "details/fields/39.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "40": SubDocument(
            "details/fields/40.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "41": SubDocument(
            "details/fields/41.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "42": SubDocument(
            "details/fields/42.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "43": SubDocument(
            "details/fields/43.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        ),
        "44": SubDocument(
            "details/fields/44.0/items",
            {
                "brand": JoinOperation(("mark", "model", "description"), ' '),
                "brand_info": "",
                "year": "year",
                "sum": "purchase",
                "sum_comment": "",
                "sum_rent": "rent",
                "sum_rent_comment": "",
                "brand_hidden": ""
            }
        )
    },
    "banks": {
        "45": [{
            "sum": NumericOperation("details/fields/45.0/items", "value", sum),
            "sum_units": "details/fields/45.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/45.1/items", "value", sum),
            "sum_foreign_units": "details/fields/45.1/units",
            "sum_foreign_comment": ""
        }],
        "46": [{
            "sum": NumericOperation("details/fields/46.0/items", "value", sum),
            "sum_units": "details/fields/46.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/46.1/items", "value", sum),
            "sum_foreign_units": "details/fields/46.1/units",
            "sum_foreign_comment": ""
        }],
        "47": [{
            "sum": NumericOperation("details/fields/47.0/items", "value", sum),
            "sum_units": "details/fields/47.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/47.1/items", "value", sum),
            "sum_foreign_units": "details/fields/47.1/units",
            "sum_foreign_comment": ""
        }],
        "48": [{
            "sum": NumericOperation("details/fields/48.0/items", "value", sum),
            "sum_units": "details/fields/48.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/48.1/items", "value", sum),
            "sum_foreign_units": "details/fields/48.1/units",
            "sum_foreign_comment": ""
        }],
        "49": [{
            "sum": NumericOperation("details/fields/49.0/items", "value", sum),
            "sum_units": "details/fields/49.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/49.1/items", "value", sum),
            "sum_foreign_units": "details/fields/49.1/units",
            "sum_foreign_comment": ""
        }],
        "50": [{
            "sum": NumericOperation("details/fields/50.0/items", "value", sum),
            "sum_units": "details/fields/50.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/50.1/items", "value", sum),
            "sum_foreign_units": "details/fields/50.1/units",
            "sum_foreign_comment": ""
        }],
        "51": [{
            "sum": NumericOperation("details/fields/51.0/items", "value", sum),
            "sum_units": "details/fields/51.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/51.1/items", "value", sum),
            "sum_foreign_units": "details/fields/51.1/units",
            "sum_foreign_comment": ""
        }],
        "52": [{
            "sum": NumericOperation("details/fields/52.0/items", "value", sum),
            "sum_units": "details/fields/52.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/52.1/items", "value", sum),
            "sum_foreign_units": "details/fields/52.1/units",
            "sum_foreign_comment": ""
        }],
        "53": [{
            "sum": NumericOperation("details/fields/53.0/items", "value", sum),
            "sum_units": "details/fields/53.0/units",
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/53.1/items", "value", sum),
            "sum_foreign_units": "details/fields/53.1/units",
            "sum_foreign_comment": ""
        }]
    },
    "liabilities": {
        "54": {
            "sum": NumericOperation("details/fields/54.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/54.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "55": {
            "sum": NumericOperation("details/fields/55.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/55.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "56": {
            "sum": NumericOperation("details/fields/56.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/56.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "57": {
            "sum": NumericOperation("details/fields/57.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/57.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "58": {
            "sum": NumericOperation("details/fields/58.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/58.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "59": {
            "sum": NumericOperation("details/fields/59.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/59.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "60": {
            "sum": NumericOperation("details/fields/60.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/60.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "61": {
            "sum": NumericOperation("details/fields/61.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/61.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "62": {
            "sum": NumericOperation("details/fields/62.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/62.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "63": {
            "sum": NumericOperation("details/fields/63.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/63.1/items", "value", sum),
            "sum_foreign_comment": ""
        },
        "64": {
            "sum": NumericOperation("details/fields/64.0/items", "value", sum),
            "sum_comment": "",
            "sum_foreign": NumericOperation("details/fields/64.1/items", "value", sum),
            "sum_foreign_comment": ""
        }
    },
    "declaration": {
        "date": "",
        "notfull": "",
        "notfull_lostpages": "",
        "additional_info": "details/comment",
        "additional_info_text": "details/comment",
        "needs_scancopy_check": "",
        "url": "details/url",
        "link": "details/link",
        "source": "%CHESNO%"
    }
}
