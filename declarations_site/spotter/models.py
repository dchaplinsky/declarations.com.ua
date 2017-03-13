from django.db import models
from django.contrib.postgres import fields
from django.contrib.auth.models import User


class SearchTask(models.Model):
    user = models.ForeignKey(User)
    query = models.CharField("Пошуковий запит", max_length=150)
    deepsearch = models.BooleanField("Шукати скрізь", default=False)
    query_params = models.TextField("Опції", blank=True, default="", max_length=500)
    is_enabled = models.BooleanField("Активний", default=True, db_index=True)
    is_deleted = models.BooleanField("Видалений", default=False)
    found_total = models.IntegerField("Знайдено всього", default=0)
    found_week = models.IntegerField("Знайдено за тиждень", default=0)
    found_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=[],
        verbose_name="Знайдені документи")
    last_run = models.DateTimeField("Останній запуск", null=True, blank=True, default=None)
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)

    def __str__(self):
        return self.query


class TaskReport(models.Model):
    task = models.ForeignKey(SearchTask)
    found_total = models.IntegerField("Знайдено всього", default=0)
    found_new = models.IntegerField("Знайдено нових", default=0)
    found_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=[],
        verbose_name="Знайдені документи")
    new_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=[],
        verbose_name="Нові документи")
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)

    @property
    def user(self):
        return self.task.user

    def __str__(self):
        return "%s %s" % (self.created, self.task)


class NotifySend(models.Model):
    task = models.ForeignKey(SearchTask)
    email = models.CharField("Адреса", max_length=150)
    error = models.CharField("Помилки відправки", max_length=250, blank=True, default="")
    found_new = models.IntegerField("Знайдено нових", default=0)
    new_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=[],
        verbose_name="Нові документи")
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)

    @property
    def user(self):
        return self.task.user

    def __str__(self):
        return "%s %s" % (self.created, self.email)
