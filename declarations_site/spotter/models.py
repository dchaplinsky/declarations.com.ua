from django.db import models
from django.contrib.auth.models import User


class SearchTask(models.Model):
    user = models.ForeignKey(User)
    query = models.CharField("Пошуковий запит", max_length=150)
    deepsearch = models.BooleanField("Шукати скрізь", default=False)
    query_params = models.TextField("Опції", blank=True, default="", max_length=500)
    is_enabled = models.BooleanField("Акнтивний", default=True)
    is_deleted = models.BooleanField("Видалений", default=False)
    found_total = models.IntegerField("Знайдено всього", default=0)
    found_week = models.IntegerField("Знайдено за тиждень", default=0)
    found_ids = models.TextField("Знайдені документи", blank=True, default="", max_length=int(16e6))
    last_run = models.DateTimeField("Останній запуск", null=True, blank=True, default=None)
    create_date = models.DateTimeField("Створений", auto_now_add=True, blank=True)
    change_date = models.DateTimeField("Змінений", auto_now=True, blank=True)

    def __unicode__(self):
        return self.query

    def __str__(self):
        return self.query


class TaskReport(models.Model):
    task = models.ForeignKey(SearchTask)
    found_total = models.IntegerField("Знайдено всього", default=0)
    found_new = models.IntegerField("Знайдено нових", default=0)
    found_ids = models.TextField("Знайдені документи", blank=True, default="", max_length=int(16e6))
    new_ids = models.TextField("Нові документи", blank=True, default="", max_length=int(16e6))
    create_date = models.DateTimeField("Створений", auto_now_add=True, blank=True)

    @property
    def user(self):
        return self.task.user

    def __unicode__(self):
        return "%s %s" % (self.create_date, self.task)

    def __str__(self):
        return "%s %s" % (self.create_date, self.task)


class NotifySend(models.Model):
    task = models.ForeignKey(SearchTask)
    email = models.CharField("Адреса", max_length=150)
    status = models.CharField("Статус відправки", max_length=250)
    new_ids = models.TextField("Нові документи", blank=True, default="", max_length=int(16e6))
    create_date = models.DateTimeField("Створений", auto_now_add=True, blank=True)

    @property
    def user(self):
        return self.task.user

    def __unicode__(self):
        return "%s %s" % (self.create_date, self.email)

    def __str__(self):
        return "%s %s" % (self.create_date, self.email)
