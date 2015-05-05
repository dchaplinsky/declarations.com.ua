# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0006_auto_20150505_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metadata',
            name='title',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
