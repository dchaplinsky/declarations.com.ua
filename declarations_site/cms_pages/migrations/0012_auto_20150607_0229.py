# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
        ('cms_pages', '0011_newspage'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, primary_key=True, to='wagtailcore.Page', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Сторінка новин',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='important',
            field=models.BooleanField(default=False, verbose_name='Важлива новина'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='newspage',
            name='sticky',
            field=models.BooleanField(default=False, verbose_name='Закріпити новину'),
            preserve_default=True,
        ),
    ]
