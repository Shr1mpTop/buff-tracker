#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quota Router

Provides API quota information.
"""

from fastapi import APIRouter
from pathlib import Path
import csv

router = APIRouter()


@router.get("/quota")
async def get_quota():
    """
    Get current API quota status
    
    Returns:
        dict: Quota information
    """
    quota_file = Path(__file__).parent.parent.parent / "api_quota.csv"
    
    if not quota_file.exists():
        return {
            "success": False,
            "error": "quota_file_not_found",
            "remaining": 0,
            "total": 60
        }
    
    try:
        # Read quota file
        with open(quota_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                return {
                    "success": False,
                    "remaining": 0,
                    "total": 60
                }
            
            # Calculate total remaining quota from all API keys
            total_remaining = sum(int(row.get('price_remaining', 0)) for row in rows)
            total_quota = len(rows) * 60  # Each key has 60 requests per minute
            
            # Get current minute from latest row
            current_minute = rows[-1].get('price_minute', '') if rows else ''
            
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
