# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0008_auto_20150505_0231'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='metadata',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='metadata',
            name='office',
        ),
        migrations.RemoveField(
            model_name='metadata',
            name='region',
        ),
        migrations.DeleteModel(
            name='MetaData',
        ),
    ]
