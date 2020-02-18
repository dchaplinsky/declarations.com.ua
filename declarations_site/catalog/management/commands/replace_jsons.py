import re
import json
from csv import writer
from parsel import Selector
import os.path
import fnmatch
import glob2


from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update file storage with new jsons"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("repo_dir", default=settings.NACP_DECLARATIONS_PATH)
        parser.add_argument("input_dir")

    def replace_file(self, existing_json, updated_json):
        with open(updated_json, "r") as in_file:
            with open(existing_json, "w") as out_file:
                json.dump(
                    json.load(in_file),
                    out_file,
                    indent=4,
                    sort_keys=True,
                    ensure_ascii=False,
                )

    def get_submission_date(self, existing_json):
        with open(existing_json, "r") as in_file:
            try:
                doc = json.load(in_file)
                return doc.get("created_date")
            except json.decoder.JSONDecodeError as e:
                self.stderr.write("API brainfart in file {}".format(existing_json))
                return None

    def handle(self, *args, **options):
        self.stdout.write(
            "Gathering JSON documents from {}".format(options["repo_dir"])
        )

        existing_jsons = {}
        for root, _, filenames in os.walk(options["repo_dir"]):
            for filename in fnmatch.filter(filenames, "*.json"):
                base_fname = os.path.basename(filename)
                guid = base_fname[-36:]
                existing_jsons[guid] = os.path.join(root, filename)

        updated_jsons = {}
        for root, _, filenames in os.walk(options["input_dir"]):
            for filename in fnmatch.filter(filenames, "*.json"):
                base_fname = os.path.basename(filename)
                guid = base_fname[-36:]
                updated_jsons[guid] = os.path.join(root, filename)

        self.stdout.write(
            "Gathered {} JSON documents in repo, {} JSON documents in incoming dir".format(
                len(existing_jsons), len(updated_jsons)
            )
        )

        for x in updated_jsons:
            if x in existing_jsons:
                self.stdout.write(
                    "Replacing {} with {}".format(existing_jsons[x], updated_jsons[x])
                )
                self.replace_file(existing_jsons[x], updated_jsons[x])
            else:
                self.stderr.write(
                    "Cannot find {} file in repository".format(updated_jsons[x])
                )

        for x in existing_jsons:
            if x not in updated_jsons:
                self.stderr.write(
                    "Cannot find {} file, submitted on {} in updated jsons".format(
                        existing_jsons[x], self.get_submission_date(existing_jsons[x])
                    )
                )
