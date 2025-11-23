#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Connection Test

Test MySQL database connection for buff tracker.
"""

import mysql.connector
from mysql.connector import Error
import socket
import signal
import sys


def test_network():
    """Test network connectivity to database server"""
    print("\nTesting network connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('mysql2.sqlpub.com', 3307))
        sock.close()
        
        if result == 0:
            print("✓ Port 3307 is reachable")
            return True
        else:
            print(f"✗ Port 3307 is not reachable (error code: {result})")
            return False
    except Exception as e:
        print(f"✗ Network test failed: {e}")
        return False


def test_connection():
    """Test MySQL database connection"""
    config = {
        'host': 'mysql2.sqlpub.com',
        'port': 3307,
        'database': 'buffotte',
        'user': 'hezhili',
        'password': 'aSh6zlBSHfvpEx4e',
        'connection_timeout': 5,
        'connect_timeout': 5,
        'ssl_disabled': True,  # Disable SSL to avoid SSL handshake issues
        'use_pure': True  # Use pure Python implementation (might be more stable)
    }
    
    print("=" * 60)
    print("MySQL Connection Test")
    print("=" * 60)
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Timeout: {config['connection_timeout']}s")
    print("=" * 60)
    
    # Test network first
    if not test_network():
        print("\n✗ Network connectivity test failed")
        print("Please check:")
        print("  1. Internet connection")
        print("  2. Firewall settings")
        print("  3. Database server status")
        return False
    
    try:
        print("\nAttempting to connect to MySQL...")
        print("Step 1: Calling mysql.connector.connect()...")
        print("(This may take up to 5 seconds...)")
        
        connection = mysql.connector.connect(**config)
        print("Step 2: Connection object created")
        
        print("Step 3: Checking if connected...")
        if connection.is_connected():
            print("Step 4: Connection verified!")
            db_info = connection.get_server_info()
            print(f"✓ Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"✓ Connected to database: {record[0]}")
            
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"✓ Tables in database: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
            
            cursor.close()
            connection.close()
            print("✓ Connection closed")
            print("\n" + "=" * 60)
            print("Connection test PASSED")
            print("=" * 60)
            return True
        else:
            print("✗ Connection object created but not connected")
            return False
            
    except Error as e:
        print(f"\n✗ MySQL Error occurred:")
        print(f"Error Code: {e.errno}")
        print(f"Error Message: {e.msg}")
        print(f"Full Error: {e}")
        print("\nCommon causes:")
        print("  - Wrong password or username")
        print("  - Database doesn't exist")
        print("  - Access denied from your IP")
        print("\n" + "=" * 60)
        print("Connection test FAILED")
        print("=" * 60)
        return False
    except socket.timeout:
        print(f"\n✗ Connection Timeout:")
        print(f"  Connection attempt timed out after {config['connection_timeout']}s")
        print("  Possible causes:")
        print("    - Firewall blocking MySQL traffic")
        print("    - Server not responding")
        print("    - Network latency too high")
        print("\n" + "=" * 60)
        print("Connection test FAILED")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("Connection test FAILED")
        print("=" * 60)
        return False


if __name__ == "__main__":
    test_connection()
