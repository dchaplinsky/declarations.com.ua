# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0015_auto_20150615_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(verbose_name='Текст новини'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='newspage',
            name='lead',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, verbose_name='Лід'),
            preserve_default=True,
        ),
    ]
