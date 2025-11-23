#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API管理器测试脚本
用于测试SteamDTAPIManager的各项功能
"""

from api_manager import SteamDTAPIManager
import time


def test_single_query():
    """测试单个物品查询"""
    print("=" * 60)
    print("测试1: 单个物品查询")
    print("=" * 60)
    
    manager = SteamDTAPIManager()
    market_hash_name = "AK-47 | Redline (Field-Tested)"
    
    print(f"查询物品: {market_hash_name}")
    result = manager.get_price_single(market_hash_name)
    
    if result and result.get("success"):
        print(f"✓ 查询成功")
        print(f"数据条数: {len(result['data'])}")
        for item in result["data"]:
            print(f"  平台: {item['platform']}")
            print(f"  售价: {item['sellPrice']}")
            print(f"  在售数量: {item['sellCount']}")
            print(f"  求购价: {item['biddingPrice']}")
    else:
        print(f"✗ 查询失败: {result}")
    
    return manager


def test_quota_status(manager):
    """测试额度查询"""
    print("\n" + "=" * 60)
    print("测试2: 额度状态查询")
    print("=" * 60)
    
    quota_status = manager.get_quota_status()
    print(f"总密钥数: {len(quota_status)}")
    print(f"显示前5个密钥状态:")
    
    for status in quota_status[:5]:
        print(f"  {status['api_key']}: {status['remaining_quota']}/{status['total_quota']} (时间: {status['minute']})")


def test_batch_query(manager):
    """测试批量查询"""
    print("\n" + "=" * 60)
    print("测试3: 批量查询")
    print("=" * 60)
    
    test_items = [
        "AK-47 | Redline (Field-Tested)",
        "AWP | Asiimov (Field-Tested)",
        "M4A4 | Howl (Factory New)",
    ]
    
    success_count = 0
    for i, item_name in enumerate(test_items, 1):
        print(f"\n[{i}/{len(test_items)}] 查询: {item_name}")
        result = manager.get_price_single(item_name)
        
        if result and result.get("success"):
            print(f"  ✓ 成功")
            success_count += 1
        else:
            print(f"  ✗ 失败")
        
        time.sleep(0.2)  # 避免过快请求
    
    print(f"\n批量查询完成: {success_count}/{len(test_items)} 成功")


def test_api_keys_loaded(manager):
    """测试API密钥加载"""
    print("\n" + "=" * 60)
    print("测试4: API密钥加载检查")
    print("=" * 60)
    
    key_count = len(manager.API_KEYS)
    print(f"已加载API密钥数量: {key_count}")
    
    if key_count > 0:
        print(f"✓ API密钥加载成功")
        print(f"第一个密钥: {manager.API_KEYS[0][:8]}...")
        print(f"最后一个密钥: {manager.API_KEYS[-1][:8]}...")
    else:
        print(f"✗ 未加载到API密钥,请检查.env文件")


if __name__ == "__main__":
    print("\n🚀 开始测试 SteamDTAPIManager\n")
    
    # 测试API密钥加载
    test_manager = SteamDTAPIManager()
    test_api_keys_loaded(test_manager)
    
    # 测试单个查询
    manager = test_single_query()
    
    # 测试额度状态
    test_quota_status(manager)
    
    # 测试批量查询
    test_batch_query(manager)
    
    # 最后再查看一次额度
    print("\n" + "=" * 60)
    print("测试完成后的额度状态")
    print("=" * 60)
    test_quota_status(manager)
    
    print("\n✅ 所有测试完成!\n")