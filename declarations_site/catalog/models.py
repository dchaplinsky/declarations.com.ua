from django.db import models
from treebeard.mp_tree import MP_Node


class Region(models.Model):
    region_name = models.CharField("Назва регіону", max_length=100,
                                   primary_key=True)
    order_id = models.IntegerField()

    def __unicode__(self):
        return self.region_name

    def __str__(self):
        return self.region_name


class Office(MP_Node):
    name = models.CharField("Назва органу", max_length=255, primary_key=True)
    order_id = models.IntegerField()

    node_order_by = ['order_id']

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name
