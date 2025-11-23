"""
Buff Tracker - SteamDT API管理工具包

用于管理SteamDT API密钥、速率限制和价格查询的Python包
"""

from .api_manager import SteamDTAPIManager, APIKeyQuota

__version__ = "1.0.0"
__author__ = "HeZhili"
__all__ = ["SteamDTAPIManager", "APIKeyQuota"]
