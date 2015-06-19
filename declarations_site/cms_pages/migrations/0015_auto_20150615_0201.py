# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0014_homepage_news_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='lead',
            field=models.TextField(blank=True, verbose_name='Лід'),
            preserve_default=True,
        ),
    ]
