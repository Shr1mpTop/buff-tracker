# CS2 Price Tracker - Frontend

极客风格的 CS2 饰品价格追踪前端页面，采用 Matrix 终端主题设计。

## 功能特性

- 🔍 **智能搜索栏**：支持模糊搜索 CS2 饰品
- 📊 **饰品详细信息**：显示多平台交易数据（C5、HALOSKINS、YOUPIN）
- 📈 **API 配额监控**：实时显示当前分钟可调用次数
- 🎨 **Matrix 终端风格**：深色主题 + 绿色荧光效果
- ⚡ **响应式设计**：支持桌面和移动端

## 技术栈

- **Vue 3** - 组合式 API
- **Vite** - 快速开发构建
- **Axios** - HTTP 请求
- **CSS3** - Matrix 终端样式

## 快速开始

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```
访问 http://localhost:5173

### 生产构建
```bash
npm run build
```

## 集成到 hezhili.online

1. 将构建后的文件复制到 hezhili.online 项目
2. 在 `App.vue` 中添加路由配置
3. 创建 `/cs2` 路由指向 `CS2Tracker` 组件

## API 端点

- `GET /api/search?name={query}&num={limit}` - 搜索饰品
- `GET /api/price/{hashname}` - 获取价格
- `GET /api/status` - API 配额状态

## 设计风格

参考 hezhili.online 的极客主题：
- 等宽字体 Source Code Pro
- 深色背景 rgba(0,0,0,0.8)
- 绿色荧光 #00ff41, #00ff7f
- 终端窗口样式
- 闪烁光标效果
