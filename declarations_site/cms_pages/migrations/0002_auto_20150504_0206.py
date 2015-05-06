# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django import VERSION as DJANGO_VERSION


def reset_homepage(apps, schema_editor):
    Site = apps.get_model('wagtailcore.Site')
    Page = apps.get_model('wagtailcore.Page')
    HomePage = apps.get_model('cms_pages.HomePage')
    ContentType = apps.get_model('contenttypes.ContentType')

    page_content_type, _ = ContentType.objects.get_or_create(
        model='page',
        app_label='wagtailcore',
        defaults={'name': 'page'} if DJANGO_VERSION < (1, 8) else {}
    )

    home_page_content_type, _ = ContentType.objects.get_or_create(
        model='homepage',
        app_label='cms_pages',
        defaults={'name': 'homepage'} if DJANGO_VERSION < (1, 8) else {}
    )

    Page.objects.all().delete()
    Site.objects.all().delete()

    root = Page.objects.create(
        title="Root",
        slug='root',
        content_type=page_content_type,
        path='0001',
        depth=1,
        numchild=1,
        url_path='/',
    )

    # Create homepage
    homepage = HomePage.objects.create(
        title="Декларації: головна сторінка",
        slug='home',
        content_type=home_page_content_type,
        path='00010001',
        depth=2,
        numchild=0,
        url_path='/home/',
    )

    # Create default site
    Site.objects.create(
        hostname='localhost',
        root_page_id=homepage.id,
        is_default_site=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(reset_homepage),
    ]
