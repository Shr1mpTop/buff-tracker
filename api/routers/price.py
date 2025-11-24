#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Price Router

Handles CS2 item price queries using the ddrager utility.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.ddrager import fetch_price

router = APIRouter()


class PriceResponse(BaseModel):
    """Price response model"""
    success: bool
    data: Optional[list] = None
    error: Optional[str] = None
    message: Optional[str] = None


@router.get("/price/{hashname}", response_model=PriceResponse)
async def get_item_price(hashname: str):
    """
    Get price data for a CS2 item by market hash name
    
    Args:
        hashname: Steam market hash name (e.g., "AK-47 | Redline (Field-Tested)")
        
    Returns:
        PriceResponse: Price data from multiple platforms
        
    Example:
        GET /api/price/AK-47 | Redline (Field-Tested)
    """
    try:
        result = fetch_price(hashname)
        
        # Check if there's an error in the result
        if isinstance(result, dict) and result.get('error'):
            raise HTTPException(
                status_code=400 if result['error'] == 'no_api_key' else 500,
                detail=result
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "fetch_failed",
                "message": str(e)
            }
        )


@router.get("/price")
async def get_price_by_query(
    hashname: str = Query(..., description="Steam market hash name")
):
    """
    Alternative endpoint: Get price by query parameter
    
    Args:
        hashname: Steam market hash name
        
    Returns:
        PriceResponse: Price data
        
    Example:
        GET /api/price?hashname=AWP | Asiimov (Field-Tested)
    """
    return await get_item_price(hashname)
