import os
from io import BytesIO

import requests
from openpyxl import load_workbook


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["BUDGET_UPDATES_CHAT_ID"]

TXT_URL = "http://45.8.250.108/budget_updates.txt"
XLSX_URL = "http://45.8.250.108/main_routine_tg_msg.xlsx"

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def read_text_file():
    """Скачивает и читает текстовый файл."""
    response = requests.get(TXT_URL, timeout=30)
    response.raise_for_status()

    # utf-8 — ожидаемая кодировка русского текста.
    # errors="strict" позволит сразу заметить проблему с кодировкой.
    return response.content.decode("utf-8")


def read_flags():
    """Скачивает XLSX и читает значения dash, slides и katya."""
    response = requests.get(XLSX_URL, timeout=30)
    response.raise_for_status()

    workbook = load_workbook(
        filename=BytesIO(response.content),
        data_only=True,
    )

    sheet = workbook.active

    # Первая строка — названия столбцов.
    headers = [cell.value for cell in sheet[1]]

    # Вторая строка — значения 0/1.
    values = [cell.value for cell in sheet[2]]

    data = {
        str(header).strip(): value
        for header, value in zip(headers, values)
    }

    return {
        "dash": data.get("dash") == 1,
        "slides": data.get("slides") == 1,
        "katya": data.get("katya") == 1,
    }


def build_message(text, flags):
    """Формирует итоговое сообщение."""
    additions = []

    if flags["dash"]:
        additions.append(
            "[Dashboard](http://45.8.250.108/index.html) обновлен."
        )

    if flags["slides"]:
        additions.append(
            "Обновлены слайды: для "
            "[дэшборда](http://45.8.250.108/Budget_dashboard_upd.pptx) "
            "и для "
            "[ОПР](http://45.8.250.108/Budget_routine_upd.pptx)."
        )

    if flags["katya"]:
        additions.append(
            "Обновил файл для "
            "[Кати Петреневой]"
            "(http://45.8.250.108/e_r_rollsums_for_Katya.xlsx)."
        )

    if additions:
        return text.rstrip() + "\n\n" + "\n".join(additions)

    return text


def send_message(message):
    """Отправляет сообщение в Telegram."""
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    response = requests.post(
        TELEGRAM_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")


def main():
    text = read_text_file()
    flags = read_flags()

    print(f"Flags: {flags}")

    message = build_message(text, flags)

    print("Message to send:")
    print(message)

    send_message(message)

    print("Budget updates message sent successfully")


if __name__ == "__main__":
    main()
