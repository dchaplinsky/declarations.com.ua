from collections import namedtuple

SubDocument = namedtuple("SubDocument", ["path_prefix", "mapping"])

MAPPING = {
    "_id": "id",
    "intro": {
        "isnotdeclaration": "",
        "declaration_year": "year"
    },
    "general": {
        "full_name": "full_name",
        "last_name": "",
        "name": "",
        "patronymic": "",

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
            "region": "region",
            "office": "office",
            "post": "position"
        },
        "post_raw": "",

        "family": SubDocument(
            "fields/4.0/items",
            {
                "relations": "",
                "name": "family_member",
                "inn": ""
            }
        ),
        "family_raw": ""
    },

    "income": {
        "5": {
            "value": "fields/5.0/items/0/value",
            "comment": "",
            "family": "fields/5.1/items/0/value",
            "family_comment": ""
        },
        "6": {
            "value": "fields/6.0/items/0/value",
            "comment": "",
            "family": "fields/6.1/items/0/value",
            "family_comment": ""
        },
        "7": {
            "value": "fields/7.0/items/0/value",
            "comment": "",
            "family": "fields/7.1/items/0/value",
            "family_comment": "",
            "source_name": "fields/7.0/items/0/comment"
        },
        "8": {
            "value": "fields/8.0/items/0/value",
            "comment": "",
            "family": "fields/8.1/items/0/value",
            "family_comment": ""
        },
        "9": {
            "value": "fields/9.0/items/0/value",
            "comment": "",
            "family": "fields/9.1/items/0/value",
            "family_comment": ""
        },
        "10": {
            "value": "fields/10.0/items/0/value",
            "comment": "",
            "family": "fields/10.1/items/0/value",
            "family_comment": ""
        },
        "11": {
            "value": "fields/11.0/items/0/value",
            "comment": "",
            "family": "fields/11.1/items/0/value",
            "family_comment": ""
        },
        "12": {
            "value": "fields/12.0/items/0/value",
            "comment": "",
            "family": "fields/12.1/items/0/value",
            "family_comment": ""
        },
        "13": {
            "value": "fields/13.0/items/0/value",
            "comment": "",
            "family": "fields/13.1/items/0/value",
            "family_comment": ""
        },
        "14": {
            "value": "fields/14.0/items/0/value",
            "comment": "",
            "family": "fields/14.1/items/0/value",
            "family_comment": ""
        },
        "15": {
            "value": "fields/15.0/items/0/value",
            "comment": "",
            "family": "fields/15.1/items/0/value",
            "family_comment": ""
        },
        "16": {
            "value": "fields/16.0/items/0/value",
            "comment": "",
            "family": "fields/16.1/items/0/value",
            "family_comment": ""
        },
        "17": {
            "value": "fields/17.0/items/0/value",
            "comment": "",
            "family": "fields/17.1/items/0/value",
            "family_comment": ""
        },
        "18": {
            "value": "fields/18.0/items/0/value",
            "comment": "",
            "family": "fields/18.1/items/0/value",
            "family_comment": ""
        },
        "19": {
            "value": "fields/19.0/items/0/value",
            "comment": "",
            "family": "fields/19.1/items/0/value",
            "family_comment": ""
        },
        "20": {
            "value": "fields/20.0/items/0/value",
            "comment": "",
            "family": "fields/20.1/items/0/value",
            "family_comment": ""
        },
        "21": SubDocument(
            "fields/21.0/items",
            {
                "country": "",
                "country_comment": "",
                "cur": "",
                "uah_equal": "value"
            }
        ),
        "22": SubDocument(
            "fields/22.0/items",
            {
                "country": "",
                "country_comment": "",
                "cur": "",
                "uah_equal": "value"
            }
        )
    },
    "declaration": {
        "date": "",
        "notfull": "",
        "notfull_lostpages": "",
        "additional_info": "comment",
        "additional_info_text": "comment",
        "needs_scancopy_check": "",
        "url": "url",
        "source": "%CHESNO%"
    }
}
