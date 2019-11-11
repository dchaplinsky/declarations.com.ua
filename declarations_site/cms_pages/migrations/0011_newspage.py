# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
        ('cms_pages', '0010_auto_20150511_0342'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='wagtailcore.Page', parent_link=True, on_delete=models.CASCADE)),
                ('headline', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('lead', models.TextField(verbose_name='Лід')),
                ('body', models.TextField(verbose_name='Текст новини')),
                ('date_added', models.DateTimeField(verbose_name='Опубліковано')),
                ('sticky', models.BooleanField(verbose_name='Закріпити новину')),
                ('important', models.BooleanField(verbose_name='Важлива новина')),
            ],
            options={
                'verbose_name': 'Новина',
            },
            bases=('wagtailcore.page',),
        ),
    ]
