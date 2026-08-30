```python
import os
import requests


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"

payload = {
    "chat_id": CHAT_ID,
    "question": "Планируете ли вы прийти завтра в офис?",
    "options": [
        "Да",
        "Нет",
        "Я в отпуске / командировке / на больничном",
    ],
    "is_anonymous": False,
    "parse_mode": "Markdown",
}

response = requests.post(URL, json=payload, timeout=30)

response.raise_for_status()

result = response.json()

if not result.get("ok"):
    raise RuntimeError(f"Telegram API error: {result}")

print("Poll sent successfully")
print(result)
```
