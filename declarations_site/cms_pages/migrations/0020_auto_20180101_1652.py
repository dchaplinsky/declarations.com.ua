# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-01 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0019_homepagebottommenulink'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepagebottommenulink',
            name='extra_class',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='homepagetopmenulink',
            name='extra_class',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
