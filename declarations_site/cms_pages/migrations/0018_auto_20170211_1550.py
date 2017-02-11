# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0017_auto_20160417_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='office',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Office', blank=True),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Region', blank=True),
        ),
        migrations.AlterField(
            model_name='personmeta',
            name='year',
            field=models.IntegerField(null=True, choices=[(2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015)], blank=True, verbose_name='Рік декларації'),
        ),
    ]
