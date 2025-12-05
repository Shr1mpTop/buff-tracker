import axios from 'axios'

// API base URL - defaults to current origin so production hits the same host (via Nginx)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export default {
  // 搜索饰品
  searchItems(name, num = 10) {
    return apiClient.get('/api/search', {
      params: { name, num }
    })
  },

  // 获取搜索建议（自动补全）
  getSuggestions(query, limit = 10) {
    return apiClient.get('/api/search/suggest', {
      params: { q: query, limit }
    })
  },

  // 获取饰品价格
  getPrice(hashname) {
    return apiClient.get(`/api/price/${encodeURIComponent(hashname)}`)
  },

  // 获取 API 状态（配额信息）
  getStatus() {
    return apiClient.get('/api/status')
  },

  // 获取 API 配额
  getQuota() {
    return apiClient.get('/api/quota')
  },

  // 健康检查
  healthCheck() {
    return apiClient.get('/api/health')
  }
}
