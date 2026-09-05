import os
from html import escape
from io import BytesIO
from urllib.parse import urljoin

import requests
from openpyxl import load_workbook


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["BUDGET_UPDATES_CHAT_ID"]

PUBLIC_BASE_URL = os.environ.get("BUDGET_PUBLIC_BASE_URL", "http://45.8.250.108/").rstrip("/") + "/"
TXT_URL = os.environ.get("BUDGET_UPDATES_TXT_URL", urljoin(PUBLIC_BASE_URL, "budget_updates.txt"))
XLSX_URL = os.environ.get("BUDGET_FLAGS_XLSX_URL", urljoin(PUBLIC_BASE_URL, "main_routine_tg_msg.xlsx"))

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def read_text_file():
    """Скачивает и читает текстовый файл с сообщением от budget_updates.py."""
    response = requests.get(TXT_URL, timeout=30)
    response.raise_for_status()
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
    headers = [cell.value for cell in sheet[1]]
    values = [cell.value for cell in sheet[2]]

    data = {
        str(header).strip(): value
        for header, value in zip(headers, values)
        if header is not None
    }

    return {
        "dash": data.get("dash") == 1,
        "slides": data.get("slides") == 1,
        "katya": data.get("katya") == 1,
    }


def html_link(label, url):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def build_message(text, flags):
    """Формирует итоговое Telegram-сообщение."""
    additions = []

    if flags["dash"]:
        additions.append(
            f"{html_link('Dashboard', urljoin(PUBLIC_BASE_URL, 'index.html'))} обновлен."
        )

    if flags["slides"]:
        additions.append(
            "Обновлены слайды: для "
            f"{html_link('дэшборда', urljoin(PUBLIC_BASE_URL, 'Budget_dashboard_upd.pptx'))} "
            "и для "
            f"{html_link('ОПР', urljoin(PUBLIC_BASE_URL, 'Budget_routine_upd.pptx'))}."
        )

    if flags["katya"]:
        additions.append(
            "Обновил файл для "
            f"{html_link('Кати Петреневой', urljoin(PUBLIC_BASE_URL, 'e_r_rollsums_for_Katya.xlsx'))}."
        )

    escaped_text = escape(text.rstrip())

    if additions:
        return escaped_text + "\n\n" + "\n".join(additions)

    return escaped_text


def send_message(message):
    """Отправляет сообщение в Telegram."""
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
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

    print(f"Text URL: {TXT_URL}")
    print(f"Flags URL: {XLSX_URL}")
    print(f"Flags: {flags}")

    message = build_message(text, flags)

    print("Message to send:")
    print(message)

    send_message(message)

    print("Budget updates message sent successfully")


if __name__ == "__main__":
    main()
