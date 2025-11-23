#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create Items Table

Create table to store CS2 item base information from kinds API.
"""

import mysql.connector
from dotenv import load_dotenv
import os
import json
from pathlib import Path


def get_connection():
    """Create database connection"""
    load_dotenv()
    
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3307)),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'connection_timeout': 10,
        'ssl_disabled': True,
        'use_pure': True
    }
    
    return mysql.connector.connect(**config)


def create_items_table():
    """Create items table based on CS2 kinds API response"""
    
    # SQL to create items table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cs2_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL COMMENT '中文名称',
        market_hash_name VARCHAR(255) NOT NULL UNIQUE COMMENT 'Steam市场Hash名称',
        
        -- Platform IDs (nullable if item not available on platform)
        buff_id VARCHAR(50) COMMENT 'BUFF平台ID',
        c5_id VARCHAR(50) COMMENT 'C5平台ID',
        youpin_id VARCHAR(50) COMMENT 'YOUPIN平台ID',
        haloskins_id VARCHAR(50) COMMENT 'HALOSKINS平台ID',
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_market_hash_name (market_hash_name),
        INDEX idx_name (name),
        INDEX idx_buff_id (buff_id),
        INDEX idx_c5_id (c5_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    COMMENT='CS2饰品基础信息表';
    """
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        print("=" * 60)
        print("Creating CS2 Items Table")
        print("=" * 60)
        print()
        
        # Create table
        print("Creating table 'cs2_items'...")
        cursor.execute(create_table_sql)
        print("✓ Table created successfully")
        
        # Show table structure
        print("\nTable structure:")
        cursor.execute("DESCRIBE cs2_items;")
        columns = cursor.fetchall()
        
        print(f"\n{'Field':<20} {'Type':<30} {'Null':<5} {'Key':<5} {'Comment':<30}")
        print("-" * 100)
        for col in columns:
            field, type_, null, key, default, extra = col[:6]
            comment = col[8] if len(col) > 8 else ''
            print(f"{field:<20} {type_:<30} {null:<5} {key:<5} {comment:<30}")
        
        connection.commit()
        
        print("\n" + "=" * 60)
        print("Table creation completed")
        print("=" * 60)
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_items_from_cache():
    """Import items from cs2_kinds_cache.json to database"""
    cache_file = Path("cs2_kinds_cache.json")
    
    if not cache_file.exists():
        print("✗ Cache file not found: cs2_kinds_cache.json")
        print("  Please run: python utils/kinds.py --api-key YOUR_KEY")
        return False
    
    try:
        # Load cache data
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        if not cache_data.get('data', {}).get('success'):
            print("✗ Cache data is invalid")
            return False
        
        items = cache_data['data']['data']
        print(f"Found {len(items)} items in cache")
        
        # Connect to database
        connection = get_connection()
        cursor = connection.cursor()
        
        # Insert SQL
        insert_sql = """
        INSERT INTO cs2_items (name, market_hash_name, buff_id, c5_id, youpin_id, haloskins_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            buff_id = VALUES(buff_id),
            c5_id = VALUES(c5_id),
            youpin_id = VALUES(youpin_id),
            haloskins_id = VALUES(haloskins_id),
            updated_at = CURRENT_TIMESTAMP
        """
        
        print("\nImporting items to database...")
        imported = 0
        errors = 0
        
        for item in items:
            try:
                name = item.get('name', '')
                market_hash_name = item.get('marketHashName', '')
                
                if not market_hash_name:
                    continue
                
                # Extract platform IDs
                platform_list = item.get('platformList', [])
                platform_ids = {
                    'BUFF': None,
                    'C5': None,
                    'YOUPIN': None,
                    'HALOSKINS': None
                }
                
                for platform in platform_list:
                    platform_name = platform.get('name', '').upper()
                    if platform_name in platform_ids:
                        platform_ids[platform_name] = platform.get('itemId')
                
                # Insert to database
                cursor.execute(insert_sql, (
                    name,
                    market_hash_name,
                    platform_ids['BUFF'],
                    platform_ids['C5'],
                    platform_ids['YOUPIN'],
                    platform_ids['HALOSKINS']
                ))
                
                imported += 1
                
                if imported % 1000 == 0:
                    print(f"  Imported {imported} items...")
                    
            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"  ✗ Error importing item: {item.get('marketHashName', 'Unknown')}")
                    print(f"    {e}")
        
        connection.commit()
        
        print(f"\n✓ Import completed:")
        print(f"  - Successfully imported: {imported}")
        print(f"  - Errors: {errors}")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM cs2_items;")
        total = cursor.fetchone()[0]
        print(f"  - Total items in database: {total}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_sample_data():
    """Show sample data from table"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        print("\n" + "=" * 60)
        print("Sample Data (first 5 items)")
        print("=" * 60)
        
        cursor.execute("SELECT * FROM cs2_items LIMIT 5;")
        items = cursor.fetchall()
        
        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item['name']}")
            print(f"   Market Hash Name: {item['market_hash_name']}")
            print(f"   Platform IDs:")
            print(f"     BUFF: {item['buff_id'] or 'N/A'}")
            print(f"     C5: {item['c5_id'] or 'N/A'}")
            print(f"     YOUPIN: {item['youpin_id'] or 'N/A'}")
            print(f"     HALOSKINS: {item['haloskins_id'] or 'N/A'}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Error showing sample data: {e}")


if __name__ == "__main__":
    import sys
    
    # Step 1: Create table
    print("Step 1: Creating table...")
    if not create_items_table():
        print("\n✗ Failed to create table")
        sys.exit(1)
    
    # Step 2: Import data
    print("\n" + "=" * 60)
    print("Step 2: Importing data from cache...")
    print("=" * 60)
    if not import_items_from_cache():
        print("\n✗ Failed to import data")
        sys.exit(1)
    
    # Step 3: Show sample data
    show_sample_data()
    
    print("\n" + "=" * 60)
    print("All operations completed successfully!")
    print("=" * 60)
