-- schema.sql
-- SQLite schema for birthdays database.

CREATE TABLE IF NOT EXISTS bday (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bday TEXT NOT NULL,
    notify_7days INTEGER NOT NULL DEFAULT 0
);
