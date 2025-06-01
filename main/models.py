from django.contrib.auth.models import User
from django.db import models

class TelegramAlertReceiver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    receive_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.telegram_chat_id}"
