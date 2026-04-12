#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_FILE = Path(__file__).parent.parent / "api_quota.db"

# Beijing timezone (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def get_db_connection():
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize the database and create the api_keys table."""
    if DB_FILE.exists():
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE api_keys (
        api_key TEXT PRIMARY KEY,
        price_single_quota INTEGER DEFAULT 60,
        price_single_timestamp TEXT,
        price_batch_quota INTEGER DEFAULT 1,
        price_batch_timestamp TEXT,
        base_quota INTEGER DEFAULT 1,
        base_timestamp TEXT,
        kline_quota INTEGER DEFAULT 120,
        kline_timestamp TEXT
    )
    """)

    api_keys_str = os.getenv("API_KEYS", "")
    if api_keys_str:
        api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]
        current_minute = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
        current_day = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
        for key in api_keys:
            cursor.execute(
                "INSERT INTO api_keys (api_key, price_single_timestamp, price_batch_timestamp, base_timestamp, kline_timestamp) VALUES (?, ?, ?, ?, ?)",
                (key, current_minute, current_minute, current_day, current_minute)
            )

    conn.commit()
    conn.close()


def migrate_database():
    """Add new columns to existing database tables."""
    if not DB_FILE.exists():
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if kline_quota column exists
    cursor.execute("PRAGMA table_info(api_keys)")
    columns = [row['name'] for row in cursor.fetchall()]

    if 'kline_quota' not in columns:
        cursor.execute("ALTER TABLE api_keys ADD COLUMN kline_quota INTEGER DEFAULT 60")
    if 'kline_timestamp' not in columns:
        current_minute = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
        cursor.execute("ALTER TABLE api_keys ADD COLUMN kline_timestamp TEXT")
        cursor.execute(f"UPDATE api_keys SET kline_timestamp = '{current_minute}'")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print(f"Database initialized at {DB_FILE}")
