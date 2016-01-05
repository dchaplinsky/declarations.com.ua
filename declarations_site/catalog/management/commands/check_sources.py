import os.path
from django.core.management.base import BaseCommand
from urllib.parse import unquote, urlsplit
from catalog.elastic_models import Declaration


class Command(BaseCommand):
    help = 'Checks if we have all sources of the declarations'

    def add_arguments(self, parser):
        parser.add_argument('destination')

    def check_url(self, url, destination):
        path = unquote(urlsplit(url).path)
        return os.path.exists(path.replace("/static/", destination))

    def handle(self, *args, **options):
        all_decls = Declaration.search().query('match_all').scan()
        urls_in_list = []
        on_unshred_it = 0
        on_static = 0
        on_chesno = 0
        no_url_no_id = 0
        not_found = 0
        duplicates = 0

        for decl in all_decls:
            url = decl["declaration"]["url"]
            if not url:
                no_url_no_id += 1
                print(decl.meta.id)
                continue

            if url in urls_in_list:
                duplicates += 1
                print(url)
                continue

            if "unshred.it" in url.lower():
                on_unshred_it += 1
                if not self.check_url(url, options["destination"]):
                    print(url)
                    not_found += 1

            elif "static.declarations.com.ua" in url.lower():
                on_static += 1
                if not self.check_url(url, options["destination"]):
                    print(url)
                    not_found += 1
            else:
                on_chesno += 1

        print(on_unshred_it, on_static, on_chesno, no_url_no_id)
        print(not_found, duplicates)
