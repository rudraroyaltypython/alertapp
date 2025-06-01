from django.contrib import admin
from .models import TelegramAlertReceiver

@admin.register(TelegramAlertReceiver)
class TelegramAlertReceiverAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_chat_id', 'receive_notifications']
    list_editable = ['receive_notifications']
