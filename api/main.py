#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CS2 Price Tracker API - FastAPI Application

Provides RESTful API for CS2 item price tracking and search functionality.
Designed to be deployed as a microservice for hezhili.online.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routers import price, search, health, quota


# Create FastAPI application
app = FastAPI(
    title="CS2 Price Tracker API",
    description="RESTful API for CS2 item price tracking and database search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS configuration - allow access from hezhili.online
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hezhili.online",
        "https://www.hezhili.online",
        "https://bufftracker.hezhili.online",
        "http://bufftracker.hezhili.online",
        "http://localhost:3000",  # Development
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(price.router, prefix="/api", tags=["Price"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(quota.router, prefix="/api", tags=["Quota"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint
    """
    return {
        "service": "CS2 Price Tracker API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "quota": "/api/quota",
            "price": "/api/price/{hashname}",
            "search": "/api/search?name={query}&num={limit}"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": str(exc)
        }
    )


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
