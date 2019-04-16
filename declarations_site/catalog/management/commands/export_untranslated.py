import re
import argparse
from pickle import dump, load
from collections import Counter
from multiprocessing import Pool
from itertools import chain, islice

import tqdm
from pyquery import PyQuery as pq
from elasticsearch_dsl import Search

from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.constants import CATALOG_INDICES, OLD_DECLARATION_INDEX
from catalog.elastic_models import Declaration, NACPDeclaration
from catalog.utils import grouper
from catalog.models import Translation
from catalog.translator import HTMLTranslator, Translator


class Command(BaseCommand):
    help = "Go through e-declarations and paper based declarations to extract chunks that aren't yet translated"

    def add_arguments(self, parser):
        parser.add_argument(
            "--concurrency",
            action="store",
            dest="concurrency",
            type=int,
            default=8,
            help="Run concurrently in N threads",
        )

        parser.add_argument(
            "--chunk_size",
            action="store",
            dest="chunk_size",
            type=int,
            default=500,
            help="Run concurrently in N threads",
        )

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
                decl.raw_html(),
                decl.CONTENT_SELECTORS,
                do_not_fetch_dicts=True,
                store_unseen=True,
            )
            trans.get_translated_html(do_not_translate=names_to_ignore)

            unseen.update(
                {
                    k: v
                    for k, v in trans.unseen.items()
                    if not k.strip().endswith("/ Україна")
                }
            )

        return len(decls), unseen, names_to_ignore

    def handle(self, *args, **options):
        Translation.objects.filter(source="u").delete()
        globally_unseen = Counter()

        all_decls = (
            Search(index=CATALOG_INDICES).doc_type(NACPDeclaration, Declaration).scan()
        )

        with tqdm.tqdm() as pbar:
            totally_unseen = Counter()
            names_to_ignore = set()

            with Pool(options["concurrency"]) as pool:
                results = pool.imap(
                    Command.extract_terms_to_translate,
                    grouper(all_decls, options["chunk_size"]),
                )

                for cnt, unseen, names in results:
                    globally_unseen.update(unseen)
                    names_to_ignore |= names
                    pbar.update(cnt)
                    pbar.write("{} items in unseen dict".format(len(globally_unseen)))

        pbar.write("{} items in names dict".format(len(names_to_ignore)))

        names_to_ignore = set(map(Translator.get_id, names_to_ignore))

        existing_translations = frozenset(
            Translation.objects.values_list("term_id", flat=True).distinct()
        ) | names_to_ignore
        pbar.write("{} items in db dict".format(len(existing_translations)))

        filtered_unseen = Counter()
        for k, v in globally_unseen.items():
            term_id = Translator.get_id(k)
            loose_id = Translator.get_loose_id(k)
            if (
                term_id not in existing_translations
                and loose_id not in existing_translations
            ):
                filtered_unseen[k] = v

        del existing_translations
        del globally_unseen

        tqdm.tqdm.write("{} items left after filtering".format(len(filtered_unseen)))

        batch_size = 500
        for batch in grouper(filter(lambda x: len(x) > 2, names_to_ignore), batch_size):
            Translation.objects.filter(term_id__in=batch, source__in=["u", "g"]).delete()

        objs = []
        seen = set()
        for k, v in tqdm.tqdm(filtered_unseen.most_common()):
            term_id = Translator.get_id(k)
            if not term_id or term_id in seen:
                continue

            seen.add(term_id)
            objs.append(
                Translation(
                    term_id=term_id,
                    term=k,
                    translation="",
                    source="u",
                    quality=0,
                    strict_id=True,
                    frequency=v,
                )
            )

        with tqdm.tqdm(total=len(objs)) as pbar:
            for batch in grouper(objs, batch_size):
                batch = list(filter(None, batch))

                Translation.objects.bulk_create(batch, batch_size)
                pbar.update(len(batch))
