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

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_manager import request_and_allocate_key, rollback_quota_on_failure


# API configuration
API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/price/single"
BATCH_API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/price/batch"
ENDPOINT_NAME = "price_single"
BATCH_ENDPOINT_NAME = "price_batch"


def request_api_key() -> str:
    """
    Request best available API key from api-manager
    
    Returns:
        str: API key or None if no available keys
    """
    return request_and_allocate_key(ENDPOINT_NAME)


def request_batch_api_key() -> str:
    """
    Request best available API key from api-manager for batch endpoint
    
    Returns:
        str: API key or None if no available keys
    """
    return request_and_allocate_key(BATCH_ENDPOINT_NAME)


def rollback_api_usage(api_key: str):
    """
    Notify api-manager about a failed API call to rollback quota
    
    Args:
        api_key: The API key that was used
    """
    rollback_quota_on_failure(api_key, ENDPOINT_NAME)


def rollback_batch_api_usage(api_key: str):
    """
    Notify api-manager about a failed batch API call to rollback quota
    
    Args:
        api_key: The API key that was used
    """
    rollback_quota_on_failure(api_key, BATCH_ENDPOINT_NAME)


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
    
    params = {"marketHashName": hashname}
    
    try:
        response = requests.get(
            API_ENDPOINT,
            headers=headers,
            params=params,
            timeout=10
        )
        
        success = response.status_code == 200
        
        if not success:
            # Rollback quota on failure
            rollback_api_usage(api_key)
            
        return response.json()
        
    except requests.RequestException as e:
        # Rollback quota on network errors or timeouts
        rollback_api_usage(api_key)
        return {
            "error": "request_failed",
            "message": str(e)
        }
    except Exception as e:
        rollback_api_usage(api_key)
        return {"error": "unexpected", "message": str(e)}


def fetch_batch_price(hashnames: list) -> dict:
    """
    Fetch batch price data for multiple items
    
    Args:
        hashnames: List of Steam market hash names
        
    Returns:
        dict: API response data or error
    """
    # Step 1: Request API key from manager
    api_key = request_batch_api_key()
    
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
    
    data = {"marketHashNames": hashnames}
    
    try:
        response = requests.post(
            BATCH_API_ENDPOINT,
            headers=headers,
            json=data,
            timeout=30  # Longer timeout for batch
        )
        
        success = response.status_code == 200
        
        if not success:
            # Rollback quota on failure
            rollback_batch_api_usage(api_key)
            
        return response.json()
        
    except requests.RequestException as e:
        # Rollback quota on network errors or timeouts
        rollback_batch_api_usage(api_key)
        return {
            "error": "request_failed",
            "message": str(e)
        }
    except Exception as e:
        rollback_batch_api_usage(api_key)
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

