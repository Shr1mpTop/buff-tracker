# 便携饰品跟踪器
hi~各位导🐕中午好!我谨代表导🐕联盟设计出便携获取不同平台饰品价格的工具，我的开发计划和代码仓库都会实时更新在这里！

## RoadMap
1. ✅ 简单的查询价格 (已完成)
2. 饰品价格追踪
3. 邮箱通知
4. 实时自动交易

## 功能特性

- ✅ 支持多个API密钥自动轮询
- ✅ 智能速率限制管理(每分钟60次)
- ✅ 额度持久化存储(CSV)
- ✅ 线程安全设计
- ✅ 自动密钥切换和重试

## 安装

### 开发模式安装 (推荐)
```bash
pip install -e .
```

### 直接使用
```bash
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件，添加你的API密钥:

```env
API_KEYS=key1,key2,key3,...
```

## 使用示例

### 作为Python包使用

```python
from buff_tracker import SteamDTAPIManager

# 创建管理器实例
manager = SteamDTAPIManager()

# 查询单个物品价格
result = manager.get_price_single("AK-47 | Redline (Field-Tested)")
print(result)

# 查看当前额度状态
status = manager.get_quota_status()
for s in status[:5]:
    print(f"{s['api_key']}: {s['remaining_quota']}/{s['total_quota']}")
```

### 运行测试脚本

```bash
python test.py
```

## 项目结构

```
buff-tracker/
├── __init__.py          # 包初始化文件
├── api_manager.py       # API管理器核心代码
├── test.py             # 测试脚本
├── setup.py            # 包安装配置
├── requirements.txt    # 依赖项
├── .env               # 环境变量(API密钥)
├── .gitignore         # Git忽略文件
├── api_quota.csv      # 额度记录(自动生成)
└── README.md          # 本文件
```

## License

MIT License
