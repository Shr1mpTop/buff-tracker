# Buff Tracker

CS2 饰品价格追踪工具 - 模块化设计的数据获取与管理系统

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置 API 密钥
创建 `.env` 文件:
```env
API_KEYS=key1,key2,key3,...
```

### 获取价格数据
```bash
python get_price.py --hashname "AK-47 | Redline (Field-Tested)"
```

## 工具集

### 1. get_price - 智能价格获取（推荐）
自动选择剩余额度最多的 API key，获取价格数据。

```bash
python get_price.py --hashname "AK-47 | Redline (Field-Tested)"
```

**特性:**
- ✅ 自动分配最优 API key
- ✅ 智能额度管理
- ✅ 返回原始 JSON 数据

---

### 2. ddrager - 核心数据获取
底层数据获取工具，直接调用 SteamDT API。

```bash
python utils/ddrager.py --apikey YOUR_KEY --hashname "AK-47 | Redline (Field-Tested)"
```

**职责:**
- 纯数据获取，返回 API 原始响应
- 更新指定 API key 的额度记录
- 可被其他工具调用

---

### 3. api-manager - API 密钥管理
管理所有 API key 的额度状态。

**初始化所有密钥:**
```bash
python utils/api-manager.py --init
```

**查看所有密钥额度:**
```bash
python utils/api-manager.py
```

**查看指定密钥额度:**
```bash
python utils/api-manager.py --api-key YOUR_KEY
```

**获取最优密钥:**
```bash
python utils/api-manager.py --best
```

**职责:**
- 初始化所有 API key 到 CSV
- 查询和显示额度状态
- 选择剩余额度最多的 key

## 设计架构

### 职责分离
```
get_price.py          # 业务层 - 智能调用
    ↓ 调用
api-manager.py        # 管理层 - 额度管理
    ↓ 提供最优 key
ddrager.py           # 数据层 - 纯数据获取
    ↓ 更新额度
api_quota.csv        # 存储层 - 额度持久化
```

### 数据流
1. `get_price` 调用 `api-manager --init` 确保所有 key 初始化
2. `get_price` 调用 `api-manager --best` 获取最优 key
3. `get_price` 调用 `ddrager` 使用最优 key 获取数据
4. `ddrager` 更新该 key 的额度到 CSV
5. 返回原始 JSON 数据

## 项目结构
```
buff-tracker/
├── get_price.py         # 智能价格获取工具
├── utils/
│   ├── ddrager.py       # 核心数据获取
│   └── api-manager.py   # API 密钥管理
├── api_quota.csv        # 额度记录（自动生成）
├── .env                 # API 密钥配置
├── requirements.txt     # 依赖项
└── README.md            # 本文档
```

## 输出示例

### get_price 输出
```json
{
  "success": true,
  "data": [
    {
      "platform": "BUFF",
      "sellPrice": 35.0,
      "sellCount": 19,
      "biddingPrice": 23.1,
      "biddingCount": 3,
      "updateTime": 1763904901
    },
    ...
  ]
}
```

### api-manager 输出
```
8603efb7...cde1: 59/60
50362887...6613: 60/60
eb8128a3...9641: 60/60
...
Total: 1919/1920
```

## 开发规范

- **ddrager**: 只负责数据获取，不包含业务逻辑
- **api-manager**: 只负责额度管理，不调用 API
- **get_price**: 协调调用，实现智能分配

## License

MIT
