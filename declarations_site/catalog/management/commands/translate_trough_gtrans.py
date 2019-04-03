import re
import argparse
from time import sleep

import tqdm

from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.utils import grouper
from catalog.models import Translation
from google.cloud import translate


class Command(BaseCommand):
    help = "Translate top N untranslated phrases from declarations through google translate"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=150000,
            help="Translate only `limit` popular phrases",
        )

        parser.add_argument(
            "gcloud_credentials",
            type=str,
            help="Google Cloud credentials to use google translate",
        )

    def handle(self, *args, **options):
        client = translate.Client.from_service_account_json(
            options["gcloud_credentials"]
        )

        for i, tasks in enumerate(
            grouper(
                tqdm.tqdm(
                    Translation.objects.filter(source="u")
                    .order_by("-frequency")[: options["limit"]]
                    .iterator()
                ),
                100,
            )
        ):
            translations = client.translate(
                [task.term for task in tasks if task is not None],
                target_language="en",
                source_language="uk",
            )

            for task, translation in zip(tasks, translations):
                task.translation = translation["translatedText"]
                task.source = "g"
                task.save()

            sleep(7)
