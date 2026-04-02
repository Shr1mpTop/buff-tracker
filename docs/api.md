# API 文档

CS2 Price Tracker FastAPI 服务文档

## 基本信息

- **Base URL**: `http://localhost:8000` (开发环境)
- **Production URL**: `https://api.hezhili.online/cs2` (生产环境)
- **API 文档**: `/docs` (Swagger UI)
- **备用文档**: `/redoc` (ReDoc)

## 快速开始

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python api/main.py

# 或使用 uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
# 构建镜像
docker build -t cs2-tracker-api .

# 运行容器
docker run -p 8000:8000 --env-file .env cs2-tracker-api

# 或使用 docker-compose
docker-compose up -d
```

---

## API 端点

### 1. 健康检查

#### `GET /api/health`

检查服务运行状态

**响应示例:**

```json
{
  "status": "healthy",
  "service": "cs2-price-tracker",
  "timestamp": "2025-11-25T10:30:00",
  "version": "1.0.0"
}
```

#### `GET /api/status`

获取详细系统状态

**响应示例:**

```json
{
  "status": "operational",
  "components": {
    "api_manager": {
      "status": "ok",
      "quota_file_exists": true
    },
    "database": {
      "status": "ok",
      "connection": "available"
    },
    "cache": {
      "status": "ok",
      "cache_file_exists": true
    }
  },
  "timestamp": "2025-11-25T10:30:00"
}
```

---

### 2. 价格查询

#### `GET /api/price/{hashname}`

根据 Steam 市场 Hash 名称获取饰品价格

**路径参数:**

- `hashname` (string, required): Steam 市场 Hash 名称

**请求示例:**

```bash
GET /api/price/AK-47 | Redline (Field-Tested)
```

**响应示例:**

```json
{
  "success": true,
  "data": [
    {
      "platform": "BUFF",
      "platformItemId": "33960",
      "sellPrice": 231.0,
      "sellCount": 8975,
      "biddingPrice": 226.0,
      "biddingCount": 281,
      "updateTime": 1763999115
    },
    {
      "platform": "C5",
      "platformItemId": "22499",
      "sellPrice": 230.7,
      "sellCount": 1725,
      "biddingPrice": 450.0,
      "biddingCount": 123,
      "updateTime": 1763999114
    }
  ]
}
```

#### `GET /api/price?hashname={name}`

查询参数版本的价格查询

**查询参数:**

- `hashname` (string, required): Steam 市场 Hash 名称

---

#### `GET /api/item/kline-data/{market_hash_name}`

获取指定饰品在特定平台上的历史价格趋势数据（K 线聚合）。

内部使用无头浏览器访问 steamdt.com，拦截页面对 `/user/steam/type-trend/v2/item/details` 的原生 POST 请求并替换参数（绕过阿里云 WAF JS 挑战），首次请求约耗时 10–20 秒。

**路径参数:**

| 参数       | 类型   | 必填 | 说明                                                   |
| ---------- | ------ | ---- | ------------------------------------------------------ |
| `hashname` | string | ✅   | Steam 市场哈希名称，含空格/竖线等特殊字符时须 URL 编码 |

**查询参数:**

| 参数        | 类型    | 必填 | 默认值  | 可选值                       | 说明                         |
| ----------- | ------- | ---- | ------- | ---------------------------- | ---------------------------- |
| `platform`  | string  | ❌   | `STEAM` | `STEAM` `YOUPIN` `BUFF` `C5` | 目标平台标识符               |
| `type_day`  | string  | ❌   | `5`     | `1` `3` `5` `7` `14` `30`    | K 线聚合周期（天）           |
| `date_type` | integer | ❌   | `3`     | `3`                          | 日期范围类型（3 = 全量历史） |

**请求示例:**

```bash
# YOUPIN 平台，5 天聚合，全量历史
GET /api/item/kline-data/M4A4%20%7C%20Buzz%20Kill%20(Factory%20New)?platform=YOUPIN&type_day=5

# BUFF 平台，1 天聚合
GET /api/item/kline-data/AK-47%20%7C%20Redline%20(Field-Tested)?platform=BUFF&type_day=1
```

**PowerShell 测试:**

```powershell
Invoke-RestMethod "http://localhost:8000/api/item/kline-data/M4A4%20%7C%20Buzz%20Kill%20(Factory%20New)?platform=YOUPIN&type_day=5" | ConvertTo-Json -Depth 3
```

**响应示例:**

```json
{
  "success": true,
  "data": [
    ["1766505559", 6966.0, 1020, 6830.0, 63, 214656.53, 30, "25690"],
    ["1766591959", 6149.0, 1064, 6090.0, 54, 361002.26, 54, "25705"]
  ]
}
```

**data 数组字段说明（每条记录为数组，按索引）:**

| 索引 | 描述                      |
| ---- | ------------------------- |
| 0    | 时间戳（Unix 秒，字符串） |
| 1    | 最高价（CNY）             |
| 2    | 成交量                    |
| 3    | 最低价（CNY）             |
| 4    | 成交笔数                  |
| 5    | 成交额（CNY）             |
| 6    | 未知字段                  |
| 7    | 未知字段                  |

**Swagger UI 测试入口:** `http://localhost:8000/docs` → `GET /api/item/kline-data/{market_hash_name}`

---

### 3. 饰品搜索

#### `GET /api/search`

模糊搜索 CS2 饰品

**查询参数:**

- `name` (string, required): 搜索关键词（支持中英文）
- `num` (integer, optional): 返回结果数量，默认 10，范围 1-100

**请求示例:**

```bash
GET /api/search?name=AK-47&num=5
GET /api/search?name=红线&num=10
```

**响应示例:**

```json
{
  "success": true,
  "query": "红线",
  "count": 3,
  "data": [
    {
      "id": 187,
      "name": "AK-47 | 红线 (久经沙场)",
      "market_hash_name": "AK-47 | Redline (Field-Tested)",
      "buff_id": "33960",
      "c5_id": "22499",
      "youpin_id": "1414",
      "haloskins_id": "22499"
    }
  ]
}
```

#### `GET /api/search/suggest`

自动补全建议（用于前端输入框）

**查询参数:**

- `q` (string, required): 查询字符串
- `limit` (integer, optional): 建议数量，默认 5，范围 1-20

**请求示例:**

```bash
GET /api/search/suggest?q=AK&limit=5
```

**响应示例:**

```json
{
  "success": true,
  "query": "AK",
  "suggestions": [
    {
      "value": "AK-47 | Redline (Field-Tested)",
      "label": "AK-47 | 红线 (久经沙场) (AK-47 | Redline (Field-Tested))",
      "id": 187
    }
  ]
}
```

---

## 错误处理

所有错误响应遵循统一格式：

```json
{
  "success": false,
  "error": "error_code",
  "message": "详细错误信息"
}
```

**常见错误码:**

- `no_api_key`: 没有可用的 API 密钥
- `fetch_failed`: 数据获取失败
- `search_failed`: 搜索失败
- `internal_server_error`: 服务器内部错误

**HTTP 状态码:**

- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器错误

---

## CORS 配置

API 允许以下来源跨域访问：

- `https://hezhili.online`
- `https://www.hezhili.online`
- `http://localhost:3000` (开发环境)
- `http://localhost:5173` (Vite 开发服务器)

---

## 前端集成示例

### JavaScript/Fetch

```javascript
// 搜索饰品
async function searchItems(query) {
  const response = await fetch(
    `https://api.hezhili.online/cs2/search?name=${encodeURIComponent(query)}&num=10`,
  );
  const data = await response.json();
  return data;
}

// 获取价格
async function getPrice(hashname) {
  const response = await fetch(
    `https://api.hezhili.online/cs2/price/${encodeURIComponent(hashname)}`,
  );
  const data = await response.json();
  return data;
}
```

### React 示例

```jsx
import { useState, useEffect } from "react";

function CS2PriceTracker() {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const response = await fetch(
      `https://api.hezhili.online/cs2/search?name=${searchQuery}&num=10`,
    );
    const data = await response.json();
    setResults(data.data);
  };

  return (
    <div>
      <input
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="搜索饰品..."
      />
      <button onClick={handleSearch}>搜索</button>

      <div>
        {results.map((item) => (
          <div key={item.id}>{item.market_hash_name}</div>
        ))}
      </div>
    </div>
  );
}
```

---

## 性能优化

1. **缓存策略**: 价格数据建议缓存 1-5 分钟
2. **搜索防抖**: 前端搜索建议使用 debounce（300-500ms）
3. **分页**: 搜索结果使用 `num` 参数控制数量
4. **并发限制**: 建议前端限制并发请求数

---

## 监控与日志

- **健康检查**: `/api/health` (用于负载均衡器)
- **系统状态**: `/api/status` (用于监控仪表板)
- **日志级别**: INFO (生产环境), DEBUG (开发环境)

---

## 部署建议

### Nginx 反向代理配置

```nginx
location /cs2 {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Systemd 服务配置

```ini
[Unit]
Description=CS2 Price Tracker API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/buff-tracker
ExecStart=/usr/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 安全建议

1. ✅ 使用 HTTPS (生产环境)
2. ✅ 配置 CORS 白名单
3. ✅ 限制 API 请求频率（使用 slowapi 或 Nginx rate limit）
4. ✅ 定期更新依赖
5. ✅ 使用非 root 用户运行（Docker 已配置）

---

## 许可证

MIT License
