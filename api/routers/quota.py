#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quota Router

Provides API quota information.
"""

from fastapi import APIRouter
from utils.db_manager import get_db_connection

router = APIRouter()


@router.get("/quota")
async def get_quota():
    """
    Get current API quota status
    
    Returns:
        dict: Quota information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query all API keys and their quotas
        cursor.execute("SELECT api_key, price_single_quota, price_single_timestamp FROM api_keys")
        rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "error": "no_api_keys_found",
                "remaining": 0,
                "total": 0
            }
        
        # Calculate total remaining quota from all API keys
        total_remaining = sum(row['price_single_quota'] for row in rows)
        total_quota = len(rows) * 60  # Each key has 60 requests per minute
        
        # Get latest timestamp
        current_minute = max((row['price_single_timestamp'] for row in rows if row['price_single_timestamp']), default='')
        
        conn.close()
        
        return {
            "success": True,
            "remaining": total_remaining,
            "total": total_quota,
            "timestamp": current_minute
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "remaining": 0,
            "total": 60
        }
