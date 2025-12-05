<template>
  <div class="cs2-tracker-page">
    <!-- ASCII Art Title -->
    <pre class="ascii-title">
 ██████╗███████╗██████╗     ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝╚════██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██║     ███████╗ █████╔╝       ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██║     ╚════██║██╔═══╝        ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
╚██████╗███████║███████╗       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
 ╚═════╝╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    </pre>

    <!-- Main Console Container -->
    <div class="console integrated">
      <div class="console-header">
        <div class="header-left">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <div class="title">cs2-tracker@terminal: ~/price-monitor</div>
        <div class="api-quota">
          <span class="quota-label">API剩余:</span>
          <span class="quota-value">{{ apiQuota }}</span>
          <span class="quota-divider">/</span>
          <span class="quota-total">{{ apiQuotaTotal }}</span>
        </div>
      </div>

      <div class="console-content">
        <!-- Search Section -->
        <div class="search-section">
          <div class="search-prompt">
            <span class="prompt-symbol">$</span>
            <span class="prompt-text">search --item</span>
          </div>
          <div class="search-box">
            <input
              v-model="searchQuery"
              @input="handleSearchInput"
              @keydown.enter="performSearch"
              type="text"
              placeholder="输入饰品名称 (例: AK-47, AWP)..."
              class="search-input"
            />
            <button @click="performSearch" class="search-btn">
              <span v-if="!searching">搜索</span>
              <span v-else class="loading-spinner">⟳</span>
            </button>
          </div>
          
          <!-- Search Suggestions -->
          <div v-if="suggestions && suggestions.length > 0" class="suggestions-dropdown">
            <div
              v-for="(item, index) in suggestions"
              :key="index"
              @click="selectSuggestion(item)"
              class="suggestion-item"
            >
              <span class="suggestion-icon">▸</span>
              <span class="suggestion-name">{{ item.name }}</span>
            </div>
          </div>
        </div>

        <!-- Search Results -->
        <div v-if="searchResults && searchResults.length > 0" class="results-section">
          <div class="section-title">
            <span class="terminal-prompt">></span>
            <span>搜索结果 ({{ searchResults.length }} 项)</span>
          </div>
          <div class="results-grid">
            <div
              v-for="(item, index) in searchResults"
              :key="index"
              @click="selectItem(item)"
              :class="['result-card', { active: selectedItem?.name === item.name }]"
            >
              <div class="result-index">[{{ index + 1 }}]</div>
              <div class="result-name">{{ item.name }}</div>
              <div class="result-hint">点击查看价格 →</div>
            </div>
          </div>
        </div>

        <!-- Item Details Section -->
        <div v-if="selectedItem" class="details-section">
          <div class="section-title">
            <span class="terminal-prompt">></span>
            <span>饰品详情</span>
          </div>
          
          <div class="item-info-card">
            <div class="item-header">
              <h3 class="item-name">{{ selectedItem.name }}</h3>
              <button @click="refreshPrice" class="refresh-btn" :disabled="loadingPrice">
                <span v-if="!loadingPrice">刷新价格</span>
                <span v-else class="loading-spinner">⟳</span>
              </button>
            </div>

            <!-- Price Information -->
            <div v-if="priceData" class="price-info">
              <div class="price-grid">
                <div class="price-card">
                  <div class="platform-name">C5GAME</div>
                  <div class="price-row">
                    <span class="price-label">收购价:</span>
                    <span class="price-value">¥{{ priceData.buyPrice || 'N/A' }}</span>
                  </div>
                  <div class="price-row">
                    <span class="price-label">出售价:</span>
                    <span class="price-value highlight">¥{{ priceData.sellPrice || 'N/A' }}</span>
                  </div>
                  <div class="platform-badge">{{ priceData.platform || 'C5' }}</div>
                </div>

                <!-- Additional platforms if available -->
                <div v-for="(platform, idx) in additionalPlatforms" :key="idx" class="price-card">
                  <div class="platform-name">{{ platform.name }}</div>
                  <div class="price-row">
                    <span class="price-label">出售价:</span>
                    <span class="price-value">¥{{ platform.price }}</span>
                  </div>
                  <div class="platform-badge">{{ platform.code }}</div>
                </div>
              </div>

              <div class="price-meta">
                <span class="meta-item">
                  <span class="meta-label">更新时间:</span>
                  <span class="meta-value">{{ formatTime(priceData.timestamp) }}</span>
                </span>
              </div>
            </div>

            <!-- Loading State -->
            <div v-else-if="loadingPrice" class="loading-state">
              <span class="loading-spinner large">⟳</span>
              <p>正在获取价格数据...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="priceError" class="error-state">
              <p class="error-message">{{ priceError }}</p>
              <button @click="refreshPrice" class="retry-btn">重试</button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!searching && (!searchResults || searchResults.length === 0) && !selectedItem" class="empty-state">
          <div class="empty-icon">🔍</div>
          <p class="empty-text">开始搜索 CS2 饰品...</p>
          <p class="empty-hint">支持中文/英文名称，如 "AK-47" 或 "火蛇"</p>
        </div>
      </div>

      <!-- Console Footer -->
      <div class="console-footer">
        <div class="footer-stats">
          <span class="stat-item">
            <span class="stat-label">饰品库:</span>
            <span class="stat-value">38,130</span>
          </span>
          <span class="stat-separator">|</span>
          <span class="stat-item">
            <span class="stat-label">状态:</span>
            <span :class="['stat-value', apiStatus]">{{ apiStatusText }}</span>
          </span>
          <span class="stat-separator">|</span>
          <span class="stat-item">
            <span class="stat-label">延迟:</span>
            <span class="stat-value">{{ latency }}ms</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast-container" v-if="toast">
      <div class="toast" :data-show="toastVisible">{{ toast }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../services/api.js'
import '../css/cs2-tracker.css'

// Reactive state
const searchQuery = ref('')
const searchResults = ref([])
const suggestions = ref([])
const selectedItem = ref(null)
const priceData = ref(null)
const apiQuota = ref(60)
const apiQuotaTotal = ref(60)
const apiStatus = ref('healthy')
const latency = ref(0)

// Loading states
const searching = ref(false)
const loadingPrice = ref(false)
const priceError = ref(null)

// Toast notification
const toast = ref(null)
const toastVisible = ref(false)

// Debounce timer for search suggestions
let suggestionTimer = null

// Quota refresh interval
let quotaInterval = null

// Computed properties
const apiStatusText = computed(() => {
  return apiStatus.value === 'healthy' ? 'ONLINE' : 'OFFLINE'
})

const additionalPlatforms = computed(() => {
  // Parse additional platform data if available
  if (priceData.value && priceData.value.allPlatforms && priceData.value.allPlatforms.length > 1) {
    return priceData.value.allPlatforms.slice(1).map(item => ({
      name: getPlatformDisplayName(item.platform),
      code: item.platform || 'N/A',
      price: item.sellPrice || item.biddingPrice || 'N/A'
    }))
  }
  return []
})

// 平台名称映射
const getPlatformDisplayName = (platform) => {
  const names = {
    'C5': 'C5GAME',
    'YOUPIN': '悠悠有品',
    'HALOSKINS': 'HALOSKINS',
    'BUFF': '网易BUFF',
    'STEAM': 'Steam市场',
    'WAXPEER': 'WAXPEER',
    'DMARKET': 'DMarket',
    'CSMONEY': 'CSMoney',
    'SKINPORT': 'Skinport'
  }
  return names[platform] || platform
}

// Methods
const showToast = (message, duration = 2000) => {
  toast.value = message
  toastVisible.value = true
  setTimeout(() => {
    toastVisible.value = false
  }, duration)
}

const handleSearchInput = () => {
  // Clear previous timer
  if (suggestionTimer) {
    clearTimeout(suggestionTimer)
  }

  // Don't show suggestions for very short queries
  if (searchQuery.value.trim().length < 2) {
    suggestions.value = []
    return
  }

  // Debounce suggestions
  suggestionTimer = setTimeout(async () => {
    try {
      const response = await api.getSuggestions(searchQuery.value, 5)
      if (response.success && Array.isArray(response.data)) {
        suggestions.value = response.data
      } else {
        suggestions.value = []
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error)
      suggestions.value = []
    }
  }, 300)
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    showToast('请输入搜索关键词')
    return
  }

  searching.value = true
  suggestions.value = []
  
  try {
    const startTime = Date.now()
    const response = await api.searchItems(searchQuery.value, 20)
    latency.value = Date.now() - startTime

    if (response.success && Array.isArray(response.data)) {
      searchResults.value = response.data
      showToast(`找到 ${response.count || response.data.length} 个结果`)
      
      // Auto-select first item if only one result
      if (response.data.length === 1) {
        selectItem(response.data[0])
      }
    } else {
      showToast('搜索失败，请重试')
      searchResults.value = []
    }
  } catch (error) {
    console.error('Search failed:', error)
    showToast('搜索出错: ' + error.message)
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

const selectSuggestion = (item) => {
  searchQuery.value = item.name
  suggestions.value = []
  performSearch()
}

const selectItem = async (item) => {
  selectedItem.value = item
  priceData.value = null
  priceError.value = null
  loadingPrice.value = true

  try {
    const startTime = Date.now()
    // 使用 market_hash_name (英文 Steam 市场名) 而不是 name (中文名)
    const hashname = item.market_hash_name || item.name
    const response = await api.getPrice(hashname)
    latency.value = Date.now() - startTime

    // API 返回格式：{success: true, data: [{platform, buyPrice, sellPrice}]}
    if (response && response.success && response.data && Array.isArray(response.data)) {
      if (response.data.length > 0) {
        // 转换为前端期望的格式
        priceData.value = {
          platform: response.data[0].platform || 'C5',
          buyPrice: response.data[0].biddingPrice || response.data[0].buyPrice,
          sellPrice: response.data[0].sellPrice,
          timestamp: new Date().toISOString(),
          allPlatforms: response.data.filter(p => p.sellPrice > 0)  // 只显示有价格的平台
        }
      } else {
        priceError.value = '暂无价格数据'
        priceData.value = null
      }
    } else if (response && response.error) {
      priceError.value = response.message || response.error || '获取价格失败'
      priceData.value = null
    } else {
      priceError.value = '获取价格失败'
      priceData.value = null
    }
  } catch (error) {
    console.error('Failed to fetch price:', error)
    priceError.value = error.message || '获取价格时发生错误'
    priceData.value = null
  } finally {
    loadingPrice.value = false
  }
}

const refreshPrice = () => {
  if (selectedItem.value) {
    selectItem(selectedItem.value)
  }
}

const fetchApiStatus = async () => {
  try {
    // 获取系统状态
    const statusResponse = await api.getStatus()
    apiStatus.value = (statusResponse && statusResponse.status === 'operational') ? 'healthy' : 'error'
    
    // 获取实际配额
    const quotaResponse = await api.getQuota()
    if (quotaResponse && quotaResponse.success) {
      apiQuota.value = quotaResponse.remaining
      apiQuotaTotal.value = quotaResponse.total
    } else {
      apiQuota.value = 60  // 默认值
      apiQuotaTotal.value = 60
    }
  } catch (error) {
    console.error('Failed to fetch API status:', error)
    apiStatus.value = 'error'
    apiQuota.value = 0
    apiQuotaTotal.value = 60
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Lifecycle hooks
onMounted(() => {
  // Initial status check
  fetchApiStatus()
  
  // Refresh quota every 5 seconds
  quotaInterval = setInterval(fetchApiStatus, 5000)
})

onUnmounted(() => {
  if (suggestionTimer) {
    clearTimeout(suggestionTimer)
  }
  if (quotaInterval) {
    clearInterval(quotaInterval)
  }
})
</script>
