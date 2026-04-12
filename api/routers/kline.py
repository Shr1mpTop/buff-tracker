#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kline Router

Handles CS2 item K-line (candlestick) chart data queries.
Proxies SteamDT POST /open/cs2/item/v1/kline.
"""

from fastapi import APIRouter, Query
from typing import Optional
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from utils.ddrager import fetch_kline_data

router = APIRouter()


@router.get(
    "/kline/{market_hash_name:path}",
    summary="查询饰品K线数据",
    description=(
        "中转 SteamDT `/open/cs2/item/v1/kline` 接口，返回饰品K线（蜡烛图）数据。\n\n"
        "**参数说明：**\n"
        "- `market_hash_name`（路径参数）：饰品名称，如 `AK-47 | Redline (Field-Tested)`\n"
        "- `type`（查询参数）：1=时K，2=日K（默认），3=周K\n"
        "- `platform`（查询参数，可选）：平台过滤，支持 ALL/BUFF/YOUPIN/C5/STEAM/HALOSKINS\n"
        "- `special_style`（查询参数，可选）：特殊款式\n\n"
        "**注意：每个API key每分钟限60次调用。**"
    ),
)
async def get_kline_data(
    market_hash_name: str,
    type: int = Query(default=2, ge=1, le=3, description="K线类型：1=时K，2=日K，3=周K"),
    platform: Optional[str] = Query(default=None, description="平台：ALL/BUFF/YOUPIN/C5/STEAM/HALOSKINS"),
    special_style: Optional[str] = Query(default=None, description="特殊款式"),
):
    """
    Get K-line data for a CS2 item from SteamDT API.
    """
    result = fetch_kline_data(
        market_hash_name=market_hash_name,
        kline_type=type,
        platform=platform,
        special_style=special_style,
    )

    if isinstance(result, dict) and "error" in result:
        return {
            "success": False,
            "data": None,
            "errorCode": -1,
            "errorMsg": result.get("message", result.get("error", "Unknown error")),
            "errorData": {},
            "errorCodeStr": result.get("error", ""),
        }

    return result
