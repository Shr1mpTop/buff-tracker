#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Search Router

Handles fuzzy search for CS2 items in the database.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.searchName import fuzzy_search_items

router = APIRouter()


class ItemInfo(BaseModel):
    """Single item information model"""
    id: int
    name: str
    market_hash_name: str
    buff_id: Optional[str] = None
    c5_id: Optional[str] = None
    youpin_id: Optional[str] = None
    haloskins_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response model"""
    success: bool
    query: str
    count: int
    data: List[ItemInfo]


@router.get("/search", response_model=SearchResponse)
async def search_items(
    name: str = Query(..., description="Search query (supports Chinese and English)", min_length=1),
    num: int = Query(10, description="Maximum number of results", ge=1, le=100)
):
    """
    Fuzzy search CS2 items by name
    
    Searches both Chinese name and market_hash_name fields.
    Results are ranked by relevance (exact match > starts with > contains).
    
    Args:
        name: Search query string (supports partial matching)
        num: Maximum number of results to return (1-100, default: 10)
        
    Returns:
        SearchResponse: List of matching items with platform IDs
        
    Examples:
        GET /api/search?name=AK-47&num=5
        GET /api/search?name=红线&num=10
        GET /api/search?name=Redline&num=3
    """
    try:
        results = fuzzy_search_items(name, num)
        
        if not results:
            return {
                "success": False,
                "query": name,
                "count": 0,
                "data": []
            }
        
        return {
            "success": True,
            "query": name,
            "count": len(results),
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "search_failed",
                "message": str(e)
            }
        )


@router.get("/search/suggest")
async def search_suggestions(
    q: str = Query(..., description="Query string for autocomplete", min_length=1),
    limit: int = Query(5, description="Number of suggestions", ge=1, le=20)
):
    """
    Get search suggestions for autocomplete
    
    Returns simplified results optimized for autocomplete/typeahead.
    
    Args:
        q: Query string
        limit: Maximum number of suggestions (1-20, default: 5)
        
    Returns:
        List of suggested item names
        
    Example:
        GET /api/search/suggest?q=AK&limit=5
    """
    try:
        results = fuzzy_search_items(q, limit)
        
        # Return simplified format for autocomplete
        suggestions = [
            {
                "value": item["market_hash_name"],
                "label": f"{item['name']} ({item['market_hash_name']})",
                "id": item["id"]
            }
            for item in results
        ]
        
        return {
            "success": True,
            "query": q,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "suggestion_failed",
                "message": str(e)
            }
        )
