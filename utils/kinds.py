#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kinds - Fetch CS2 Item Base Information

Fetches all CS2 item categories and base information from SteamDT API.
Rate limit: 1 request per day per API key.

Architecture:
- Data Layer: Requests API key from api-manager before fetching
- Notifies api-manager after successful/failed API call for quota tracking
"""

import sys
import argparse
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path


# API configuration
API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/base"
ENDPOINT_NAME = "base"
CACHE_FILE = "cs2_kinds_cache.json"


def request_api_key() -> str:
    """
    Request best available API key from api-manager for base endpoint
    
    Returns:
        str: API key or None if no available keys
    """
    result = subprocess.run(
        ['python', 'utils/api-manager.py', '--request-key', ENDPOINT_NAME],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode == 0:
        api_key = result.stdout.strip()
        return api_key if api_key else None
    return None


def notify_api_usage(api_key: str, success: bool):
    """
    Notify api-manager about API call result for quota tracking
    
    Args:
        api_key: The API key that was used
        success: Whether the API call succeeded
    """
    subprocess.run(
        ['python', 'utils/api-manager.py', '--notify-usage',
         '--endpoint', ENDPOINT_NAME,
         '--api-key', api_key,
         '--success' if success else '--failed'],
        capture_output=True,
        cwd=Path(__file__).parent.parent
    )


class CS2KindsFetcher:
    """CS2 Kinds API Manager"""
    
    def __init__(self):
        """
        Initialize fetcher (API key will be requested from api-manager)
        """
        self.cache_path = Path(CACHE_FILE)
        self.api_key = None
    
    def fetch_kinds(self) -> dict:
        """
        Fetch CS2 item base information from API
        Requests API key from api-manager automatically
        
        Returns:
            dict: API response data
        """
        # Step 1: Request API key from manager
        print(f"Requesting API key from api-manager...")
        self.api_key = request_api_key()
        
        if not self.api_key:
            print(f"✗ No available API key")
            return {
                "error": "no_api_key",
                "message": "No available API key from api-manager (daily quota exhausted?)"
            }
        
        # Step 2: Call API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"Fetching CS2 item base information...")
            print(f"Endpoint: {API_ENDPOINT}")
            print(f"API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
            print()
            
            response = requests.get(
                API_ENDPOINT,
                headers=headers,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            success = response.status_code == 200
            
            # Step 3: Notify api-manager about result
            notify_api_usage(self.api_key, success)
            
            if success:
                data = response.json()
                print(f"✓ Successfully fetched data")
                return data
            else:
                print(f"✗ API request failed")
                print(f"Response: {response.text}")
                return {"error": f"HTTP {response.status_code}", "message": response.text}
                
        except requests.exceptions.Timeout:
            notify_api_usage(self.api_key, False)
            print(f"✗ Request timeout")
            return {"error": "timeout", "message": "Request timeout after 30 seconds"}
        except requests.exceptions.RequestException as e:
            notify_api_usage(self.api_key, False)
            print(f"✗ Request error: {e}")
            return {"error": "request_failed", "message": str(e)}
        except Exception as e:
            notify_api_usage(self.api_key, False)
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
        description="Fetch CS2 item base information from SteamDT API",
        epilog="Note: API key is automatically requested from api-manager"
    )
    
    args = parser.parse_args()
    
    # Create fetcher and run (API key requested internally)
    fetcher = CS2KindsFetcher()
    data = fetcher.run()
    
    # Print summary
    if not data.get('error'):
        print(f"\nData preview:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")
    
    return 0 if not data.get('error') else 1


if __name__ == "__main__":
    sys.exit(main())
