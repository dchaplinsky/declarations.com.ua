import sys
import json
from copy import deepcopy
from csv import DictReader

template = {
    "intro": {
        "isnotdeclaration": "0. ЦЕ НЕ ДЕКЛАРАЦІЯ (почищено)",
        "declaration_year": "0. Це декларація за ____ рік? (почищено)"
    },
    "general": {
        "last_name": "1. П.І.Б (почищено)",
        "name": "",
        "surname": "",
        "inn": "ИНН",
        "addresses": [
            {
                "place": "2",
                "place_district": "Вінницький",
                "place_city": "Вінниця",
                "place_city_type": "city",
                "place_address": "вул Петренка",
                "place_address_type": "actual"
            }
        ],
        "post": {
            "region": "2",
            "office": "Апеляційний суд",
            "post": "Суддя"
        },
        "family": [
            {
                "relations": "spouse",
                "name": "Іванов В.В.",
                "inn": "",
                "inn_hidden": "on"
            },
            {
                "relations": "other",
                "relations_other": "Пасинок",
                "name": "Іванов О. О.",
                "inn": "",
                "inn_unclear": "on"
            }
        ]
    },
    "income": {
        "5": {
            "value": "ОБЩ: 5, Загальна сума сукупного доходу Декларанта",
            "comment": "",
            "family": "ОБЩ: 5, Загальна сума сукупного доходу Членів сім\"ї",
            "family_comment": ""
        },
        "6": {
            "value": "1000",
            "comment": "Тисяса",
            "family": "2000",
            "family_comment": "Дві тисячі"
        },
        "7": {
            "value": "3000",
            "comment": "Три тисячі",
            "family": "4000",
            "family_comment": "Чотири тисячі",
            "source_name": ""
        },
        "8": {
            "value": "0",
            "comment": "Нуль гривень",
            "family": "10"
        },
        "9": {
            "value": "20",
            "comment": "двадцять гривень",
            "family": "30"
        },
        "10": {
            "value": "40",
            "comment": "сорок гривень",
            "family": "50"
        },
        "11": {
            "value": "60",
            "comment": "шістдесят гривень",
            "family": "70"
        },
        "12": {
            "value": "80",
            "comment": "вісімдесят",
            "family": "90"
        },
        "13": {
            "value": "100",
            "comment": "сто гривень",
            "family": "110"
        },
        "14": {
            "value": "120",
            "comment": "сто двадцять гривень",
            "family": "130"
        },
        "15": {
            "value": "140",
            "comment": "140 гривень",
            "family": "150"
        },
        "16": {
            "value": "160",
            "comment": "160 гривень",
            "family": "170"
        },
        "17": {
            "value": "180",
            "comment": "180 гривень",
            "family": "190"
        },
        "18": {
            "value": "200",
            "comment": "200 гривень",
            "family": "210"
        },
        "19": {
            "value": "220",
            "comment": "220 гривень ",
            "family": "230"
        },
        "20": {
            "value": "240",
            "comment": "240 гривень",
            "family": "250"
        },
        "21": [
            {
                "country": "Країна 2",
                "country_comment": "Коментар 2",
                "cur": "20000",
                "uah_equal": "200000"
            },
            {
                "country": "Країна 1",
                "country_comment": "Коментар 1",
                "cur": "30000",
                "uah_equal": "300000"
            }
        ],
        "22": [
            {
                "country": "Країна 4",
                "country_comment": "Коментар 4",
                "cur": "2000",
                "uah_equal": "20000"
            },
            {
                "country": "Країна 3",
                "country_comment": "Коментар 3",
                "cur": "1000",
                "uah_equal": "10000"
            }
        ],
        "8_family": {
            "comment": "Десять гривень"
        },
        "9_family": {
            "comment": "тридцять гривень"
        },
        "10_family": {
            "comment": "п'ятдесят"
        },
        "11_family": {
            "comment": "сімдесят гривень"
        },
        "12_family": {
            "comment": "дев'яносто гривень"
        },
        "13_family": {
            "comment": "сто десять гривень"
        },
        "14_family": {
            "comment": "сто тридцять гривень"
        },
        "15_family": {
            "comment": "150 гривень"
        },
        "16_family": {
            "comment": "170 гривень"
        },
        "17_family": {
            "comment": "190 гривень"
        },
        "18_family": {
            "comment": "210 гривень"
        },
        "19_family": {
            "comment": "230 гривень"
        },
        "20_family": {
            "comment": "250 гривень"
        }
    }
}


def recur_map(f, data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = f(v)
            elif isinstance(v, (list, dict)):
                data[k] = recur_map(f, data[k])

    if isinstance(data, list):
        for k, v in enumerate(data):
            if isinstance(v, str):
                data[k] = f(v)
            elif isinstance(v, (list, dict)):
                data[k] = recur_map(f, data[k])

    return data


def convert_line(l):
    out = deepcopy(template)

    out = recur_map(lambda v: l.get(v, ""), out)

    return out

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit("not enough args")

    with open(sys.argv[1], "r", encoding='cp1251') as fp:
        dr = DictReader(fp, delimiter=";")

        res = []
        for l in dr:
            res.append(convert_line(l))
            break

        print(json.dumps(res, ensure_ascii=False, indent="  "))
