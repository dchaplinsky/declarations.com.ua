# Generated by Django 2.2.11 on 2020-06-09 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_auto_20200220_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='region_name_en',
            field=models.CharField(default='', max_length=100, verbose_name='Назва регіону [en]'),
        ),
    ]
