from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import TelegramAlertReceiver
import requests
import json

# 🔐 Your Telegram bot token (store it securely in production!)
TELEGRAM_BOT_TOKEN = '8065356352:AAF2uHFDwTfRiZ04umBw1GdH3J6_ebVOgyc'  # Replace with your actual bot token

def home(request):
    return render(request, 'main/home.html')


@csrf_exempt
def send_alert(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    latitude = data.get('latitude')
    longitude = data.get('longitude')
    message_text = data.get('message', '🚨 Emergency Alert!')

    if latitude is None or longitude is None:
        return JsonResponse({"error": "Missing latitude or longitude"}, status=400)

    location_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    alert_message = f"{message_text}\n📍 Location: {location_url}"

    # Updated filter to use `telegram_chat_id`
    receivers = TelegramAlertReceiver.objects.filter(
        receive_notifications=True,
        telegram_chat_id__isnull=False
    ).exclude(telegram_chat_id='')

    if not receivers.exists():
        return JsonResponse({"error": "No receivers available to send alerts"}, status=400)

    errors = []
    for receiver in receivers:
        try:
            send_telegram_message(receiver.telegram_chat_id, alert_message)
        except Exception as e:
            errors.append(f"Failed to send to {receiver.user.username}: {str(e)}")

    if errors:
        return JsonResponse({"error": " | ".join(errors)}, status=500)

    return JsonResponse({"status": "Alert sent"})


def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        raise Exception(f"Telegram API error: {response.status_code} - {response.text}")


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            chat_id = data['message']['chat']['id']
            username = data['message']['from']['username']

            from django.contrib.auth.models import User
            user = User.objects.filter(username=username).first()
            if user:
                receiver, _ = TelegramAlertReceiver.objects.get_or_create(user=user)
                receiver.telegram_chat_id = chat_id
                receiver.save()

            return JsonResponse({'status': 'chat_id saved'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
