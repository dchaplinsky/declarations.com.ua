import os.path
import re
from csv import reader
from itertools import islice
from html import unescape

from django.core.management.base import BaseCommand

from tqdm import tqdm

from catalog.translator import Translator
from catalog.models import Translation


class Command(BaseCommand):
    help = "Load dictionaries in CSV and load them into DB"

    def handle(self, *args, **options):
        DICTIONARY = Translator()

        CURR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        DICT_DIR = os.path.join(CURR_DIR, "data/dictionaries/")

        DICTIONARY.load_dict_from_csv(
            os.path.join(DICT_DIR, "decl_translations.csv"), "t", 10
        )
        DICTIONARY.load_dict_from_csv(
            os.path.join(DICT_DIR, "pep_translations.csv"), "p", 9
        )
        DICTIONARY.load_dict_from_csv(
            os.path.join(DICT_DIR, "google_dictionary.csv"), "g", 3
        )

        Translation.objects.all().delete()

        with tqdm(total=len(DICTIONARY.inner_dict)) as pbar:
            batch_size = 500
            objs = (
                Translation(
                    term_id=k,
                    term=v["term"],
                    translation=unescape(v["translation"]),
                    source=v["source"],
                    quality=v["quality"],
                    strict_id=v["strict_id"],
                )
                for k, v in DICTIONARY.inner_dict.items()
            )

            while True:
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                Translation.objects.bulk_create(batch, batch_size)
                pbar.update(len(batch))
