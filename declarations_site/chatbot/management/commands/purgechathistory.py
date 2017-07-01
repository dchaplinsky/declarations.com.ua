import logging
from datetime import timedelta
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
from django.db.models.deletion import Collector
from django.core.management.base import BaseCommand

from chatbot.models import ChatHistory


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Purge old chat history (default 30 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=30,
            help='Delete task reports older than N days (default 30)')
        parser.add_argument(
            '--force', action='store_true', default=False,
            help='Allow delete fresh then 7 days',
        )

    def handle(self, *args, **options):
        verbosity = int(options.get("verbosity", "1"))
        levels = (logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

        if "verbosity" in options:
            logging.basicConfig(format='%(message)s', level=levels[verbosity])

        if options['days'] < 7 and not options['force']:
            logger.error('Delete less than one week not allowed, try use --force')
            return

        if options['days'] < 1:
            logger.error('Delete less than one day not allowed at all')
            return

        start_date = timezone.now() - timedelta(days=options['days'])
        collector = Collector(using=DEFAULT_DB_ALIAS)

        logger.info("Purge old chat records since {}".format(start_date))

        for model in [ChatHistory]:
            qs = model.objects.filter(created__lt=start_date)
            logger.info("Delete {} records in {}".format(qs.count(), model._meta.db_table))
            collector.collect(qs)
            collector.delete()

        logger.info("Done purge old records.")
