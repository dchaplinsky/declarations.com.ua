# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from django.db import migrations


def load_regions(apps, schema_editor):
    Region = apps.get_model("catalog", "Region")

    with open("catalog/migrations/regions.csv", "r") as fp:
        r = csv.reader(fp)

        for i, l in enumerate(r):
            Region.objects.update_or_create(
                region_name=l[0],
                order_id=i
            )


def load_offices(apps, schema_editor):
    from catalog.models import Office

    root = Office.add_root(name='Україна', order_id=0)
    get = lambda node: Office.objects.get(pk=node.pk)

    with open("catalog/migrations/offices.csv", "r") as fp:
        r = csv.reader(fp)

        prev_filled_row = -1
        levels = {}
        for i, l, in enumerate(r):
            if not any(l):
                continue

            filled_row = None

            for j, r in enumerate(l):
                if r:
                    prev_filled_row = filled_row
                    filled_row = j
                    break

            if prev_filled_row is not None and filled_row is not None:
                if filled_row > prev_filled_row:
                    if filled_row != prev_filled_row + 1:
                        print(l)

            if filled_row == 0:
                levels[filled_row] = get(root).add_child(
                    name=l[filled_row], order_id=i + 1)
            else:
                levels[filled_row] = get(levels[filled_row - 1]).add_child(
                    name=l[filled_row], order_id=i + 1)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_regions),
        migrations.RunPython(load_offices),
    ]
