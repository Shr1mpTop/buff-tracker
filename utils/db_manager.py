#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_FILE = Path(__file__).parent.parent / "api_quota.db"

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
        base_quota INTEGER DEFAULT 1,
        base_timestamp TEXT
    )
    """)

    api_keys_str = os.getenv("API_KEYS", "")
    if api_keys_str:
        api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]
        current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
        current_day = datetime.now().strftime("%Y-%m-%d")
        for key in api_keys:
            cursor.execute(
                "INSERT INTO api_keys (api_key, price_single_timestamp, base_timestamp) VALUES (?, ?, ?)",
                (key, current_minute, current_day)
            )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print(f"Database initialized at {DB_FILE}")
