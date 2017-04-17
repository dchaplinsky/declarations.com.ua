import logging
from django.core.management.base import BaseCommand

from spotter.models import SearchTask, TaskReport
from spotter.utils import first_run


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reset spotter tasks with more that 1K results'

    def handle(self, *args, **options):
        for task in SearchTask.objects.filter(is_enabled=True, is_deleted=False,
                                              found_total__gt=1000):
            try:
                task_reports = TaskReport.objects.filter(task=task.id)
                print('Task "{}" total found {} total reports {}'.format(
                    task.query, task.found_total, task_reports.count()))
                task_reports.delete()
                task.found_total = 0
                task.found_week = 0
                task.found_ids = []
                task.last_run = None
                first_run(task)
                task.save()
                print('\t-> new total found {}'.format(task.found_total))
            except Exception as e:
                print('Reset task "{}" failed: {}'.format(task.query, e))
