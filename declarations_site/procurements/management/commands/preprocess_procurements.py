import os.path
from django.core.management.base import BaseCommand
from procurements.models import Sellers


class Command(BaseCommand):
    help = 'Cleans up some mess in procurement sellers'


    def handle(self, *args, **options):
        for s in Sellers.objects.all().iterator():
            if s.code:
                s.code = s.code.strip().lstrip("0")

            s.save()
