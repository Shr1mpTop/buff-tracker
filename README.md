# CS2 Price Tracker API

CS2 饰品价格追踪 API 服务，提供实时价格查询和批量数据获取。

## 功能特点

- ✅ **单价查询**：通过 Steam market hash name 获取单个饰品价格
- ✅ **批量查询**：一次查询多个饰品的完整价格数据
- ✅ **饰品搜索**：支持中英文模糊搜索 CS2 饰品
- ✅ **配额管理**：自动管理 API 调用配额，支持多种限制策略
- ✅ **实时更新**：后台自动重置过期配额
- ✅ **Docker 部署**：容器化部署，支持生产环境
- ✅ **UTC+8 时间**：所有时间戳使用北京时间

## 技术栈

- **后端**：FastAPI + Python 3.9
- **数据库**：SQLite（配额管理）
- **部署**：Docker + Docker Compose
- **外部 API**：SteamDT API

## 快速开始

### Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/Shr1mpTop/buff-tracker.git
cd buff-tracker

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 API 密钥

# 启动服务
docker-compose up --build -d

# 查看日志
docker-compose logs -f
```

### 本地开发

```bash
# 安装依赖
uv venv
uv pip sync pyproject.toml

# 配置 .env 文件

# 启动开发服务器
uvicorn api.main:app --reload --host 0.0.0.0 --port 8010
```

## API 接口

### 基础信息

- **健康检查**：`GET /api/health`
- **配额状态**：`GET /api/quota`

### 价格查询

- **单价查询**：`GET /api/price/{hashname}`
- **批量查询**：`POST /api/price/batch`

### 饰品搜索

- **搜索接口**：`GET /api/search?name={query}&num={limit}`

## 配额限制

- **单价 API**：每密钥 60 次/分钟
- **批量 API**：每密钥 1 次/分钟
- **基础 API**：每密钥 1 次/天

## 文档

启动服务后访问：

- **API 文档**：http://localhost:8010/docs
- **ReDoc**：http://localhost:8010/redoc

## 项目结构

```
buff-tracker/
├── api/
│   ├── main.py          # FastAPI 应用入口
│   └── routers/         # API 路由
├── utils/
│   ├── api_manager.py   # 配额管理
│   ├── db_manager.py    # 数据库操作
│   ├── ddrager.py       # 价格获取工具
│   └── searchName.py    # 搜索工具
├── docker-compose.yml   # Docker 编排
├── Dockerfile          # 容器配置
└── pyproject.toml      # 项目配置
```

## 许可证

MIT License
