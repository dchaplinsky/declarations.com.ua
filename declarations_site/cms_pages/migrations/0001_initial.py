# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name': 'Головна сторінка',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='HomePageTopMenuLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('caption', models.CharField(blank=True, max_length=255)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RawHTMLPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('body', models.TextField(verbose_name='Текст сторінки')),
            ],
            options={
                'verbose_name': 'Raw-HTML сторінка',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('body', wagtail.wagtailcore.fields.RichTextField(verbose_name='Текст сторінки')),
            ],
            options={
                'verbose_name': 'Статична сторінка',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AddField(
            model_name='homepagetopmenulink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', blank=True, related_name='+', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagetopmenulink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='top_menu_links', to='cms_pages.HomePage'),
            preserve_default=True,
        ),
    ]
