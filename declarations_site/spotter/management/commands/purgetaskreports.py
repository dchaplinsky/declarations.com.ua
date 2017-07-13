import logging
from datetime import timedelta
from django.db import DEFAULT_DB_ALIAS, connection
from django.utils import timezone
from django.db.models.deletion import Collector
from django.core.management.base import BaseCommand

from spotter.models import TaskReport, NotifySend


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Purge old task reports (default 30 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=30,
            help='Delete task reports older than N days (default 30)')
        parser.add_argument(
            '--force', action='store_true', default=False,
            help='Allow delete fresher than 7 days',
        )
        parser.add_argument(
            '--vacuum', action='store_true', default=False,
            help='Run VACUUM command after delete',
        )
        parser.add_argument(
            '--full', action='store_true', default=False,
            help='Only with --vacuum run VACUUM FULL command',
        )

    def handle(self, *args, **options):
        verbosity = int(options.get("verbosity", "1"))
        levels = (logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

        if "verbosity" in options:
            logging.basicConfig(format='%(message)s', level=levels[verbosity])

        if options['days'] < 7 and not options['force']:
            logger.error('Delete less than one week not allowed, try using --force')
            return

        if options['days'] < 1:
            logger.error('Delete less than one day not allowed at all')
            return

        start_date = timezone.now() - timedelta(days=options['days'])
        collector = Collector(using=DEFAULT_DB_ALIAS)

        logger.info("Purge old records since {}".format(start_date))

        for model in (NotifySend, TaskReport):
            qs = model.objects.filter(created__lt=start_date)
            logger.info("Delete {} records in {}".format(qs.count(), model._meta.db_table))
            collector.collect(qs)
            collector.delete()

        logger.info("Done purging old records.")

        if not options['vacuum']:
            return

        sql = "VACUUM"

        if options['full']:
            sql += " FULL"

        force_proxy = connection.cursor()
        realconn = connection.connection
        old_isolation_level = realconn.isolation_level
        realconn.set_isolation_level(0)
        cursor = realconn.cursor()

        for model in (NotifySend, TaskReport):
            sql_command = "{} {}".format(sql, model._meta.db_table)
            logger.info("Run {}".format(sql_command))
            cursor.execute(sql_command)

        realconn.set_isolation_level(old_isolation_level)
        del force_proxy
