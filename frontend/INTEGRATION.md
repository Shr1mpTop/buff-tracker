# CS2 Price Tracker - 集成到 hezhili.online

## 方式一：作为独立路由页面（推荐）

### 1. 复制组件到 hezhili.online 项目

将以下文件复制到你的 hezhili.online 项目：

```
hezhili.online/frontend/src/
├── components/
│   └── CS2Tracker.vue          # 复制此文件
├── css/
│   └── cs2-tracker.css         # 复制此文件
└── services/
    └── api.js                  # 复制此文件（如果没有类似的API服务）
```

### 2. 修改 hezhili.online 的 App.vue

在 `App.vue` 中添加 CS2 Tracker 路由：

```vue
<template>
  <div class="app">
    <MatrixBackground />
    <Sidebar @navigate="handleNavigate" />
    <main class="main-content">
      <!-- 现有页面 -->
      <div v-if="currentView === 'home'">...</div>
      <Projects v-else-if="currentView === 'projects'" @navigate="handleNavigate" />
      <About v-else-if="currentView === 'profile'" />
      <Blog v-else-if="currentView === 'blog'" @navigate="handleNavigate" />
      
      <!-- 新增：CS2 Tracker 页面 -->
      <CS2Tracker v-else-if="currentView === 'cs2'" />
      
    </main>
  </div>
</template>

<script>
import CS2Tracker from './components/CS2Tracker.vue'  // 导入组件

export default {
  components: {
    // ... 现有组件
    CS2Tracker  // 注册组件
  },
  // ... 其他代码
}
</script>
```

### 3. 添加侧边栏导航项

在 `Sidebar.vue` 中添加 CS2 Tracker 的导航选项：

```vue
<template>
  <aside class="sidebar">
    <!-- 现有导航项 -->
    <button @click="navigate('home')">🏠 Home</button>
    <button @click="navigate('projects')">📂 Projects</button>
    <button @click="navigate('profile')">👤 About</button>
    <button @click="navigate('blog')">📝 Blog</button>
    
    <!-- 新增：CS2 Tracker -->
    <button @click="navigate('cs2')">🎮 CS2 Tracker</button>
  </aside>
</template>
```

### 4. 配置环境变量

在 hezhili.online 项目的 `.env` 文件中添加：

```env
# API Base URL
VITE_API_BASE_URL=https://hezhili.online/cs2-api
```

或者在本地开发时：

```env
# .env.local (本地开发)
VITE_API_BASE_URL=http://localhost:8000
```

### 5. 配置 Nginx 反向代理

在你的服务器上配置 Nginx：

```nginx
server {
    listen 80;
    server_name hezhili.online;

    # 前端静态文件
    location / {
        root /var/www/hezhili.online/dist;
        try_files $uri $uri/ /index.html;
    }

    # CS2 Tracker API 代理
    location /cs2-api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 方式二：作为 Projects 列表项

如果你想把 CS2 Tracker 作为项目展示在 Projects 页面：

### 1. 修改 Projects.vue

在项目列表中添加 CS2 Tracker：

```javascript
const projects = [
  // ... 现有项目
  {
    id: 5,
    title: 'CS2 Price Tracker',
    description: 'Counter-Strike 2 饰品价格实时追踪系统，支持多平台价格对比、智能搜索和 API 配额监控',
    url: '/cs2',  // 内部路由
    image: '🎮'
  }
]
```

### 2. 处理内部路由

在 `projectInternalKey` 函数中添加映射：

```javascript
const projectInternalKey = (url) => {
  if (!url) return 'home'
  if (url === '/') return 'home'
  if (url.startsWith('/about')) return 'profile'
  if (url.startsWith('/buffotte')) return 'buffotte'
  if (url.startsWith('/blog')) return 'blog'
  if (url.startsWith('/cs2')) return 'cs2'  // 新增
  return 'home'
}
```

---

## 方式三：嵌入现有 Buffotte 页面

如果你想替换或增强现有的 Buffotte 报告页面：

### 1. 替换 BuffotteReport.vue

直接将 `CS2Tracker.vue` 重命名为 `BuffotteReport.vue` 并覆盖原文件。

### 2. 或者在 Buffotte 页面中嵌入

在 `BuffotteReport.vue` 中导入并使用：

```vue
<template>
  <div class="buffotte-page">
    <!-- 现有内容 -->
    
    <!-- 新增：实时价格追踪 -->
    <div class="price-tracker-section">
      <h2>实时价格追踪</h2>
      <CS2Tracker />
    </div>
  </div>
</template>

<script setup>
import CS2Tracker from './CS2Tracker.vue'
</script>
```

---

## 本地测试步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看效果

### 3. 确保后端 API 运行

```bash
cd ..
uvicorn api.main:app --reload
```

API 运行在 http://localhost:8000

### 4. 测试功能

- ✅ 搜索饰品：输入 "AK-47" 或 "AWP"
- ✅ 查看价格：点击搜索结果
- ✅ API 配额：观察右上角实时更新
- ✅ 响应式：调整浏览器窗口大小

---

## 生产部署清单

- [ ] 复制组件文件到 hezhili.online 项目
- [ ] 更新 App.vue 路由配置
- [ ] 添加侧边栏导航项
- [ ] 配置环境变量 (.env)
- [ ] 构建前端：`npm run build`
- [ ] 部署 FastAPI 后端（Docker 或 PM2）
- [ ] 配置 Nginx 反向代理
- [ ] 设置 SSL 证书（Let's Encrypt）
- [ ] 测试所有功能
- [ ] 监控 API 配额和错误日志

---

## 样式风格说明

CS2 Tracker 完全遵循 hezhili.online 的极客 Matrix 主题：

- **配色方案**：深黑背景 + 绿色荧光 (#00ff41, #00ff7f)
- **字体**：Source Code Pro 等宽字体
- **视觉效果**：
  - 终端窗口样式（红黄绿三色点）
  - Matrix 字符雨背景
  - 绿色光晕阴影
  - 闪烁光标动画
  - 扫描线效果
- **交互反馈**：
  - 悬停高亮
  - 边框发光
  - 平滑过渡动画
  - Toast 通知

所有样式都与你的网站完美融合！🎨
