# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class AuctionTypes(models.Model):
    name = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = 'auction_types'


class Branches(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512)
    sname = models.CharField(max_length=4)
    name_vidm = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = 'branches'


class Bulletins(models.Model):
    name = models.CharField(max_length=32)
    pub_date = models.DateField()
    comments = models.CharField(max_length=1024, blank=True, null=True)
    is_published = models.NullBooleanField()
    bulletin_type_id = models.IntegerField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bulletins'


class Buyers(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    person = models.TextField(blank=True, null=True)
    modify_date = models.DateField(blank=True, null=True)
    create_date = models.DateField(blank=True, null=True)
    name_en = models.TextField(blank=True, null=True)
    address_en = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    region = models.ForeignKey('Regions', blank=True, null=True, on_delete=models.CASCADE)
    err = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'buyers'


class Currencies(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    name_genitive = models.CharField(max_length=64)
    sname = models.CharField(max_length=16)
    kop_sname = models.CharField(max_length=16, blank=True, null=True)
    sname_en = models.CharField(max_length=10, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'currencies'


class CurrencyRates(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    rate = models.FloatField(blank=True, null=True)
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'currency_rates'


class PurchaseResultTypes(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'purchase_result_types'


class Purchases(models.Model):
    disc = models.CharField(max_length=2, blank=True, null=True)
    goods_name = models.TextField(blank=True, null=True)
    goods_quan = models.TextField(blank=True, null=True)
    goods_name_short = models.TextField(blank=True, null=True)
    lot_count = models.IntegerField(blank=True, null=True)
    cost_source = models.TextField(blank=True, null=True)
    cost_dispatcher_code = models.CharField(max_length=512, blank=True, null=True)
    cost_dispatcher_name = models.CharField(max_length=1024, blank=True, null=True)
    purchase_type_id = models.IntegerField(blank=True, null=True)
    announce_id = models.IntegerField(blank=True, null=True)
    start_bulletin_number = models.CharField(max_length=1024, blank=True, null=True)
    is_frame = models.IntegerField(blank=True, null=True)
    prozorro = models.CharField(max_length=32, blank=True, null=True)
    prozorro_number = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    buyer = models.ForeignKey(Buyers, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branches, blank=True, null=True, on_delete=models.CASCADE)
    auction_type = models.ForeignKey(AuctionTypes, blank=True, null=True, on_delete=models.CASCADE)
    subject_type = models.ForeignKey('SubjectTypes', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'purchases'

class Regions(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'regions'


class Sellers(models.Model):
    name = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address_full = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    group_discr = models.TextField(unique=True, blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    err = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'sellers'


class SubjectTypes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'subject_types'

class Transactions(models.Model):
    date = models.DateField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    volume_uah = models.FloatField(blank=True, null=True)
    accept_date = models.DateField(blank=True, null=True)
    is_vat_included = models.IntegerField(blank=True, null=True)
    disc = models.CharField(max_length=10, blank=True, null=True)
    lots = models.TextField(blank=True, null=True)
    goods_code = models.CharField(max_length=256, blank=True, null=True)
    grounds = models.TextField(blank=True, null=True)
    classifier_goods_name = models.TextField(blank=True, null=True)
    announce_date = models.DateField(blank=True, null=True)
    announce_code = models.CharField(max_length=64, blank=True, null=True)
    announce_number = models.CharField(max_length=32, blank=True, null=True)
    announce_is_external = models.IntegerField(blank=True, null=True)
    announce_unumber = models.CharField(max_length=256, blank=True, null=True)
    prozorro = models.CharField(max_length=32, blank=True, null=True)
    prozorro_number = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    purchase = models.ForeignKey(Purchases, on_delete=models.CASCADE)
    seller = models.ForeignKey(Sellers, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    purchase_result_type = models.ForeignKey(PurchaseResultTypes, blank=True, null=True, on_delete=models.CASCADE)
    bulletin = models.ForeignKey(Bulletins, blank=True, null=True, on_delete=models.CASCADE)
    expected_volume = models.FloatField(blank=True, null=True)
    err = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'transactions'
