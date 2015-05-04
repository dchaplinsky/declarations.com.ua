# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20150504_2343'),
        ('cms_pages', '0005_auto_20150504_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('office', models.ForeignKey(blank=True, to='catalog.Office')),
                ('region', models.ForeignKey(blank=True, to='catalog.Region')),
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
