import requests

api_key = "8603efb746f84156ac23dc6c01f2cde1"  # 你的API密钥
# Steam市场使用的是英文名称格式
market_hash_name = "Sticker | jdm64 | MLG Columbus 2016"  # 饰品英文名称

url = "https://open.steamdt.com/open/cs2/v1/price/single"
headers = {
    "Authorization": f"Bearer {api_key}"
}
params = {
    "marketHashName": market_hash_name
}

response = requests.get(url, headers=headers, params=params)
print(f"HTTP状态码: {response.status_code}")
print(f"响应内容: {response.text}")
print()

result = response.json()
print(f"解析后的结果: {result}")
print()

if result.get("success"):
    print(f"数据条数: {len(result['data'])}")
    if result["data"]:
        for item in result["data"]:
            print(f"平台: {item['platform']}")
            print(f"售价: {item['sellPrice']}")
            print(f"在售数量: {item['sellCount']}")
            print(f"求购价: {item['biddingPrice']}")
            print(f"更新时间: {item['updateTime']}")
            print("-" * 40)
    else:
        print("没有返回价格数据")
else:
    print(f"错误码: {result.get('errorCode')}")
    print(f"错误信息: {result.get('errorMsg')}")