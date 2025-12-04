Birthday API

Features

Tech Stack

Requirements

Installation and Setup

1. Installation
git clone https://github.com/aidantambling/bday-reminder.git
cd bday-reminder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Environment Setup
mv .env.template .env

Edit .env to fill in appropriate values
DB_PATH: path to your sqlite3 db. Typically will be ./data/birthdays.db
LOG_PATH: path to your log file. Options include ./ or ./logs/
SMS_NUM: phone number to which alerts should be texted
TEXTBELT_KEY: textbelt api key being used to send sms messages
SESSION_SECRET: a random, long string used to secure middleware

3. Database Setup
./data/init_db.sh

Deployment

Project Structure

bday/
│
├── bday_api/
│   ├── main.py
│   └── static/
│       └── index.html
│
├── data/
│   └── init_db.sh
│   └── schema.sql
│
├── requirements.txt
├── .env.template
└── README.md
