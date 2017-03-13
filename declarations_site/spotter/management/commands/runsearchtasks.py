import logging
from django.core.management.base import BaseCommand

from spotter.models import SearchTask
from spotter.utils import do_search, create_report, create_notify


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run registered search tasks and send notifications'

    def handle(self, *args, **options):
        verbosity = int(options.get("verbosity", "1"))
        levels = (logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

        if "verbosity" in options:
            logging.basicConfig(format='%(message)s', level=levels[verbosity])

        for task in SearchTask.objects.filter(is_enabled=True, is_deleted=False):
            try:
                self.run_search_task(task)
            except Exception as e:
                logger.exception("run_search_task(%d) %s", task.id, str(e))

    def run_search_task(self, task):
        logger.info("Process %s %s", task.user, task.query)
        search = do_search(task)
        report = create_report(task, search)
        logger.info("Found %d new %d", report.found_total, report.found_new)
        if report.found_new:
            notify = create_notify(task, report)
            logger.info("Send notify %s %s", notify.email, notify.error)
