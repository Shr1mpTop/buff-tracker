# 便携饰品跟踪器
hi~各位导🐕中午好!我谨代表导🐕联盟设计出便携获取不同平台饰品价格的工具，我的开发计划和代码仓库都会实时更新在这里！

## RoadMap
1. ✅ 简单的查询价格 (已完成)
2. 饰品价格追踪
3. 邮箱通知
4. 实时自动交易

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
创建 `.env` 文件，添加你的SteamDT API密钥:
```env
API_KEYS=key1,key2,key3,...
```

### 3. 使用示例

```python
from api_manager import SteamDTAPIManager

# 创建管理器
manager = SteamDTAPIManager()

# 查询价格
result = manager.get_price_single("AK-47 | Redline (Field-Tested)")
print(result)

# 查看额度
status = manager.get_quota_status()
for s in status[:5]:
    print(f"{s['api_key']}: {s['remaining_quota']}/{s['total_quota']}")
```

### 4. 运行测试
```bash
python test.py
```

## 项目结构

```
buff-tracker/
├── api_manager.py      # API管理器
├── test.py            # 测试脚本
├── requirements.txt   # 依赖项
├── .env              # API密钥配置
└── README.md         # 说明文档
```
