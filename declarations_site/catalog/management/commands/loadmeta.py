import csv

from django.core.management.base import BaseCommand, CommandError
from cms_pages.models import MetaData


class Command(BaseCommand):
    args = '<file_path>'
    help = ('Loads the CSV file with titles/meta-description '
            'for regions and region/office landing pages')

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a CSV file')

        with open(file_path, 'r', encoding='utf-8') as source:
            reader = csv.DictReader(source, delimiter=",")

            res = [0, 0]

            for l in reader:
                if l["Регіон"] == "НЕМА":
                    l["Регіон"] = None

                if l["Відомство"] == "НЕМА":
                    l["Відомство"] = None

                _, created = MetaData.objects.update_or_create(
                    region_id=l["Регіон"],
                    office_id=l["Відомство"],
                    defaults={
                        "title": l["title"].strip(),
                        "description": l["meta-description"].strip()
                    }
                )

                res[created] += 1

            self.stdout.write(
                'Loaded {} new items and updated {} existing'.format(*res))
