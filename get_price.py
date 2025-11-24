#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get Price - Automated skin price fetcher

Automatically calls ddrager to fetch price data.
ddrager requests API key from api-manager internally.
"""

import sys
import argparse
import json
import subprocess


def get_price(hashname):
    """
    Fetch price data using ddrager (which handles API key management internally)
    
    Args:
        hashname: Steam market hash name
        
    Returns:
        dict: Price data or None
    """
    # Call ddrager (it will request API key from api-manager automatically)
    result = subprocess.run(
        ['python', 'utils/ddrager.py', '--hashname', hashname],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
    else:
        # Print error message from ddrager
        if result.stderr:
            print(result.stderr, file=sys.stderr)
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
