from django.db import models
from treebeard.mp_tree import MP_Node


class Region(models.Model):
    region_name = models.CharField("Назва регіону", max_length=100)
    order_id = models.IntegerField()


class Office(MP_Node):
    name = models.CharField("Назва органу", max_length=255)
    order_id = models.IntegerField()

    node_order_by = ['order_id']
