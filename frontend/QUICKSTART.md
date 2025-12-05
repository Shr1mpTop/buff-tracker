# CS2 Price Tracker - 快速启动指南

## 🚀 本地开发

### 前置要求

- Node.js 16+ 
- npm 或 yarn
- Python 3.11+ (后端 API)
- 运行中的后端服务 (localhost:8000)

### 1️⃣ 安装依赖

```bash
cd frontend
npm install
```

### 2️⃣ 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3️⃣ 启动后端 API

在另一个终端窗口：

```bash
cd ..
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档: http://localhost:8000/docs

---

## 📦 生产构建

### 构建前端

```bash
npm run build
```

生成的文件在 `dist/` 目录

### 预览构建

```bash
npm run preview
```

---

## 🎯 功能测试清单

### 搜索功能
- [ ] 输入 "AK-47" 搜索
- [ ] 输入 2 个字符后显示自动补全建议
- [ ] 点击建议项自动搜索
- [ ] 搜索结果显示在网格中
- [ ] 空搜索提示错误

### 价格查询
- [ ] 点击搜索结果项
- [ ] 显示加载状态
- [ ] 价格卡片显示多平台数据
- [ ] 刷新价格按钮功能
- [ ] 错误状态显示和重试

### API 配额监控
- [ ] 右上角实时显示剩余次数
- [ ] 每 5 秒自动刷新
- [ ] 状态显示 ONLINE/OFFLINE
- [ ] 延迟时间显示

### 用户体验
- [ ] Matrix 背景动画流畅
- [ ] Toast 通知正常显示
- [ ] 响应式布局（桌面/平板/手机）
- [ ] 光标闪烁动画
- [ ] 悬停效果和过渡动画

---

## 🔧 环境配置

### 开发环境 (.env.local)

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 生产环境 (.env.production)

```env
VITE_API_BASE_URL=https://hezhili.online/cs2-api
```

---

## 🐛 故障排查

### 问题：搜索无结果

**原因**：后端 API 未运行

**解决**：
```bash
# 检查后端状态
curl http://localhost:8000/api/health

# 如果失败，启动后端
uvicorn api.main:app --reload
```

### 问题：CORS 错误

**原因**：跨域请求被阻止

**解决**：在 `api/main.py` 中添加允许的源：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 添加前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题：API 配额显示 0

**原因**：API 管理器未运行或配额耗尽

**解决**：
```bash
# 检查 api_quota.csv 文件
cat ../api_quota.csv

# 等待下一分钟配额重置
```

### 问题：Matrix 背景不显示

**原因**：Canvas 渲染问题

**解决**：
- 检查浏览器控制台错误
- 刷新页面
- 清除浏览器缓存

---

## 📊 性能优化

### 构建优化

```javascript
// vite.config.js
export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'axios']
        }
      }
    }
  }
})
```

### 图片优化

- 使用 WebP 格式
- 懒加载图片
- 使用 CDN

### API 优化

- 启用 HTTP/2
- 使用 Redis 缓存
- 设置合理的请求超时

---

## 🔐 安全建议

### 生产环境

1. **HTTPS 加密**
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
}
```

2. **API 速率限制**
```python
# 在后端添加
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/search")
@limiter.limit("10/minute")
async def search_items(...):
    ...
```

3. **输入验证**
- 前端：限制搜索关键词长度
- 后端：Pydantic 模型验证

4. **环境变量保护**
- 不要在代码中硬编码 API 密钥
- 使用 `.env` 文件（不提交到 Git）

---

## 📝 开发笔记

### 技术栈

- **前端框架**: Vue 3 (Composition API)
- **构建工具**: Vite 5
- **HTTP 客户端**: Axios
- **样式**: 纯 CSS3 (Matrix 主题)

### 目录结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── CS2Tracker.vue      # 主组件
│   │   └── MatrixBackground.vue # 背景动画
│   ├── css/
│   │   └── cs2-tracker.css     # 样式文件
│   ├── services/
│   │   └── api.js              # API 封装
│   ├── App.vue                 # 根组件
│   ├── main.js                 # 入口文件
│   └── style.css               # 全局样式
├── index.html
├── package.json
└── vite.config.js
```

### API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/status` | GET | 系统状态（包含配额） |
| `/api/search` | GET | 搜索饰品 |
| `/api/search/suggest` | GET | 搜索建议 |
| `/api/price/{hashname}` | GET | 获取价格 |

### 状态管理

使用 Vue 3 Composition API 的 `ref` 和 `computed`：

```javascript
const searchQuery = ref('')           // 搜索输入
const searchResults = ref([])         // 搜索结果
const selectedItem = ref(null)        // 选中项
const priceData = ref(null)           // 价格数据
const apiQuota = ref(60)              // API 配额
```

---

## 🎨 设计规范

### 配色方案

```css
/* 主色调 */
--primary-green: #00ff41;      /* 主绿色 */
--secondary-green: #00ff7f;    /* 次绿色 */
--light-green: #9fffbf;        /* 浅绿色 */

/* 背景 */
--bg-black: rgba(0,0,0,0.85);  /* 主背景 */
--bg-dark: rgba(0,0,0,0.5);    /* 次背景 */

/* 边框 */
--border-green: rgba(0,255,127,0.3);
```

### 字体

```css
font-family: 'Source Code Pro', Consolas, Monaco, 'Courier New', monospace;
```

### 动画

- **闪烁光标**: 1s 无限循环
- **旋转加载**: 1s 线性无限
- **淡入淡出**: 0.3s ease
- **悬停过渡**: 0.3s ease

---

## 📞 支持

如有问题，请查看：

- [FastAPI 文档](../docs/api.md)
- [集成指南](./INTEGRATION.md)
- [项目 README](./README.md)

或在 GitHub 创建 Issue: https://github.com/Shr1mpTop/buff-tracker
