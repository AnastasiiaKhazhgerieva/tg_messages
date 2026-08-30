
import os
import requests


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["NEWS_CHAT_ID"]

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"

payload = {
    "chat_id": CHAT_ID,
    "question": 'На этой неделе новостной блок по "..." подготавливает',
    "options": [
        "Внешнему сектору",
        "Экономике",
        "Инфляции",
        "Не готовлю, смотрю ответы",
    ],
    "is_anonymous": False,
}

response = requests.post(URL, json=payload, timeout=30)
response.raise_for_status()

result = response.json()

if not result.get("ok"):
    raise RuntimeError(f"Telegram API error: {result}")

print("News poll sent successfully")
print(result)
