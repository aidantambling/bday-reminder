#!/usr/bin/env bash
set -e

mkdir -p data

sqlite3 data/birthdays.db < schema.sql

echo "Created data/birthdays.db"
