# Buff Tracker

CS2 饰品价格追踪工具 - 服务化分层架构的数据获取与管理系统

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
python utils/ddrager.py --hashname "AWP | Pit Viper (Field-Tested)"
```

## 工具集

### 1. ddrager - 价格数据获取（推荐）
自动向 api-manager 请求 API key，调用 SteamDT API 获取价格数据。

```bash
python utils/ddrager.py --hashname "AK-47 | Redline (Field-Tested)"
```

**特性:**
- ✅ 自动请求最优 API key（无需手动传入）
- ✅ 自动通知 api-manager 使用结果
- ✅ 失败自动回滚额度
- ✅ 返回原始 JSON 数据

**内部工作流程:**
1. 请求 api-manager 分配 API key
2. 调用 SteamDT API
3. 通知 api-manager 调用结果（成功/失败）

---

### 2. kinds - CS2 饰品基础信息获取
获取所有 CS2 饰品的基础信息（1 请求/天限制）。

```bash
python utils/kinds.py
```

**特性:**
- ✅ 自动请求 base 端点专用 API key
- ✅ 缓存到 `cs2_kinds_cache.json`
- ✅ 严格的 1/天限流保护

---

### 3. api-manager - API 密钥管理服务
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
python utils/api-manager.py --best price_single
```

**服务接口（供数据层调用）:**
```bash
# 分配 API key（自动扣减额度）
python utils/api-manager.py --request-key price_single

# 通知使用结果（失败则回滚额度）
python utils/api-manager.py --notify-usage --endpoint price_single --api-key KEY --success
python utils/api-manager.py --notify-usage --endpoint price_single --api-key KEY --failed
```

**职责:**
- 初始化所有 API key 到 CSV
- 查询和显示额度状态
- **提供服务接口**：分配 key、追踪额度、失败回滚
- 支持多端点：`price_single` (60/分钟), `base` (1/天)

## 设计架构

### 服务化分层设计
```
用户
  ↓
ddrager.py / kinds.py    # 数据层 - 请求服务，获取数据
  ↓ 请求 API key
  ↓ 通知使用结果
api-manager.py           # 管理层 - 提供服务，监听调用
  ↓ 读写
api_quota.csv            # 存储层 - 额度持久化
```

### 调用流程（以 ddrager 为例）
1. `ddrager` → `api-manager --request-key price_single`（获取 key，自动扣减额度）
2. `ddrager` → 调用 SteamDT API
3. `ddrager` → `api-manager --notify-usage --success/--failed`（通知结果，失败则回滚）

**核心优势:**
- ✅ **依赖倒置**：数据层主动请求，管理层提供服务
- ✅ **自动回滚**：API 调用失败时恢复已扣减额度
- ✅ **解耦彻底**：数据层无需知道额度管理实现细节

## 项目结构
```
buff-tracker/
├── utils/
│   ├── ddrager.py          # 价格数据获取（price_single 端点）
│   ├── kinds.py            # 饰品基础信息（base 端点）
│   └── api-manager.py      # API 密钥管理服务
├── docs/
│   ├── db.md               # 数据库设计文档
│   └── design.md           # 架构设计文档
├── api_quota.csv           # 额度记录（自动生成）
├── cs2_kinds_cache.json    # 饰品信息缓存
├── .env                    # API 密钥配置
├── requirements.txt        # 依赖项
└── README.md               # 本文档
```

## 输出示例

### ddrager 输出
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

### 单一职责原则
- **ddrager/kinds**: 数据层 - 纯 HTTP 请求，无额度管理逻辑
- **api-manager**: 管理层 - 只负责 key 分配与额度追踪，不调用业务 API
- **通信方式**: subprocess RPC（数据层调用管理层服务接口）

### 依赖方向
- ✅ 数据层依赖管理层（请求服务）
- ❌ 管理层不依赖数据层（被动响应）

### 错误处理
- API 调用失败时，数据层通知管理层 `--failed`
- 管理层自动回滚已扣减的额度

---

## 详细文档

- **架构设计**: 查看 `docs/design.md` 了解服务化分层架构
- **数据库设计**: 查看 `docs/db.md` 了解 cs2_items 表结构

## License

MIT
