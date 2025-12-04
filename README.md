Birthday API
Store birthdays and receive periodic alerts for them. Never miss a birthday again!

Features
Add, list, update, and delete birthdays
Optionally enable advanced 7-day alerts (for when you need to send a card!)
Basic password-based auth for privacy
Locally-hosted SQLite database, static web interface for adjustments
Automatic SMS alerts

Tech Stack
Python 3.12+
FastAPI
Starlette Sessions
Pydantic
Uvicorn
SQLite

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
chmod +x ./data/init_db.sh
./data/init_db.sh

When bday.py runs, if any of the birthdays in the database match the current date, it will send an SMS alert. Additional adjustments can be made to make the app perform to standard.

4. (Optional) Automation
The bday.py reminder script can be scheduled to run once per day (for example, I chose 8:00 A.M. EST).
The implementation of the automation is left to user discretion, but I will specify mine as follows (Systemd on Linux):

A. Create /etc/systemd/system/bday-reminder.service:

[Unit]
Description=Run birthday reminder script

[Service]
Type=oneshot
User=<your-user>
Group=<your-group>
WorkingDirectory=<path-to-your-bday-reminder-repo>
ExecStart=<path-to-your-bday-reminder-repo>/.venv/bin/python <path-to-your-bday-reminder-repo>/bday.py

B. Create /etc/systemd/system/bday-reminder.timer:

[Unit]
Description=Daily birthday reminder at 09:00

[Timer]
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target

C. Enable + start the timer
sudo systemctl daemon-reload
sudo systemctl enable --now bday-reminder.timer

Verify the timer is active with:
systemctl list-timers | grep bday-reminder

Optionally, manually run the reminder for testing:
sudo systemctl start bday-reminder.service

5. (Optional) Web Deployment
As of this point in the instructions, the end-user needs to manually add entries to data/birthdays.db. For better interactivity, it's desirable to deploy a web interface for the app.
Web deployment is accomplished via the bday_api/ directory. The implementation of the deployment is left to user discretion, but I will specify mine as follows:

A. Create /etc/systemd/system/bday-api.service:

[Unit]
Description=Birthday API (FastAPI/Uvicorn)
After=network.target

[Service]
User=<your-user>
Group=<your-group>
WorkingDirectory=<path-to-your-bday-reminder-repo>/bday_api
ExecStart=<path-to-your-bday-reminder-repo>/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

B. Reload and start:

sudo systemctl daemon-reload
sudo systemctl enable --now bday-api.service
sudo systemctl status bday-api.service

At this point the API is available on the server at http://127.0.0.1:8000

C. (Optional) Caddy reverse proxy - create /etc/caddy/Caddyfile
yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}

D. Activate Caddy proxy:

sudo systemctl enable --now caddy
sudo systemctl status caddy

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
