# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0007_auto_20150505_0230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='office',
            field=models.ForeignKey(blank=True, to='catalog.Office', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metadata',
            name='region',
            field=models.ForeignKey(blank=True, to='catalog.Region', null=True),
            preserve_default=True,
        ),
    ]
