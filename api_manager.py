import requests
import threading
import time
import csv
import os
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class APIKeyQuota:
    """API密钥额度信息"""
    api_key: str
    minute_timestamp: str  
    remaining_quota: int  


# 加载环境变量
load_dotenv()

class SteamDTAPIManager:
    """SteamDT API管理器 - 支持自动密钥轮询和速率限制管理"""
    
    # 从环境变量加载API密钥列表
    API_KEYS = os.getenv('API_KEYS', '').split(',') if os.getenv('API_KEYS') else []
    
    # 速率限制配置
    RATE_LIMITS = {
        "price_single": 60,  # 每分钟60次
    }
    
    # API端点
    API_ENDPOINTS = {
        "price_single": "https://open.steamdt.com/open/cs2/v1/price/single",
    }
    
    def __init__(self, quota_file: str = "api_quota.csv"):
        """
        初始化API管理器
        
        Args:
            quota_file: 额度记录文件路径
        """
        self.quota_file = Path(quota_file)
        self.lock = threading.Lock()
        self.quota_cache: Dict[str, Dict[str, any]] = {}  # {api_key: {'remaining_quota': int, 'minute_timestamp': str}}
        self._load_quota()
    
    def _get_current_minute(self) -> str:
        """获取当前分钟时间戳（UTC+8）"""
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def _load_quota(self):
        """从CSV文件加载额度信息"""
        if not self.quota_file.exists():
            # 如果文件不存在，初始化所有密钥
            self._initialize_quota()
            return
        
        try:
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    api_key = row['api_key']
                    remaining = int(row['remaining_quota'])
                    minute = row['minute_timestamp']
                    
                    self.quota_cache[api_key] = {
                        'remaining_quota': remaining,
                        'minute_timestamp': minute
                    }
        except Exception as e:
            print(f"Failed to load quota file: {e}")
            self._initialize_quota()
    
    def _initialize_quota(self):
        """初始化所有API密钥的额度"""
        current_minute = self._get_current_minute()
        for api_key in self.API_KEYS:
            self.quota_cache[api_key] = {
                'remaining_quota': self.RATE_LIMITS["price_single"],
                'minute_timestamp': current_minute
            }
        self._save_quota()
    
    def _save_quota(self):
        """保存额度信息到CSV文件"""
        try:
            with open(self.quota_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['api_key', 'remaining_quota', 'minute_timestamp'])
                
                for api_key in self.API_KEYS:
                    if api_key in self.quota_cache:
                        info = self.quota_cache[api_key]
                        writer.writerow([api_key, info['remaining_quota'], info['minute_timestamp']])
                    else:
                        # 如果缓存中没有，写入默认值
                        current_minute = self._get_current_minute()
                        writer.writerow([api_key, self.RATE_LIMITS["price_single"], current_minute])
        except Exception as e:
            print(f"Failed to save quota file: {e}")
    
    def _get_available_api_key(self, rate_limit: int) -> Optional[str]:
        """
        获取一个有剩余额度的API密钥
        
        Args:
            rate_limit: 该接口的速率限制
            
        Returns:
            可用的API密钥，如果所有密钥都用完则返回None
        """
        current_minute = self._get_current_minute()
        
        with self.lock:
            # 查找有剩余额度的密钥
            for api_key in self.API_KEYS:
                # 确保密钥在缓存中
                if api_key not in self.quota_cache:
                    self.quota_cache[api_key] = {
                        'remaining_quota': rate_limit,
                        'minute_timestamp': current_minute
                    }
                
                quota_info = self.quota_cache[api_key]
                
                # 对比当前时间和记录时间
                if quota_info['minute_timestamp'] != current_minute:
                    # 分钟不一致，恢复额度到60
                    quota_info['remaining_quota'] = rate_limit
                    quota_info['minute_timestamp'] = current_minute
                
                # 如果有剩余额度，使用这个密钥
                if quota_info['remaining_quota'] > 0:
                    quota_info['remaining_quota'] -= 1
                    self._save_quota()
                    return api_key
            
            return None
    
    def _cleanup_old_quota(self):
        """清理超过2分钟的旧额度记录"""
        current_time = datetime.now()
        
        for api_key in list(self.quota_cache.keys()):
            for minute in list(self.quota_cache[api_key].keys()):
                try:
                    record_time = datetime.strptime(minute, "%Y-%m-%d %H:%M")
                    # 如果记录超过2分钟，删除
                    if (current_time - record_time).total_seconds() > 120:
                        del self.quota_cache[api_key][minute]
                except:
                    pass
    
    def get_price_single(self, market_hash_name: str, max_retries: int = 3, retry_delay: int = 1) -> Optional[Dict]:
        """
        查询单个饰品价格
        
        Args:
            market_hash_name: Steam市场饰品名称（英文）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            价格数据字典，失败返回None
        """
        rate_limit = self.RATE_LIMITS["price_single"]
        url = self.API_ENDPOINTS["price_single"]
        
        for attempt in range(max_retries):
            # Get available API key
            api_key = self._get_available_api_key(rate_limit)
            
            if api_key is None:
                print(f"All API keys exhausted for current minute, waiting {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            
            # 发起请求
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            params = {
                "marketHashName": market_hash_name
            }
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    return result
                elif response.status_code == 429:
                    # 速率限制，标记该密钥本分钟额度用完
                    with self.lock:
                        if api_key in self.quota_cache:
                            self.quota_cache[api_key]['remaining_quota'] = 0
                            self._save_quota()
                    print(f"Rate limit hit for {api_key[:8]}..., trying next key")
                    continue
                else:
                    print(f"HTTP error: {response.status_code}, {response.text}")
                    
            except Exception as e:
                print(f"Request exception: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        print(f"Failed to get price after {max_retries} retries")
        return None
    
    def get_quota_status(self) -> List[Dict]:
        """
        获取所有API密钥的当前额度状态
        
        Returns:
            额度状态列表
        """
        current_minute = self._get_current_minute()
        status = []
        
        with self.lock:
            for api_key in self.API_KEYS:
                if api_key in self.quota_cache:
                    quota_info = self.quota_cache[api_key]
                    
                    # 如果分钟不一致，显示恢复后的额度
                    if quota_info['minute_timestamp'] != current_minute:
                        remaining = self.RATE_LIMITS["price_single"]
                    else:
                        remaining = quota_info['remaining_quota']
                else:
                    remaining = self.RATE_LIMITS["price_single"]
                
                status.append({
                    "api_key": f"{api_key[:8]}...{api_key[-4:]}",
                    "remaining_quota": remaining,
                    "total_quota": self.RATE_LIMITS["price_single"],
                    "minute": quota_info['minute_timestamp'] if api_key in self.quota_cache else current_minute
                })
        
        return status
    
    def _cleanup_old_quota(self):
        """此方法不再需要，保留以兼容"""
        pass


# 使用示例
if __name__ == "__main__":
    # 确保已安装 python-dotenv: pip install python-dotenv
    manager = SteamDTAPIManager()
    
    print("=" * 60)
    print("Test 1: Single item query")
    print("=" * 60)
    
    market_hash_name = "Sticker | jdm64 | MLG Columbus 2016"
    result = manager.get_price_single(market_hash_name)
    print(result)
    
    print("\n" + "=" * 60)
    print("Test 2: Quota status")
    print("=" * 60)
    
    quota_status = manager.get_quota_status()
    for status in quota_status[:5]:
        print(f"{status['api_key']}: {status['remaining_quota']}/{status['total_quota']}")
    print(f"... Total {len(quota_status)} keys")
    
    print("\n" + "=" * 60)
    print("Test 3: Batch query")
    print("=" * 60)
    
    test_items = [
        "★ Bayonet | Marble Fade (Minimal Wear)",
        "★ Karambit | Scorched (Factory New)",
        "StatTrak™ SSG 08 | Big Iron (Well-Worn)",
    ]
    
    for item_name in test_items:
        print(f"\n{item_name}:")
        result = manager.get_price_single(item_name)
        print(result)
        time.sleep(0.1)
