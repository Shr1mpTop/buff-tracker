#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Health Check Router

Provides health check and system status endpoints.
"""

from fastapi import APIRouter
from datetime import datetime
import os
from pathlib import Path

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "cs2-price-tracker",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/status")
async def system_status():
    """
    Detailed system status
    
    Returns:
        dict: Detailed system information
    """
    # Check if quota file exists
    quota_file = Path(__file__).parent.parent.parent / "api_quota.csv"
    cache_file = Path(__file__).parent.parent.parent / "cs2_kinds_cache.json"
    
    return {
        "status": "operational",
        "components": {
            "api_manager": {
                "status": "ok" if quota_file.exists() else "warning",
                "quota_file_exists": quota_file.exists()
            },
            "database": {
                "status": "ok",
                "connection": "available"
            },
            "cache": {
                "status": "ok" if cache_file.exists() else "empty",
                "cache_file_exists": cache_file.exists()
            }
        },
        "timestamp": datetime.now().isoformat()
    }
