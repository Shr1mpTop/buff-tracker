#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SearchName - Fuzzy search CS2 item names from database

Searches cs2_items table for items matching the query string,
returns top N most relevant market_hash_name results.
"""

import sys
import argparse
import json
from mysql.connector import connect, Error
from pathlib import Path
from dotenv import load_dotenv
import os


def get_db_connection():
    """
    Create database connection using .env configuration
    
    Returns:
        mysql.connector.connection: Database connection or None
    """
    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    try:
        connection = connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            connection_timeout=10,
            use_pure=True,
            ssl_disabled=True
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        return None


def fuzzy_search_items(query: str, limit: int = 10) -> list:
    """
    Fuzzy search items by name or market_hash_name
    
    Uses MySQL LIKE with wildcards for fuzzy matching.
    Prioritizes exact matches, then starts-with, then contains.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        list: List of dicts with item information
    """
    connection = get_db_connection()
    
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Multi-tier search strategy for better ranking:
        # 1. Exact match (highest priority)
        # 2. Starts with query (high priority)
        # 3. Contains query (medium priority)
        # 4. Word boundary match (low priority)
        
        search_query = """
        SELECT 
            id,
            name,
            market_hash_name,
            buff_id,
            c5_id,
            youpin_id,
            haloskins_id,
            CASE
                WHEN market_hash_name = %s THEN 1
                WHEN name = %s THEN 1
                WHEN market_hash_name LIKE %s THEN 2
                WHEN name LIKE %s THEN 2
                WHEN market_hash_name LIKE %s THEN 3
                WHEN name LIKE %s THEN 3
                ELSE 4
            END AS relevance
        FROM cs2_items
        WHERE 
            market_hash_name LIKE %s
            OR name LIKE %s
        ORDER BY relevance ASC, market_hash_name ASC
        LIMIT %s
        """
        
        # Prepare search patterns
        exact = query
        starts_with = f"{query}%"
        contains = f"%{query}%"
        
        cursor.execute(search_query, (
            exact, exact,           # Exact match
            starts_with, starts_with,  # Starts with
            contains, contains,     # Contains
            contains, contains,     # WHERE clause
            limit
        ))
        
        results = cursor.fetchall()
        
        # Remove relevance score from output
        for item in results:
            item.pop('relevance', None)
        
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"Database query error: {e}", file=sys.stderr)
        if connection:
            connection.close()
        return []


def main():
    parser = argparse.ArgumentParser(
        description='SearchName - Fuzzy search CS2 item names from database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/searchName.py --name "AK-47" --num 5
  python utils/searchName.py --name "Redline" --num 10
  python utils/searchName.py --name "刺刀" --num 3
  
Output:
  JSON array of matching items with market_hash_name and platform IDs
        """
    )
    
    parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Search query (supports Chinese and English, fuzzy matching)'
    )
    
    parser.add_argument(
        '--num',
        type=int,
        default=10,
        help='Maximum number of results to return (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Validate num parameter
    if args.num < 1:
        print("Error: --num must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    if args.num > 100:
        print("Warning: --num is capped at 100 for performance", file=sys.stderr)
        args.num = 100
    
    # Search database
    results = fuzzy_search_items(args.name, args.num)
    
    if not results:
        print(json.dumps({
            "success": False,
            "message": f"No items found matching '{args.name}'",
            "data": []
        }, ensure_ascii=False))
        sys.exit(1)
    
    # Output results
    output = {
        "success": True,
        "query": args.name,
        "count": len(results),
        "data": results
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
