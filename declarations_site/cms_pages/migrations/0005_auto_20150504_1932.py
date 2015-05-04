# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fill_homepage(apps, schema_editor):
    HomePage = apps.get_model('cms_pages.HomePage')
    home_page = HomePage.objects.all()[0]
    home_page.body = """
Ми знаходимо, розшифровуємо та публікуємо декларації чиновників, щоб викрити їхню брехню про статки та майно. <br/>
Ви можете допомогти проекту <a href="http://sotnya.org.ua">долучившись до розшифровки</a>, або зробивши перерахунок на картку 5168 7423 3713 2520 (ПриватБанк).<br />
Краще долучайтесь до розшифровки, а гроші - на АТО. З вдячністю, Денис Бігус.
    """.strip()
    home_page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0004_homepage_body'),
    ]

    operations = [
        migrations.RunPython(fill_homepage),
    ]
