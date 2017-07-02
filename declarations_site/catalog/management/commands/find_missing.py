import re
import json
from csv import writer
from parsel import Selector
import os.path
import fnmatch
import glob2
from multiprocessing import Pool

from django.core.management.base import BaseCommand


def _parse_me(base_fname):
    json_fname = "{}.json".format(base_fname)
    html_fname = "{}.html".format(base_fname)

    base_fname = os.path.basename(base_fname)
    guid = base_fname[-36:]
    name = base_fname[:-36].replace("_", " ").strip()

    try:
        with open(json_fname, "r") as fp:
            data = json.load(fp)
        with open(html_fname, "r") as fp:
            raw_html = fp.read()
            html = Selector(raw_html)
    except ValueError:
        print(
            "File {} or it's HTML counterpart cannot be parsed".format(
                json_fname))
        return (name, guid)
    except FileNotFoundError:
        print(
            "File {} or it's HTML counterpart cannot be found".format(
                json_fname))
        return (name, guid)

    try:
        data = data["data"]
    except KeyError:
        print("API brainfart: {}, {}".format(guid, base_fname))
        return (name, guid)

    if "step_0" not in data:
        print("Bad header format: {}, {}".format(guid, base_fname))
        return (name, guid)

    return None


class Command(BaseCommand):
    number_of_processes = 8

    help = ('Checks the file storage for broken files')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('file_path')
        parser.add_argument('csv_out')

    def handle(self, *args, **options):
        base_dir = options['file_path']
        missing_files = options['csv_out']

        self.stdout.write("Gathering JSON documents from {}".format(base_dir))

        jsons = []
        for root, _, filenames in os.walk(base_dir):
            for filename in fnmatch.filter(filenames, '*.json'):
                jsons.append(os.path.join(root, filename))

        htmls = []
        for root, _, filenames in os.walk(base_dir):
            for filename in fnmatch.filter(filenames, '*.html'):
                htmls.append(os.path.join(root, filename))

        self.stdout.write("Gathered {} JSON documents, {} HTML documents".format(
            len(jsons), len(htmls)))

        docs_to_check = (
            set(j.replace(".json", "").lower() for j in jsons) |
            set(h.replace(".html", "").lower() for h in htmls)
        )

        my_tiny_pool = Pool(self.number_of_processes)

        result = list(
            filter(
                None,
                my_tiny_pool.map(_parse_me, docs_to_check)
            )
        )

        with open(missing_files, "w") as fp:
            w = writer(fp)

            for r in result:
                w.writerow(r)

        self.stdout.write(
            'Found {} inconsistent or broken items'.format(len(result)))
