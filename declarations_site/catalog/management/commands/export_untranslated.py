import os.path
import json
import fnmatch
import argparse
from pickle import dump
from collections import Counter
from itertools import chain
from multiprocessing import Pool

import glob2
import tqdm
import jmespath
from pyquery import PyQuery as pq
from elasticsearch_dsl.connections import connections

from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.constants import OLD_DECLARATION_INDEX, NACP_SELECTORS_TO_TRANSLATE
from catalog.elastic_models import Declaration, NACPDeclaration
from catalog.utils import grouper
from catalog.models import Translation
from catalog.translator import HTMLTranslator, Translator


class Command(BaseCommand):
    help = "Go through e-declarations and paper based declarations to extract chunks that aren't yet translated"

    def add_arguments(self, parser):
        parser.add_argument("outfile", type=argparse.FileType("wb"))

    @classmethod
    def extract_terms_to_translate(cls, decls):
        unseen = Counter()
        for decl in decls:
            if decl is None:
                continue

            names_to_ignore = set(
                chain.from_iterable(
                    map(lambda x: x.split(" "), decl.names_autocomplete or [])
                )
            ) | set(decl.names_autocomplete or [])

            trans = HTMLTranslator(
                decl.raw_html(), NACP_SELECTORS_TO_TRANSLATE, do_not_fetch_dicts=True,
                store_unseen=True
            )
            trans.get_translated_html(do_not_translate=names_to_ignore)

            unseen.update(
                {
                    k: v
                    for k, v in trans.unseen.items()
                    if not k.strip().endswith("/ Україна")
                }
            )

        return len(decls), unseen

    def handle(self, *args, **options):
        globally_unseen = Counter()

        all_e_decls = NACPDeclaration.search().scan()

        with tqdm.tqdm() as pbar:
            totally_unseen = Counter()

            with Pool(8) as pool:
                results = pool.imap(Command.extract_terms_to_translate, grouper(all_e_decls, 200))

                for cnt, unseen in results:
                    globally_unseen.update(unseen)
                    pbar.update(cnt)

        existing_translations = frozenset(
            Translation.objects.values_list("term_id", flat=True).distinct()
        )

        filtered_unseen = Counter()
        for k, v in globally_unseen.items():
            if (
                Translator.get_id(k) not in existing_translations
                and Translator.get_loose_id(k) not in existing_translations
            ):
                filtered_unseen[k] = v

        dump(filtered_unseen, options["outfile"])
