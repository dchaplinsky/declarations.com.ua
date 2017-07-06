# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-17 20:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuctionTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
            options={
                'managed': False,
                'db_table': 'auction_types',
            },
        ),
        migrations.CreateModel(
            name='Branches',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('sname', models.CharField(max_length=4)),
                ('name_vidm', models.CharField(max_length=512)),
            ],
            options={
                'managed': False,
                'db_table': 'branches',
            },
        ),
        migrations.CreateModel(
            name='Bulletins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('pub_date', models.DateField()),
                ('comments', models.CharField(blank=True, max_length=1024, null=True)),
                ('is_published', models.NullBooleanField()),
                ('bulletin_type_id', models.IntegerField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'bulletins',
            },
        ),
        migrations.CreateModel(
            name='Buyers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('fax', models.TextField(blank=True, null=True)),
                ('email', models.TextField(blank=True, null=True)),
                ('person', models.TextField(blank=True, null=True)),
                ('modify_date', models.DateField(blank=True, null=True)),
                ('create_date', models.DateField(blank=True, null=True)),
                ('name_en', models.TextField(blank=True, null=True)),
                ('address_en', models.TextField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('err', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'buyers',
            },
        ),
        migrations.CreateModel(
            name='Currencies',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('name_genitive', models.CharField(max_length=64)),
                ('sname', models.CharField(max_length=16)),
                ('kop_sname', models.CharField(blank=True, max_length=16, null=True)),
                ('sname_en', models.CharField(blank=True, max_length=10, null=True)),
                ('code', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'currencies',
            },
        ),
        migrations.CreateModel(
            name='CurrencyRates',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('rate', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'currency_rates',
            },
        ),
        migrations.CreateModel(
            name='PurchaseResultTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'managed': False,
                'db_table': 'purchase_result_types',
            },
        ),
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disc', models.CharField(blank=True, max_length=2, null=True)),
                ('goods_name', models.TextField(blank=True, null=True)),
                ('goods_quan', models.TextField(blank=True, null=True)),
                ('goods_name_short', models.TextField(blank=True, null=True)),
                ('lot_count', models.IntegerField(blank=True, null=True)),
                ('cost_source', models.TextField(blank=True, null=True)),
                ('cost_dispatcher_code', models.CharField(blank=True, max_length=512, null=True)),
                ('cost_dispatcher_name', models.CharField(blank=True, max_length=1024, null=True)),
                ('purchase_type_id', models.IntegerField(blank=True, null=True)),
                ('announce_id', models.IntegerField(blank=True, null=True)),
                ('start_bulletin_number', models.CharField(blank=True, max_length=1024, null=True)),
                ('is_frame', models.IntegerField(blank=True, null=True)),
                ('prozorro', models.CharField(blank=True, max_length=32, null=True)),
                ('prozorro_number', models.TextField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'purchases',
            },
        ),
        migrations.CreateModel(
            name='Regions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'regions',
            },
        ),
        migrations.CreateModel(
            name='Sellers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('address_full', models.TextField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('group_discr', models.TextField(blank=True, null=True, unique=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('err', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'sellers',
            },
        ),
        migrations.CreateModel(
            name='SubjectTypes',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'managed': False,
                'db_table': 'subject_types',
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('volume', models.FloatField(blank=True, null=True)),
                ('volume_uah', models.FloatField(blank=True, null=True)),
                ('accept_date', models.DateField(blank=True, null=True)),
                ('is_vat_included', models.IntegerField(blank=True, null=True)),
                ('disc', models.CharField(blank=True, max_length=10, null=True)),
                ('lots', models.TextField(blank=True, null=True)),
                ('goods_code', models.CharField(blank=True, max_length=256, null=True)),
                ('grounds', models.TextField(blank=True, null=True)),
                ('classifier_goods_name', models.TextField(blank=True, null=True)),
                ('announce_date', models.DateField(blank=True, null=True)),
                ('announce_code', models.CharField(blank=True, max_length=64, null=True)),
                ('announce_number', models.CharField(blank=True, max_length=32, null=True)),
                ('announce_is_external', models.IntegerField(blank=True, null=True)),
                ('announce_unumber', models.CharField(blank=True, max_length=256, null=True)),
                ('prozorro', models.CharField(blank=True, max_length=32, null=True)),
                ('prozorro_number', models.TextField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('expected_volume', models.FloatField(blank=True, null=True)),
                ('err', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'transactions',
            },
        ),
    ]