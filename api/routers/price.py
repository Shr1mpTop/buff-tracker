#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Price Router

Handles CS2 item price queries using the ddrager utility.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional
import sys
import pathlib

# Add project root to path
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from utils.ddrager import fetch_price, fetch_batch_price, fetch_history_price

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


class HistoryPriceResponse(BaseModel):
    """History price response model"""
    success: bool
    data: Optional[list] = None
    error: Optional[str] = None
    message: Optional[str] = None


class BatchPriceResponse(BaseModel):
    """Batch price response model"""
    success: bool
    data: Optional[list] = None
    error: Optional[str] = None
    message: Optional[str] = None


@router.get(
    "/item/kline-data/{market_hash_name}",
    response_model=HistoryPriceResponse,
    summary="获取饰品历史价格趋势",
    description=(
        "通过 Steam 市场哈希名称在指定平台上查询历史价格趋势数据。\n\n"
        "内部使用无头浏览器访问 steamdt.com（绕过阿里云 WAF），\n"
        "拦截页面对 `/user/steam/type-trend/v2/item/details` 的原生 POST 请求，"
        "并将 body 替换为指定的 `platform` / `typeDay` / `dateType` 参数后返回响应。\n\n"
        "**注意**: 首次请求需启动浏览器，耗时约 10-20 秒。"
    ),
)
async def get_item_kline_data(
    market_hash_name: str = Path(
        ...,
        description="Steam 市场哈希名称，含特殊字符时需 URL 编码",
        openapi_examples={
            "m4a4": {"summary": "M4A4 | Buzz Kill (FN)", "value": "M4A4 | Buzz Kill (Factory New)"},
            "ak47": {"summary": "AK-47 | 红线 (FT)", "value": "AK-47 | Redline (Field-Tested)"},
            "awp":  {"summary": "AWP | 亚洲人 (FT)",  "value": "AWP | Asiimov (Field-Tested)"},
        },
    ),
    platform: str = Query(
        "STEAM",
        description="平台标识符",
        openapi_examples={
            "steam":  {"summary": "Steam",   "value": "STEAM"},
            "youpin": {"summary": "悠悠有品", "value": "YOUPIN"},
            "buff":   {"summary": "BUFF",    "value": "BUFF"},
            "c5":     {"summary": "C5",      "value": "C5"},
        },
    ),
    type_day: str = Query(
        "5",
        description="K 线聚合周期（天）",
        openapi_examples={
            "1d":  {"summary": "1 天",  "value": "1"},
            "3d":  {"summary": "3 天",  "value": "3"},
            "5d":  {"summary": "5 天",  "value": "5"},
            "7d":  {"summary": "7 天",  "value": "7"},
            "30d": {"summary": "30 天", "value": "30"},
        },
    ),
    date_type: int = Query(3, description="日期范围类型（3 = 全量历史）"),
):
    """
    Get K-line (candlestick) historical price data for a CS2 item on a specific platform.

    Uses a headless browser to navigate steamdt.com (bypassing Aliyun WAF),
    then POSTs to /user/steam/type-trend/v2/item/details with the given params.

    Args:
        market_hash_name: Steam market hash name, e.g. "M4A4 | Buzz Kill (Factory New)"
        platform:         Platform identifier (default: STEAM)
        type_day:         Aggregation period in days (default: 5)
        date_type:        Date range type (default: 3)

    Returns:
        HistoryPriceResponse: K-line price trend data

    Example:
        GET /api/item/kline-data/M4A4%20%7C%20Buzz%20Kill%20(Factory%20New)?platform=YOUPIN&type_day=5
    """
    try:
        result = await fetch_history_price(market_hash_name, platform, type_day, date_type)

        if isinstance(result, dict) and result.get("error"):
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": result["error"],
                    "message": result.get("message", ""),
                },
            )

        if isinstance(result, dict) and result.get("success") is False:
            raise HTTPException(
                status_code=502,
                detail={
                    "success": False,
                    "error": "steamdt_error",
                    "message": result.get("errorMsg") or "SteamDT API error",
                },
            )

        return {
            "success": True,
            "data": result.get("data"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "fetch_failed", "message": str(e)},
        )


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
