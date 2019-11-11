from django.db import models
from django.contrib.postgres import fields
from django.contrib.auth.models import User


class SearchTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField("Пошуковий запит", max_length=150)
    deepsearch = models.BooleanField("Шукати скрізь", default=False)
    query_params = models.TextField("Опції", blank=True, default="", max_length=500)
    is_enabled = models.BooleanField("Активний", default=True, db_index=True)
    is_deleted = models.BooleanField("Видалений", default=False)
    found_total = models.IntegerField("Знайдено всього", default=0)
    found_week = models.IntegerField("Знайдено за тиждень", default=0)
    found_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=list,
        verbose_name="Знайдені документи")
    last_run = models.DateTimeField("Останній запуск", null=True, blank=True, default=None)
    chat_data = models.TextField("Дані чату", blank=True, default="", max_length=2000)
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)
    title = property(lambda self: self.query_title)

    def __str__(self):
        deepsearch = "*" if self.deepsearch else ""
        return "<{}: {}{}>".format(self.id, self.query, deepsearch)

    @property
    def is_allowed_edit_email(self):
        return self.user.email and not self.user.email.endswith(".chatbot")

    @property
    def display_email(self):
        if self.user.email and "@" in self.user.email and self.user.email.endswith(".chatbot"):
            return self.user.email.split("@", 1)[1]
        return self.user.email

    @property
    def query_opt(self):
        opt = []
        if not self.query:
            opt.append("пустий")
        if self.query_params and len(self.query_params) > 10:
            opt.append("з фільтрами")
        if self.deepsearch:
            opt.append("шукати скрізь")
        if not opt:
            return ""
        return " ({})".format(", ".join(opt))

    @property
    def query_title(self):
        return "{}{}".format(self.query, self.query_opt)


class TaskReport(models.Model):
    task = models.ForeignKey(SearchTask, on_delete=models.CASCADE)
    found_total = models.IntegerField("Знайдено всього", default=0)
    found_new = models.IntegerField("Знайдено нових", default=0)
    found_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=list,
        verbose_name="Знайдені документи")
    new_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=list,
        verbose_name="Нові документи")
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)
    user = property(lambda self: self.task.user)

    def __str__(self):
        return "<{}: {} {}>".format(self.id, self.created, self.task)


class NotifySend(models.Model):
    task = models.ForeignKey(SearchTask, on_delete=models.CASCADE)
    email = models.CharField("Адреса", max_length=150)
    error = models.CharField("Помилки відправки", max_length=250, blank=True, default="")
    found_new = models.IntegerField("Знайдено нових", default=0)
    new_ids = fields.ArrayField(models.CharField(max_length=60), blank=True, default=list,
        verbose_name="Нові документи")
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)
    user = property(lambda self: self.task.user)

    def __str__(self):
        return "<{}: {} {}>".format(self.id, self.created, self.email)
