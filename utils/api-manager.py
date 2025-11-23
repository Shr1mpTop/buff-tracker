#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Manager - Monitor and display API key quota status

A command-line tool to check remaining quota for SteamDT API keys.
"""

import sys
import argparse
import csv
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_current_minute():
    """Get current minute timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_quota(quota_file="api_quota.csv"):
    """Load quota information from CSV file"""
    quota_cache = {}
    quota_path = Path(quota_file)
    
    if not quota_path.exists():
        return quota_cache
    
    try:
        with open(quota_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                api_key = row['api_key']
                remaining = int(row['remaining_quota'])
                minute = row['minute_timestamp']
                
                quota_cache[api_key] = {
                    'remaining_quota': remaining,
                    'minute_timestamp': minute
                }
    except Exception as e:
        pass
    
    return quota_cache


def get_api_keys():
    """Get API keys from environment"""
    api_keys_str = os.getenv('API_KEYS', '')
    if api_keys_str:
        return [key.strip() for key in api_keys_str.split(',') if key.strip()]
    return []


def display_quota(api_key=None):
    """Display quota for specific API key or all keys"""
    quota_cache = load_quota()
    api_keys = get_api_keys()
    current_minute = get_current_minute()
    rate_limit = 60  # Default rate limit per minute
    
    if not api_keys:
        print("No API keys found")
        return
    
    # Filter to specific key if provided
    if api_key:
        if api_key not in api_keys:
            print(f"Key not found: {api_key[:8]}...")
            return
        keys_to_display = [api_key]
    else:
        keys_to_display = api_keys
    
    # Display quota for each key
    for key in keys_to_display:
        masked_key = f"{key[:8]}...{key[-4:]}"
        
        if key in quota_cache:
            quota_info = quota_cache[key]
            
            # If minute doesn't match, quota is restored
            if quota_info['minute_timestamp'] != current_minute:
                remaining = rate_limit
            else:
                remaining = quota_info['remaining_quota']
        else:
            # No quota record, assume full quota
            remaining = rate_limit
        
        print(f"{masked_key}: {remaining}/{rate_limit}")
    
    # Show summary only for all keys
    if not api_key and len(keys_to_display) > 1:
        total_remaining = sum(
            quota_cache[key]['remaining_quota'] if key in quota_cache and quota_cache[key]['minute_timestamp'] == current_minute else rate_limit
            for key in keys_to_display
        )
        print(f"Total: {total_remaining}/{len(keys_to_display) * rate_limit}")


def main():
    parser = argparse.ArgumentParser(
        description='API Manager - Monitor API key quota status',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/api-manager.py
  python utils/api-manager.py --api-key YOUR_SPECIFIC_KEY
        """
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Display quota for specific API key'
    )
    
    args = parser.parse_args()
    
    display_quota(api_key=args.api_key)


if __name__ == "__main__":
    main()
