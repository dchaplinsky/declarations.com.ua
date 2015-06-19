# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0013_auto_20150615_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='news_count',
            field=models.IntegerField(default=6, verbose_name='Кількість новин на сторінку'),
            preserve_default=True,
        ),
    ]
