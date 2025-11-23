#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DDrager - Core Data Fetching Tool for Steam Market Prices

A lightweight command-line tool that fetches raw price data from SteamDT API.
Returns unprocessed JSON data for use by other tools.
"""

import sys
import argparse
import json
import requests
import threading
import time
import csv
import os
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class APIKeyQuota:
    """API key quota information"""
    api_key: str
    minute_timestamp: str  
    remaining_quota: int


# Load environment variables
load_dotenv()


class SteamDTAPIManager:
    """SteamDT API Manager - Supports automatic key rotation and rate limit management"""
    
    # Load API keys from environment variables
    API_KEYS = os.getenv('API_KEYS', '').split(',') if os.getenv('API_KEYS') else []
    
    # Rate limit configuration
    RATE_LIMITS = {
        "price_single": 60,  # 60 requests per minute
    }
    
    # API endpoints
    API_ENDPOINTS = {
        "price_single": "https://open.steamdt.com/open/cs2/v1/price/single",
    }
    
    def __init__(self, quota_file: str = "api_quota.csv"):
        """
        Initialize API manager
        
        Args:
            quota_file: Path to quota tracking file
        """
        self.quota_file = Path(quota_file)
        self.lock = threading.Lock()
        self.quota_cache: Dict[str, Dict[str, any]] = {}
        self._load_quota()
    
    def _get_current_minute(self) -> str:
        """Get current minute timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def _load_quota(self):
        """Load quota information from CSV file"""
        if not self.quota_file.exists():
            self._initialize_quota()
            return
        
        try:
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    api_key = row['api_key']
                    remaining = int(row['remaining_quota'])
                    minute = row['minute_timestamp']
                    
                    self.quota_cache[api_key] = {
                        'remaining_quota': remaining,
                        'minute_timestamp': minute
                    }
        except Exception as e:
            self._initialize_quota()
    
    def _initialize_quota(self):
        """Initialize quota for all API keys"""
        current_minute = self._get_current_minute()
        for api_key in self.API_KEYS:
            self.quota_cache[api_key] = {
                'remaining_quota': self.RATE_LIMITS["price_single"],
                'minute_timestamp': current_minute
            }
        self._save_quota()
    
    def _save_quota(self):
        """Save quota information to CSV file"""
        try:
            # Load existing quota data first
            existing_quota = {}
            if self.quota_file.exists():
                with open(self.quota_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_quota[row['api_key']] = {
                            'remaining_quota': int(row['remaining_quota']),
                            'minute_timestamp': row['minute_timestamp']
                        }
            
            # Update with current cache
            existing_quota.update(self.quota_cache)
            
            # Write all quota data
            with open(self.quota_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['api_key', 'remaining_quota', 'minute_timestamp'])
                
                for api_key, info in existing_quota.items():
                    writer.writerow([api_key, info['remaining_quota'], info['minute_timestamp']])
        except Exception as e:
            pass
    
    def _get_available_api_key(self, rate_limit: int) -> Optional[str]:
        """Get an API key with remaining quota"""
        current_minute = self._get_current_minute()
        
        with self.lock:
            for api_key in self.API_KEYS:
                if api_key not in self.quota_cache:
                    self.quota_cache[api_key] = {
                        'remaining_quota': rate_limit,
                        'minute_timestamp': current_minute
                    }
                
                quota_info = self.quota_cache[api_key]
                
                if quota_info['minute_timestamp'] != current_minute:
                    quota_info['remaining_quota'] = rate_limit
                    quota_info['minute_timestamp'] = current_minute

                if quota_info['remaining_quota'] > 0:
                    quota_info['remaining_quota'] -= 1
                    self._save_quota()
                    return api_key
            
            return None
    
    def get_price_single(self, market_hash_name: str, max_retries: int = 3, retry_delay: int = 1) -> Optional[Dict]:
        """
        Query single item price
        
        Args:
            market_hash_name: Steam market item name
            max_retries: Maximum retry attempts
            retry_delay: Retry delay in seconds
            
        Returns:
            Raw API response dictionary, or None on failure
        """
        rate_limit = self.RATE_LIMITS["price_single"]
        url = self.API_ENDPOINTS["price_single"]
        
        for attempt in range(max_retries):
            api_key = self._get_available_api_key(rate_limit)
            
            if api_key is None:
                time.sleep(retry_delay)
                continue

            headers = {"Authorization": f"Bearer {api_key}"}
            params = {"marketHashName": market_hash_name}
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    with self.lock:
                        if api_key in self.quota_cache:
                            self.quota_cache[api_key]['remaining_quota'] = 0
                            self._save_quota()
                    continue
                    
            except Exception as e:
                pass
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        return None


def main():
    parser = argparse.ArgumentParser(
        description='DDrager - Core data fetching tool for Steam market prices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ddrager.py --apikey YOUR_KEY --hashname "AK-47 | Redline (Field-Tested)"
  python ddrager.py --apikey YOUR_KEY --hashname "AWP | Asiimov (Field-Tested)"
        """
    )
    
    parser.add_argument(
        '--apikey',
        type=str,
        required=True,
        help='API key for SteamDT (required)'
    )
    
    parser.add_argument(
        '--hashname',
        type=str,
        required=True,
        help='Steam market hash name'
    )
    
    args = parser.parse_args()
    
    # Set API key temporarily
    os.environ['API_KEYS'] = args.apikey
    SteamDTAPIManager.API_KEYS = [args.apikey]
    
    manager = SteamDTAPIManager()
    result = manager.get_price_single(market_hash_name=args.hashname)
    
    # Output raw JSON data to stdout
    if result:
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

