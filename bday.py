import os
import sqlite3
import sys
import logging
from datetime import date, datetime
import requests
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.getenv("DB_PATH")
LOG_PATH = os.getenv("LOG_PATH")
TEXTBELT_KEY = os.getenv("TEXTBELT_KEY")
SMS_NUM = os.getenv("SMS_NUM")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def send_text(msg):
    try:
        resp = requests.post('https://textbelt.com/text', {
            'phone': SMS_NUM,
            'message': f"{msg}",
            'key': TEXTBELT_KEY,
        })
        data = resp.json()
        success = data.get("success", False)
        quota_remaining = data.get('quotaRemaining')

        if success:
            logging.info(f"SMS sent successfully. TextID={data.get('textId')}, Quota remaining={quota_remaining}")
        else:
            err_msg = data.get('error', 'Unknown error')
            logging.error(f"SMS send failed: {err_msg}")

        if (quota_remaining == 6):
            logging.warning("Only 5 messages remaining on Textbelt quota!")
            send_text('Alert: You have 5 messages remaining with Textbelt')

    except Exception as e:
        logging.exception(f"Unexpected error while sending SMS: {e}")


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT name, bday, notify_7days FROM bday")
    today = date.today()

    logging.info(f"Running birthday check on {today}")

    sms = ''
    for name, bday_str, notify_7days in c.fetchall():
        bday = datetime.strptime(bday_str, "%Y-%m-%d").date()
        next_bday = date(today.year, bday.month, bday.day)
        if (next_bday < today):
            next_bday = next_bday.replace(year=today.year + 1)

        days_until = (next_bday - today).days
        years_old = next_bday.year - bday.year

        if days_until == 0:
            sms += f"It is {name}'s birthday! They turned {years_old}!\n"
        elif days_until == 7 and notify_7days:
            sms += f"7 days until {name}'s birthday! They are turning {years_old}!\n"
    if sms != '':
        send_text(sms)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
