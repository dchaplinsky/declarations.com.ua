import logging
import argparse
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from spotter.utils import find_search_task, save_search_task


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create some tasks for monitoring and broadcasting'

    def add_arguments(self, parser):
        parser.add_argument(
            'list_of_queries', type=argparse.FileType('r'),
            help='File with queries',
        )

    def handle(self, *args, **options):
        verbosity = int(options.get("verbosity", "1"))
        levels = (logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

        if "verbosity" in options:
            logging.basicConfig(format='%(message)s', level=levels[verbosity])

        user, _ = User.objects.get_or_create(
            email=settings.BROADCASTER_USER,
            defaults={"username": "whistleblower"}
        )

        total = 0
        added = 0
        skipped = 0
        errors = 0
        for q in options["list_of_queries"]:
            q = q.strip()
            if not q:
                continue
            
            total += 1
            try:
                if not find_search_task(user, q):
                    save_search_task(user, q, deepsearch=False)
                    added += 1
                else:
                    skipped += 1
            except ValueError as e:
                logger.error(str(e))
                errors += 1

        logger.info("Total: {}, added: {}, already in db: {}, skipped due to error: {}".format(total, added, skipped, errors))