from django.db import models
from treebeard.mp_tree import MP_Node


class Region(models.Model):
    region_name = models.CharField("Назва регіону", max_length=100, primary_key=True)
    region_name_en = models.CharField(
        "Назва регіону [en]", max_length=100, default="", blank=True
    )
    order_id = models.IntegerField()

    def __unicode__(self):
        return self.region_name

    def __str__(self):
        return self.region_name


class Office(MP_Node):
    name = models.CharField("Назва органу", max_length=255, primary_key=True)
    order_id = models.IntegerField()

    node_order_by = ["order_id"]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Translation(models.Model):
    SOURCE_CHOICES = {
        "g": "Google translate",
        "p": "Translations from PEP project",
        "t": "Translator of declarations project",
        "u": "Yet to translate",
    }

    term_id = models.CharField(
        "Ідентифікатор терміну", primary_key=True, max_length=4096
    )
    term = models.TextField("Термін")
    translation = models.TextField("Переклад")
    source = models.CharField(
        "Джерело перекладу", max_length=1, choices=SOURCE_CHOICES.items()
    )
    quality = models.IntegerField("Суб'єктивна якість перекладу")
    strict_id = models.BooleanField("Чи було ідентифікатор спрощено")
    frequency = models.IntegerField("Кількість вживань у текстах", default=0)

    class Meta:
        index_together = [["frequency", "source"]]
