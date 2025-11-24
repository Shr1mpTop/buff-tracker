#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DDrager - Core Data Fetching Tool for Steam Market Prices

A lightweight command-line tool that fetches raw price data from SteamDT API.
Returns unprocessed JSON data for use by other tools.

Architecture:
- Data Layer: Requests API key from api-manager before each call
- Notifies api-manager after successful/failed API call for quota tracking
"""

import sys
import argparse
import json
import requests
import subprocess
from pathlib import Path


# API configuration
API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/price/single"
ENDPOINT_NAME = "price_single"


def request_api_key() -> str:
    """
    Request best available API key from api-manager
    
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


def fetch_price(hashname: str) -> dict:
    """
    Fetch price data for a given item
    
    Args:
        hashname: Steam market hash name
        
    Returns:
        dict: API response data or error
    """
    # Step 1: Request API key from manager
    api_key = request_api_key()
    
    if not api_key:
        return {
            "error": "no_api_key",
            "message": "No available API key from api-manager"
        }
    
    # Step 2: Call API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {"market_hash_name": hashname}
    
    try:
        response = requests.get(
            API_ENDPOINT,
            headers=headers,
            params=params,
            timeout=10
        )
        
        success = response.status_code == 200
        
        # Step 3: Notify api-manager about result
        notify_api_usage(api_key, success)
        
        if success:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }
            
    except requests.exceptions.Timeout:
        notify_api_usage(api_key, False)
        return {"error": "timeout", "message": "Request timeout"}
    except requests.exceptions.RequestException as e:
        notify_api_usage(api_key, False)
        return {"error": "request_failed", "message": str(e)}
    except Exception as e:
        notify_api_usage(api_key, False)
        return {"error": "unexpected", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='DDrager - Core data fetching tool for Steam market prices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/ddrager.py --hashname "AK-47 | Redline (Field-Tested)"
  python utils/ddrager.py --hashname "AWP | Asiimov (Field-Tested)"
  
Note: API key is automatically requested from api-manager
        """
    )
    
    parser.add_argument(
        '--hashname',
        type=str,
        required=True,
        help='Steam market hash name'
    )
    
    args = parser.parse_args()
    
    # Fetch price (API key requested internally)
    data = fetch_price(args.hashname)
    
    # Output raw JSON
    if not data.get('error'):
        print(json.dumps(data, ensure_ascii=False))
        sys.exit(0)
    else:
        print(json.dumps(data, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

