# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0016_auto_20150615_0215'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('fullname', models.CharField(verbose_name="Повне ім'я", max_length=150)),
                ('year', models.IntegerField(verbose_name='Рік декларації', blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='personmeta',
            unique_together=set([('year', 'fullname')]),
        ),
    ]
