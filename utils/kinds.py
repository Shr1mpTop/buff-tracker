#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kinds - Fetch CS2 Item Base Information

Fetches all CS2 item categories and base information from SteamDT API.
Rate limit: 1 request per day per API key.
"""

import sys
import argparse
import json
import requests
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class CS2KindsFetcher:
    """CS2 Kinds API Manager"""
    
    API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/base"
    CACHE_FILE = "cs2_kinds_cache.json"
    
    def __init__(self, api_key: str):
        """
        Initialize fetcher
        
        Args:
            api_key: SteamDT API key
        """
        self.api_key = api_key
        self.cache_path = Path(self.CACHE_FILE)
    
    def fetch_kinds(self) -> dict:
        """
        Fetch CS2 item base information from API
        
        Returns:
            dict: API response data
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"Fetching CS2 item base information...")
            print(f"Endpoint: {self.API_ENDPOINT}")
            print(f"API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
            print()
            
            response = requests.get(
                self.API_ENDPOINT,
                headers=headers,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Successfully fetched data")
                return data
            else:
                print(f"✗ API request failed")
                print(f"Response: {response.text}")
                return {"error": f"HTTP {response.status_code}", "message": response.text}
                
        except requests.exceptions.Timeout:
            print(f"✗ Request timeout")
            return {"error": "timeout", "message": "Request timeout after 30 seconds"}
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error: {e}")
            return {"error": "request_failed", "message": str(e)}
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return {"error": "unexpected", "message": str(e)}
    
    def save_cache(self, data: dict) -> bool:
        """
        Save fetched data to cache file
        
        Args:
            data: Data to save
            
        Returns:
            bool: Success status
        """
        try:
            # Add metadata
            cache_data = {
                "fetched_at": datetime.now().isoformat(),
                "api_key_used": f"{self.api_key[:8]}...{self.api_key[-4:]}",
                "data": data
            }
            
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Data saved to: {self.cache_path.absolute()}")
            print(f"File size: {self.cache_path.stat().st_size:,} bytes")
            return True
            
        except Exception as e:
            print(f"\n✗ Failed to save cache: {e}")
            return False
    
    def load_cache(self) -> dict:
        """
        Load data from cache file
        
        Returns:
            dict: Cached data or None
        """
        if not self.cache_path.exists():
            return None
        
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            print(f"Cache file found: {self.cache_path.absolute()}")
            print(f"Fetched at: {cache_data.get('fetched_at', 'Unknown')}")
            print(f"API key used: {cache_data.get('api_key_used', 'Unknown')}")
            return cache_data
            
        except Exception as e:
            print(f"Failed to load cache: {e}")
            return None
    
    def run(self) -> dict:
        """
        Main execution: fetch data and save to cache
        
        Returns:
            dict: Fetched data
        """
        print("=" * 60)
        print("CS2 Kinds Fetcher")
        print("=" * 60)
        print()
        
        # Fetch data
        data = self.fetch_kinds()
        
        # Save to cache
        if not data.get('error'):
            self.save_cache(data)
        
        print()
        print("=" * 60)
        print("Fetch Complete")
        print("=" * 60)
        
        return data


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Fetch CS2 item base information from SteamDT API"
    )
    parser.add_argument(
        '--api-key',
        required=True,
        help='SteamDT API key'
    )
    
    args = parser.parse_args()
    
    # Create fetcher and run
    fetcher = CS2KindsFetcher(args.api_key)
    data = fetcher.run()
    
    # Print summary
    if not data.get('error'):
        print(f"\nData preview:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")
    
    return 0 if not data.get('error') else 1


if __name__ == "__main__":
    sys.exit(main())
