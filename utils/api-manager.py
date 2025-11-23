#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Manager - Monitor and manage API key quota

Manages API key quota tracking, updates, and display.
Supports multiple API endpoints with different rate limits.
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
                
                # Load price_single quota
                price_remaining = int(row.get('price_remaining', 60))
                price_minute = row.get('price_minute', '')
                
                # Load base quota
                base_remaining = int(row.get('base_remaining', 1))
                base_day = row.get('base_day', '')
                
                quota_cache[api_key] = {
                    'price_single': {
                        'remaining_quota': price_remaining,
                        'minute_timestamp': price_minute
                    },
                    'base': {
                        'remaining_quota': base_remaining,
                        'day_timestamp': base_day
                    }
                }
    except Exception as e:
        pass
    
    return quota_cache


def save_quota(quota_cache, quota_file="api_quota.csv"):
    """Save quota information to CSV file"""
    try:
        with open(quota_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'api_key', 
                'price_remaining', 'price_minute',
                'base_remaining', 'base_day'
            ])
            
            for api_key, info in quota_cache.items():
                writer.writerow([
                    api_key,
                    info['price_single']['remaining_quota'],
                    info['price_single']['minute_timestamp'],
                    info['base']['remaining_quota'],
                    info['base']['day_timestamp']
                ])
    except Exception as e:
        pass


def initialize_all_keys(quota_file="api_quota.csv"):
    """Initialize quota for all API keys from .env"""
    api_keys = get_api_keys()
    if not api_keys:
        return
    
    quota_cache = load_quota(quota_file)
    current_minute = get_current_minute()
    current_day = get_current_day()
    
    # Ensure all keys are in the cache
    for api_key in api_keys:
        if api_key not in quota_cache:
            quota_cache[api_key] = {
                'price_single': {
                    'remaining_quota': 60,
                    'minute_timestamp': current_minute
                },
                'base': {
                    'remaining_quota': 1,
                    'day_timestamp': current_day
                }
            }
    
    save_quota(quota_cache, quota_file)


def get_api_keys():
    """Get API keys from environment"""
    api_keys_str = os.getenv('API_KEYS', '')
    if api_keys_str:
        return [key.strip() for key in api_keys_str.split(',') if key.strip()]
    return []


def get_best_api_key(endpoint="price_single", quota_file="api_quota.csv"):
    """
    Get the API key with the most remaining quota for specified endpoint
    
    Args:
        endpoint: API endpoint name ('price_single' or 'base')
        quota_file: Path to quota CSV file
    
    Returns:
        str: Best API key or None if no available keys
    """
    quota_cache = load_quota(quota_file)
    api_keys = get_api_keys()
    
    if endpoint not in RATE_LIMITS:
        print(f"Unknown endpoint: {endpoint}", file=sys.stderr)
        return None
    
    rate_config = RATE_LIMITS[endpoint]
    rate_limit = rate_config['limit']
    
    if not api_keys:
        return None
    
    best_key = None
    max_quota = -1
    
    # Get current timestamp based on period
    if rate_config['period'] == 'minute':
        current_timestamp = get_current_minute()
        timestamp_key = 'minute_timestamp'
    else:  # day
        current_timestamp = get_current_day()
        timestamp_key = 'day_timestamp'
    
    for api_key in api_keys:
        if api_key in quota_cache and endpoint in quota_cache[api_key]:
            quota_info = quota_cache[api_key][endpoint]
            
            # If timestamp doesn't match, quota is restored
            if quota_info.get(timestamp_key) != current_timestamp:
                remaining = rate_limit
            else:
                remaining = quota_info['remaining_quota']
        else:
            remaining = rate_limit
        
        if remaining > max_quota:
            max_quota = remaining
            best_key = api_key
    
    return best_key if max_quota > 0 else None


def display_quota(api_key=None, endpoint=None):
    """
    Display quota for specific API key or all keys
    
    Args:
        api_key: Specific API key to display (None for all)
        endpoint: Specific endpoint to display (None for all)
    """
    quota_cache = load_quota()
    api_keys = get_api_keys()
    current_minute = get_current_minute()
    current_day = get_current_day()
    
    if not api_keys:
        print("No API keys found")
        return
    
    if api_key:
        # Display specific key
        if api_key not in api_keys:
            print(f"API key not found in .env")
            return
        
        if api_key not in quota_cache:
            print(f"No quota data for this API key")
            return
        
        print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
        print()
        
        quota_info = quota_cache[api_key]
        
        # Display price_single quota
        if not endpoint or endpoint == "price_single":
            price_info = quota_info.get('price_single', {})
            price_minute = price_info.get('minute_timestamp', '')
            if price_minute != current_minute:
                price_remaining = 60
            else:
                price_remaining = price_info.get('remaining_quota', 60)
            print(f"Price Single: {price_remaining}/60 (per minute)")
        
        # Display base quota
        if not endpoint or endpoint == "base":
            base_info = quota_info.get('base', {})
            base_day = base_info.get('day_timestamp', '')
            if base_day != current_day:
                base_remaining = 1
            else:
                base_remaining = base_info.get('remaining_quota', 1)
            print(f"Base Info:    {base_remaining}/1  (per day)")
    else:
        # Display all keys
        print(f"{'API Key':<20} {'Price (min)':<15} {'Base (day)':<15}")
        print("=" * 50)
        
        for key in api_keys:
            masked_key = f"{key[:8]}...{key[-4:]}"
            
            if key in quota_cache:
                quota_info = quota_cache[key]
                
                # Price quota
                price_info = quota_info.get('price_single', {})
                price_minute = price_info.get('minute_timestamp', '')
                if price_minute != current_minute:
                    price_remaining = 60
                else:
                    price_remaining = price_info.get('remaining_quota', 60)
                
                # Base quota
                base_info = quota_info.get('base', {})
                base_day = base_info.get('day_timestamp', '')
                if base_day != current_day:
                    base_remaining = 1
                else:
                    base_remaining = base_info.get('remaining_quota', 1)
                
                print(f"{masked_key:<20} {price_remaining:>2}/60         {base_remaining:>1}/1")
            else:
                print(f"{masked_key:<20} {'60/60':<15} {'1/1':<15}")


def main():
    parser = argparse.ArgumentParser(
        description='API Manager - Monitor and manage API key quota',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/api-manager.py
  python utils/api-manager.py --api-key YOUR_KEY
  python utils/api-manager.py --init
  python utils/api-manager.py --best
        """
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Display quota for specific API key'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize all API keys in quota file'
    )
    
    parser.add_argument(
        '--best',
        type=str,
        choices=['price_single', 'base'],
        help='Get the best API key for specified endpoint'
    )
    
    parser.add_argument(
        '--endpoint',
        type=str,
        choices=['price_single', 'base'],
        help='Filter by specific endpoint'
    )
    
    args = parser.parse_args()
    
    if args.init:
        initialize_all_keys()
        print("✓ Initialized quota for all API keys")
    elif args.best:
        best_key = get_best_api_key(endpoint=args.best)
        if best_key:
            print(best_key)
        else:
            sys.exit(1)
    else:
        display_quota(api_key=args.api_key, endpoint=args.endpoint)


if __name__ == "__main__":
    main()
