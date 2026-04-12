#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base Router

Handles CS2 item base info queries (proxies SteamDT /open/cs2/v1/base).
Note: This upstream API can only be called once per day per key.
"""

from fastapi import APIRouter
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from utils.ddrager import fetch_base_info

router = APIRouter()


@router.get(
    "/base",
    summary="获取Steam饰品基础信息",
    description="中转 SteamDT /open/cs2/v1/base 接口，返回所有CS2饰品的基础信息（名称、marketHashName、各平台itemId）。\n\n**注意：该上游接口每天每个key只能调用一次。**",
)
async def get_base_info():
    """
    Get base info for all CS2 items from SteamDT API.
    """
    result = fetch_base_info()

    if "error" in result:
        return {
            "success": False,
            "data": None,
            "errorCode": -1,
            "errorMsg": result.get("message", result.get("error", "Unknown error")),
            "errorData": {},
            "errorCodeStr": result.get("error", ""),
        }

    return result
