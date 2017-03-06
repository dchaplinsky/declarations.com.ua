from django.core.management.base import BaseCommand

from spotter.models import SearchTask
from spotter.utils import do_search, create_report, create_notify


class Command(BaseCommand):
    help = 'Run registered seaech tasks and send notifications'

    def handle(self, *args, **options):
        for task in SearchTask.objects.filter(is_enabled=True, is_deleted=False):
            self.run_search_task(task)

    def run_search_task(self, task):
        print("Process %s %s" % (task.user, task.query))
        search = do_search(task)
        report = create_report(task, search)
        print("  Total %d new %d" % (report.found_total, report.found_new))
        if report.found_new:
            notify = create_notify(task, report)
            print("  Send notify to", notify.email, notify.status)
