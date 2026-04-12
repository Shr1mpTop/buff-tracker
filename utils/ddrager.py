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
import time
import requests
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_manager import request_and_allocate_key, rollback_quota_on_failure


# API configuration
API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/price/single"
BATCH_API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/price/batch"
BASE_API_ENDPOINT = "https://open.steamdt.com/open/cs2/v1/base"
HISTORY_API_ENDPOINT = "https://api.steamdt.com/user/steam/type-trend/v2/item/details"
ENDPOINT_NAME = "price_single"
BATCH_ENDPOINT_NAME = "price_batch"
BASE_ENDPOINT_NAME = "base"


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


def request_base_api_key() -> str:
    """
    Request best available API key from api-manager for base endpoint
    
    Returns:
        str: API key or None if no available keys
    """
    return request_and_allocate_key(BASE_ENDPOINT_NAME)


def rollback_base_api_usage(api_key: str):
    """
    Notify api-manager about a failed base API call to rollback quota
    
    Args:
        api_key: The API key that was used
    """
    rollback_quota_on_failure(api_key, BASE_ENDPOINT_NAME)


def fetch_base_info() -> dict:
    """
    Fetch base info for all CS2 items
    
    Returns:
        dict: API response data or error
    """
    api_key = request_base_api_key()
    
    if not api_key:
        return {
            "error": "no_api_key",
            "message": "No available API key from api-manager"
        }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            BASE_API_ENDPOINT,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            rollback_base_api_usage(api_key)
            
        return response.json()
        
    except requests.RequestException as e:
        rollback_base_api_usage(api_key)
        return {
            "error": "request_failed",
            "message": str(e)
        }
    except Exception as e:
        rollback_base_api_usage(api_key)
        return {"error": "unexpected", "message": str(e)}


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


def _sync_fetch_history_price(
    hashname: str,
    platform: str = "STEAM",
    type_day: str = "5",
    date_type: int = 3,
) -> dict:
    """
    Synchronous Playwright implementation.  Runs in a thread pool so it
    doesn't conflict with the FastAPI / uvicorn asyncio event loop.

    Strategy:
    1. Navigate to the steamdt.com item detail page to pass the Aliyun WAF
       JS challenge via natural browser rendering.
    2. Use page.route() to intercept the page's own POST to type-trend and
       replace the body with our desired platform / typeDay / dateType params.
       The WAF sees a natural browser request, so it passes.
    3. Capture the modified response via page.on("response").
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "error": "playwright_not_installed",
            "message": "Run: uv add playwright && uv run playwright install chromium",
        }

    from urllib.parse import quote

    item_url = f"https://steamdt.com/cs2/{quote(hashname)}"
    captured_result: dict = {}

    def route_type_trend(route, request):
        try:
            original = json.loads(request.post_data or "{}")
            ts = original.get("timestamp", str(int(time.time() * 1000)))
            modified = {
                "itemId": original.get("itemId", ""),
                "platform": platform,
                "typeDay": type_day,
                "dateType": date_type,
                "timestamp": ts,
            }
            route.continue_(post_data=json.dumps(modified))
        except Exception:
            route.continue_()

    def handle_response(response):
        if "type-trend" in response.url and not captured_result:
            try:
                captured_result["result"] = response.json()
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/145.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            viewport={"width": 1920, "height": 1080},
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};
        """)
        page = context.new_page()
        page.route("**/type-trend/**", route_type_trend)
        page.on("response", handle_response)

        # Navigate to item page — page will naturally POST to type-trend
        try:
            page.goto(item_url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            pass

        # Poll up to 15 s for the captured response
        for _ in range(30):
            if captured_result:
                break
            page.wait_for_timeout(500)

        browser.close()

    result = captured_result.get("result")
    if result is None:
        return {
            "error": "no_data",
            "message": (
                f"Could not retrieve type-trend data for '{hashname}'. "
                "The item may not exist on steamdt.com."
            ),
        }
    return result


async def fetch_history_price(
    hashname: str,
    platform: str = "STEAM",
    type_day: str = "5",
    date_type: int = 3,
) -> dict:
    """
    Fetch historical price trend data for a CS2 item.

    Navigates to the steamdt.com item detail page (https://steamdt.com/cs2/{hashname})
    using a headless Chromium browser to pass the Aliyun WAF JS challenge,
    then POSTs to /user/steam/type-trend/v2/item/details with the specified
    platform / typeDay / dateType parameters from within the page context.

    Internally uses sync_playwright in a ThreadPoolExecutor to avoid
    asyncio / ProactorEventLoop compatibility issues on Windows.

    Args:
        hashname:  Steam market hash name, e.g. "M4A4 | Buzz Kill (Factory New)"
        platform:  Platform identifier ("STEAM", "YOUPIN", "BUFF", "C5", ...)
        type_day:  Aggregation period in days ("1", "3", "5", "7", "14", "30")
        date_type: Date range type (3 = default full history)

    Returns:
        dict: Raw SteamDT type-trend response {success, data, errorCode, ...}
              or {"error": ..., "message": ...} on failure
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from functools import partial

    loop = asyncio.get_event_loop()
    fn = partial(_sync_fetch_history_price, hashname, platform, type_day, date_type)
    with ThreadPoolExecutor(max_workers=1) as executor:
        result = await loop.run_in_executor(executor, fn)
    return result


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

