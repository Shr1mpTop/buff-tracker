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

from utils.ddrager import fetch_price, fetch_batch_price

router = APIRouter()


class PriceResponse(BaseModel):
    """Price response model"""
    success: bool
    data: Optional[list] = None
    error: Optional[str] = None
    message: Optional[str] = None


class BatchPriceRequest(BaseModel):
    """Batch price request model"""
    hashnames: list[str]


class BatchPriceResponse(BaseModel):
    """Batch price response model"""
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


@router.post("/price/batch", response_model=BatchPriceResponse)
async def get_batch_item_prices(request: BatchPriceRequest):
    """
    Get batch price data for multiple CS2 items
    
    Args:
        request: BatchPriceRequest with list of market hash names
        
    Returns:
        BatchPriceResponse: Batch price data from SteamDT
        
    Example:
        POST /api/price/batch
        {
            "hashnames": [
                "AK-47 | Redline (Field-Tested)",
                "AWP | Asiimov (Field-Tested)"
            ]
        }
    """
    try:
        if not request.hashnames or len(request.hashnames) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "invalid_request",
                    "message": "hashnames list cannot be empty"
                }
            )
        
        if len(request.hashnames) > 100:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "batch_too_large",
                    "message": "Maximum 100 items per batch"
                }
            )
        
        result = fetch_batch_price(request.hashnames)
        
        # Check if there's an error in the result
        if isinstance(result, dict):
            if result.get('error'):
                raise HTTPException(
                    status_code=400 if result['error'] == 'no_api_key' else 500,
                    detail=result
                )
            elif result.get('success') == False:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "steamdt_error",
                        "message": result.get('errorMsg', 'SteamDT API error'),
                        "errorCode": result.get('errorCode')
                    }
                )
            elif result.get('success') == True:
                return {
                    "success": True,
                    "data": result.get('data')
                }
        
        # Fallback
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "fetch_failed",
                "message": str(e)
            }
        )
