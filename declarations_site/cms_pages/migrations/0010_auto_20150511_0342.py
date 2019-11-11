# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20150511_0328'),
        ('cms_pages', '0009_auto_20150511_0339'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('office', models.ForeignKey(to='catalog.Office', null=True, blank=True, on_delete=models.CASCADE)),
                ('region', models.ForeignKey(to='catalog.Region', null=True, blank=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='metadata',
            unique_together=set([('region', 'office')]),
        ),
    ]
