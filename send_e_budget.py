
import os
from io import BytesIO

import requests
from openpyxl import load_workbook


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["E_BUDGET_CHAT_ID"]

XLSX_URL = "http://45.8.250.108/e_budget.xlsx"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def main():
    # Скачиваем Excel-файл
    response = requests.get(XLSX_URL, timeout=30)
    response.raise_for_status()

    # Открываем Excel из памяти
    workbook = load_workbook(
        filename=BytesIO(response.content),
        data_only=True,
    )

    sheet = workbook.active

    # Первая строка — заголовки
    headers = [cell.value for cell in sheet[1]]

    # Вторая строка — данные
    values = [cell.value for cell in sheet[2]]

    # Связываем заголовки со значениями
    data = {
        str(header): "" if value is None else str(value)
        for header, value in zip(headers, values)
    }

    date = data["Дата"]
    income_plan = data["Доходы план"]
    income_fact = data["Доходы факт"]
    expense_plan = data["Расходы план"]
    expense_fact = data["Расходы факт"]

    # Формируем сообщение
    message = f"""💰 *Федеральный бюджет* (`{date}`):

📈 *Доходы:*
План: `{income_plan}`
Факт: `{income_fact}`

📉 *Расходы:*
План: `{expense_plan}`
Факт: `{expense_fact}`"""

    # Отправляем сообщение в Telegram
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    telegram_response = requests.post(
        TELEGRAM_URL,
        json=payload,
        timeout=30,
    )

    telegram_response.raise_for_status()

    result = telegram_response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")

    print("E-budget message sent successfully")


if __name__ == "__main__":
    main()
