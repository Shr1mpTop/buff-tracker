#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get Price - Automated skin price fetcher

Automatically selects the best API key and fetches price data.
"""

import sys
import argparse
import json
import subprocess


def get_best_api_key():
    """Get the API key with the most remaining quota"""
    result = subprocess.run(
        ['python', 'utils/api-manager.py', '--best', 'price_single'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        api_key = result.stdout.strip()
        return api_key if api_key else None
    
    return None


def get_price(hashname):
    """Fetch price data using the best available API key"""
    # Initialize all keys first time
    subprocess.run(
        ['python', 'utils/api-manager.py', '--init'],
        capture_output=True
    )
    
    # Get the best API key
    api_key = get_best_api_key()
    
    if not api_key:
        print("No available API keys with remaining quota", file=sys.stderr)
        return None
    
    # Call ddrager to fetch data
    result = subprocess.run(
        ['python', 'utils/ddrager.py', '--apikey', api_key, '--hashname', hashname],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Get Price - Automated skin price fetcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_price.py --hashname "AK-47 | Redline (Field-Tested)"
  python get_price.py --hashname "AWP | Asiimov (Field-Tested)"
        """
    )
    
    parser.add_argument(
        '--hashname',
        type=str,
        required=True,
        help='Steam market hash name'
    )
    
    args = parser.parse_args()
    
    # Fetch price data
    data = get_price(args.hashname)
    
    if data:
        print(json.dumps(data, ensure_ascii=False))
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
