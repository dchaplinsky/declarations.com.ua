from django.db import models
from django.contrib.auth.models import User


class ChatHistory(models.Model):
    user = models.ForeignKey(User, null=True, default=None)
    from_id = models.CharField("FromID", max_length=250, default='', db_index=True)
    from_name = models.CharField("FromName", max_length=250, default='')
    channel = models.CharField("ChannelID", max_length=250, default='')
    conversation = models.CharField("Conversation", max_length=250, default='')
    query = models.CharField("Запит", max_length=250, default='')
    answer = models.CharField("Відповідь", max_length=250, default='')
    timestamp = models.CharField("Timestamp", max_length=50, default='')
    auto_reply = models.BooleanField("Розсилка", default=False)
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True, db_index=True)

    def __str__(self):
        return self.query
