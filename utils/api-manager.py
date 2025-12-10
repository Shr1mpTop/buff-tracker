#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Manager - Monitor and manage API key quota

Manages API key quota tracking, updates, and display.
Supports multiple API endpoints with different rate limits.
"""

import sys
import argparse
from datetime import datetime
import os
from dotenv import load_dotenv
from . import db_manager  # Import the new DB manager

# Load environment variables
load_dotenv()


# API endpoint rate limits
RATE_LIMITS = {
    "price_single": {
        "limit": 60,
        "period": "minute"  # 60 requests per minute
    },
    "base": {
        "limit": 1,
        "period": "day"  # 1 request per day
    }
}


def get_current_minute():
    """Get current minute timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def get_current_day():
    """Get current day timestamp"""
    return datetime.now().strftime("%Y-%m-%d")


def get_api_keys():
    """Get API keys from environment"""
    api_keys_str = os.getenv('API_KEYS', '')
    if api_keys_str:
        return [key.strip() for key in api_keys_str.split(',') if key.strip()]
    return []


def request_and_allocate_key(endpoint: str) -> str:
    """
    Service interface: Allocate best API key for data layer request
    Also decrements quota for the allocated key
    
    Args:
        endpoint: API endpoint name ('price_single' or 'base')
        
    Returns:
        str: Allocated API key or None if no available keys
    """
    db_manager.initialize_database()  # Ensure DB is initialized
    
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    if endpoint not in RATE_LIMITS:
        return None

    rate_config = RATE_LIMITS[endpoint]
    rate_limit = rate_config['limit']
    
    if rate_config['period'] == 'minute':
        current_timestamp = get_current_minute()
        quota_field = 'price_single_quota'
        timestamp_field = 'price_single_timestamp'
    else:  # day
        current_timestamp = get_current_day()
        quota_field = 'base_quota'
        timestamp_field = 'base_timestamp'

    # Reset quotas for keys where the timestamp is outdated
    cursor.execute(f"SELECT api_key, {timestamp_field} FROM api_keys")
    keys_to_reset = [row['api_key'] for row in cursor.fetchall() if row[timestamp_field] != current_timestamp]
    
    if keys_to_reset:
        placeholders = ','.join('?' for _ in keys_to_reset)
        cursor.execute(
            f"UPDATE api_keys SET {quota_field} = ?, {timestamp_field} = ? WHERE api_key IN ({placeholders})",
            (rate_limit, current_timestamp, *keys_to_reset)
        )
        conn.commit()

    # Find the best key
    cursor.execute(
        f"SELECT api_key FROM api_keys WHERE {quota_field} > 0 ORDER BY {quota_field} DESC LIMIT 1"
    )
    result = cursor.fetchone()

    if result:
        best_key = result['api_key']
        # Decrement quota
        cursor.execute(
            f"UPDATE api_keys SET {quota_field} = {quota_field} - 1 WHERE api_key = ?",
            (best_key,)
        )
        conn.commit()
        conn.close()
        return best_key
    
    conn.close()
    return None


def update_quota_on_success(api_key: str, endpoint: str):
    """
    Service interface: Called by data layer on successful API call (no action needed for now)
    """
    # With the new system, quota is decremented at allocation, so no action is needed here.
    # We could add logging or other success tracking in the future.
    pass


def rollback_quota_on_failure(api_key: str, endpoint: str):
    """
    Service interface: Called by data layer on failed API call to rollback quota
    """
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    
    if endpoint not in RATE_LIMITS:
        conn.close()
        return

    if RATE_LIMITS[endpoint]['period'] == 'minute':
        quota_field = 'price_single_quota'
    else:
        quota_field = 'base_quota'

    cursor.execute(
        f"UPDATE api_keys SET {quota_field} = {quota_field} + 1 WHERE api_key = ?",
        (api_key,)
    )
    conn.commit()
    conn.close()
    

def main():
    """Main function for CLI tool"""
    parser = argparse.ArgumentParser(description="API Key Quota Manager")
    parser.add_argument(
        'action', 
        choices=['request', 'rollback', 'show'], 
        help="Action to perform. 'request' allocates a key, 'rollback' restores quota on failure, 'show' displays current quotas."
    )
    parser.add_argument('--endpoint', type=str, help="API endpoint (e.g., 'price_single' or 'base')")
    parser.add_argument('--api_key', type=str, help="API key to rollback quota for")
    
    args = parser.parse_args()

    if args.action == 'request':
        if not args.endpoint:
            print("Error: --endpoint is required for the 'request' action.", file=sys.stderr)
            sys.exit(1)
        allocated_key = request_and_allocate_key(args.endpoint)
        if allocated_key:
            print(allocated_key)  # Output just the key for scripting
        else:
            print("No available API key for this endpoint.", file=sys.stderr)
            sys.exit(1)

    elif args.action == 'rollback':
        if not args.api_key or not args.endpoint:
            print("Error: --api_key and --endpoint are required for the 'rollback' action.", file=sys.stderr)
            sys.exit(1)
        rollback_quota_on_failure(args.api_key, args.endpoint)
        print(f"Rolled back quota for key {args.api_key} on endpoint {args.endpoint}.")

    elif args.action == 'show':
        db_manager.initialize_database()
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_keys ORDER BY api_key")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("No API keys found in the database.")
            return

        print(f"{'API Key':<50} {'Price Quota':<15} {'Price Minute':<20} {'Base Quota':<15} {'Base Day':<20}")
        print("-" * 120)
        for row in rows:
            print(
                f"{row['api_key']:<50} "
                f"{row['price_single_quota']:<15} "
                f"{row['price_single_timestamp']:<20} "
                f"{row['base_quota']:<15} "
                f"{row['base_timestamp']:<20}"
            )

if __name__ == '__main__':
    main()
