#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

DB_FILE="$PROJECT_ROOT/data/birthdays.db"
SCHEMA_FILE="$SCRIPT_DIR/schema.sql"

mkdir -p "$PROJECT_ROOT/data"

sqlite3 "$DB_FILE" < "$SCHEMA_FILE"

echo "Created $DB_FILE"
