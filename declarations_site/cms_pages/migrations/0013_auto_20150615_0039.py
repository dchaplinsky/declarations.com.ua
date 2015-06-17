# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0005_make_filter_spec_unique'),
        ('cms_pages', '0012_auto_20150607_0229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newspage',
            name='headline',
        ),
        migrations.AddField(
            model_name='newspage',
            name='image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, to='wagtailimages.Image'),
            preserve_default=True,
        ),
    ]
