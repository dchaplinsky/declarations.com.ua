# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-01 16:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchtask',
            name='chat_data',
            field=models.TextField(blank=True, default='', max_length=2000, verbose_name='Дані чату'),
        ),
    ]