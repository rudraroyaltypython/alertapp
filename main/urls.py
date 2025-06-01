from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('send_alert/', views.send_alert, name='send_alert'),  # <-- Add this line
    path('telegram-webhook/', views.telegram_webhook, name='telegram_webhook'),
]
