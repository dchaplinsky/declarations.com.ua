from django.db import models
from django.contrib.auth.models import User


class ChatHistory(models.Model):
    user = models.ForeignKey(User, null=True, default=None)
    from_id = models.CharField("FromID", max_length=250)
    from_name = models.CharField("FromName", max_length=250)
    conversation = models.CharField("Conversation", max_length=250)
    query = models.CharField("Запит", max_length=250)
    answer = models.CharField("Відповідь", max_length=250)
    timestamp = models.CharField("Timestamp", max_length=50)
    created = models.DateTimeField("Створений", auto_now_add=True, blank=True)

    def __str__(self):
        return self.query
