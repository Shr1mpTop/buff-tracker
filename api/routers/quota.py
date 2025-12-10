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
        cursor.execute("SELECT api_key, price_single_quota, price_batch_quota, base_quota, price_single_timestamp FROM api_keys")
        rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "error": "no_api_keys_found",
                "single_remaining": 0,
                "single_total": 0,
                "batch_remaining": 0,
                "batch_total": 0,
                "base_remaining": 0,
                "base_total": 0
            }
        
        num_keys = len(rows)
        
        # Calculate totals
        single_remaining = sum(row['price_single_quota'] for row in rows)
        single_total = num_keys * 60
        
        batch_remaining = sum(row['price_batch_quota'] for row in rows)
        batch_total = num_keys * 1
        
        base_remaining = sum(row['base_quota'] for row in rows)
        base_total = num_keys * 1
        
        # Get latest timestamp
        current_minute = max((row['price_single_timestamp'] for row in rows if row['price_single_timestamp']), default='')
        
        conn.close()
        
        return {
            "success": True,
            "single_remaining": single_remaining,
            "single_total": single_total,
            "batch_remaining": batch_remaining,
            "batch_total": batch_total,
            "base_remaining": base_remaining,
            "base_total": base_total,
            "timestamp": current_minute
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "single_remaining": 0,
            "single_total": 0,
            "batch_remaining": 0,
            "batch_total": 0,
            "base_remaining": 0,
            "base_total": 0
        }
