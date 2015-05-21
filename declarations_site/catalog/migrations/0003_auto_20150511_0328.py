# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import csv


def delete_offices(apps, schema_editor):
    Office = apps.get_model("catalog", "Office")

    Office.objects.all().delete()


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
                    name=l[filled_row].strip(), order_id=i + 1)
            else:
                levels[filled_row] = get(levels[filled_row - 1]).add_child(
                    name=l[filled_row].strip(), order_id=i + 1)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20150504_2343'),
        # ('cms_pages', '0009_auto_20150511_0339'),
    ]

    operations = [
        migrations.RunPython(delete_offices),

        migrations.RemoveField(
            model_name='office',
            name='id',
        ),
        migrations.RemoveField(
            model_name='region',
            name='id',
        ),
        migrations.AlterField(
            model_name='office',
            name='name',
            field=models.CharField(serialize=False, primary_key=True, verbose_name='Назва органу', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='region',
            name='region_name',
            field=models.CharField(serialize=False, primary_key=True, verbose_name='Назва регіону', max_length=100),
            preserve_default=True,
        ),
        migrations.RunPython(load_offices),
    ]
