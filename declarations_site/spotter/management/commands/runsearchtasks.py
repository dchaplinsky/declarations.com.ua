import logging
from time import time
from threading import Lock, get_ident
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand

from spotter.models import SearchTask
from spotter.utils import do_search, create_report, create_notify


logger = logging.getLogger(__name__)


class DummyLock(object):
    """Dummy lock object for single thread mode"""

    def acquire(self):
        pass

    def release(self):
        pass


class Command(BaseCommand):
    help = 'Run registered search tasks and send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--concurrency', action='store',
            dest='concurrency', type=int, default=0,
            help='Run concurrently in N threads',
        )

    def handle(self, *args, **options):
        if 'verbosity' in options:
            verbosity = int(options['verbosity'])
            levels = (logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)
            logging.basicConfig(format='%(message)s', level=levels[verbosity])

        concurrency = int(options.get('concurrency', 0))
        self.lock = Lock() if concurrency else DummyLock()
        self.counters = {'success': 0, 'failed': 0, 'emails': 0}
        start_time = time()

        query = SearchTask.objects.filter(is_enabled=True, is_deleted=False, user__is_active=True)

        if concurrency:
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                executor.map(self.run_search_task, query)
        else:
            for task in query:
                self.run_search_task(task)

        self.counters['worktime'] = int(time() - start_time)
        logger.info("Total {success} success {failed} failed {emails} emails sent in {worktime} sec."
                    .format(**self.counters))

    def inc_counter(self, counter_name):
        self.lock.acquire()
        try:
            self.counters[counter_name] += 1
        finally:
            self.lock.release()

    def run_search_task(self, task):
        try:
            thread_id = get_ident()
            logger.info("Thread-%d Process %s %s", thread_id, task.user, task.query)
            search = do_search(task)
            report = create_report(task, search)
            logger.info("Thread-%d Found %d new %d", thread_id, report.found_total, report.found_new)
            if report.found_new:
                notify = create_notify(task, report)
                logger.info("Thread-%d Send notify %s %s", thread_id, notify.email, notify.error)
                self.inc_counter('emails')
            self.inc_counter('success')
        except Exception as e:
            logger.exception("Thread-%d run_search_task(%d) %s", thread_id, task.id, str(e))
            self.inc_counter('failed')
