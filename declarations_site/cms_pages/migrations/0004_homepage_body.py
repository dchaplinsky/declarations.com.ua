# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0003_auto_20150504_0217'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='body',
            field=wagtail.core.fields.RichTextField(verbose_name='Текст сторінки', default=''),
            preserve_default=False,
        ),
    ]
