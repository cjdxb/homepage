<template>
  <div class="home" :style="backgroundStyle">
    <div class="overlay"></div>
    <div class="content">
      <!-- 时间日期和天气信息 -->
      <div class="header-section">
        <div class="time">{{ currentTime }}</div>

        <!-- 日期和天气合并一行 -->
        <div class="date-weather-row">
          <span class="date">{{ currentDate }}</span>
          <span class="row-divider">|</span>
          <div class="weather-wrapper">
            <span class="weather-inline" @click="toggleCityInput">
              <template v-if="weatherLoading">
                <span class="weather-loading-text">...</span>
              </template>
              <template v-else-if="weather">
                <span class="weather-icon">{{ getWeatherEmoji(weather.weather_code) }}</span>
                <span class="weather-temp">{{ weather.temp }}°</span>
                <span class="weather-desc">{{ weather.weather_desc }}</span>
                <span class="weather-city-group">
                  <span class="weather-city">{{ currentCity }}</span>
                </span>
              </template>
              <template v-else>
                <span class="weather-placeholder">设置城市</span>
              </template>
            </span>

            <!-- 城市输入弹窗 -->
            <div v-if="showCityInput" class="city-input-popup" @click.stop>
              <input
                ref="cityInputRef"
                v-model="cityInputValue"
                @keydown.enter="confirmCity"
                @keydown.esc="showCityInput = false"
                placeholder="输入城市名称"
                class="city-input"
              />
              <div class="city-input-actions">
                <button class="btn-auto" @click="autoLocate">自动定位</button>
                <button class="btn-confirm" @click="confirmCity">确定</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索框 -->
      <div class="search-container">
        <div class="search-box">
          <div class="engine-selector" @click.stop="toggleEngineDropdown">
            <img
              v-if="!engineIconErrors[currentEngine?.id]"
              :src="getEngineIcon(currentEngine)"
              class="engine-icon"
              @error="handleEngineIconError($event, currentEngine)"
            />
            <span v-else class="engine-fallback">{{ currentEngine?.name?.charAt(0) || 'G' }}</span>
            <svg class="arrow" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M7 10l5 5 5-5z"/>
            </svg>
          </div>
          <input
            type="text"
            v-model="searchQuery"
            @input="onSearchInput"
            @keydown="onSearchKeydown"
            @focus="onSearchFocus"
            @blur="onSearchBlur"
            placeholder="搜索..."
            class="search-input"
            autocomplete="off"
          />
          <button class="search-btn" @click="search">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </button>
        </div>
        <div v-if="showEngineDropdown" class="engine-dropdown">
          <div
            v-for="engine in searchEngines"
            :key="engine.id"
            class="engine-option"
            :class="{ active: currentEngine?.id === engine.id }"
            @click="selectEngine(engine)"
          >
            <img
              v-if="!engineIconErrors[engine.id]"
              :src="getEngineIcon(engine)"
              class="engine-icon"
              @error="handleEngineIconError($event, engine)"
            />
            <span v-else class="engine-fallback-small">{{ engine.name.charAt(0) }}</span>
            <span>{{ engine.name }}</span>
          </div>
        </div>
        <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
          <div
            v-for="(suggestion, index) in suggestions"
            :key="index"
            class="suggestion-item"
            :class="{ active: index === selectedSuggestionIndex }"
            @mousedown.prevent="selectSuggestion(suggestion)"
          >
            <svg class="suggestion-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <span>{{ suggestion }}</span>
          </div>
        </div>
      </div>

      <!-- 快捷方式网格 -->
      <div class="shortcuts-grid">
        <a
          v-for="shortcut in shortcuts"
          :key="shortcut.id"
          :href="shortcut.url"
          target="_blank"
          class="shortcut-item"
        >
          <div class="icon-wrapper">
            <img
              v-if="!iconErrors[shortcut.id]"
              :src="getShortcutIcon(shortcut)"
              :alt="shortcut.name"
              @error="(e) => handleIconError(e, shortcut)"
            />
            <span v-else class="icon-fallback">
              {{ shortcut.name.charAt(0).toUpperCase() }}
            </span>
          </div>
          <span class="item-label">{{ shortcut.name }}</span>
        </a>
      </div>

      <!-- 壁纸版权信息 -->
      <div class="wallpaper-copyright" v-if="wallpaperCopyright">
        {{ wallpaperCopyright }}
      </div>

      <!-- 左下角版权和备案号 -->
      <div class="site-footer">
        <span class="copyright">&copy; {{ currentYear }} NUTSIM.COM All Rights Reserved.</span>
        <template v-if="settings.icp_number">
          <span class="footer-divider">|</span>
          <a class="icp" href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{{ settings.icp_number }}</a>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'

const shortcuts = ref([])
const settings = ref({ wallpaper_mode: 'bing', custom_wallpaper_url: '', default_search_engine_id: 1, icp_number: '', site_title: '' })
const currentYear = new Date().getFullYear()
const wallpaperUrl = ref('')
const wallpaperCopyright = ref('')
const searchQuery = ref('')
const searchEngines = ref([])
const currentEngine = ref(null)
const showEngineDropdown = ref(false)
const iconErrors = ref({})
const engineIconErrors = ref({})

const suggestions = ref([])
const showSuggestions = ref(false)
const selectedSuggestionIndex = ref(-1)
let suggestionTimeout = null

const currentTime = ref('')
const currentDate = ref('')
let timeInterval = null

// 天气相关
const weather = ref(null)
const weatherLoading = ref(true)
const currentCity = ref('')
const showCityInput = ref(false)
const cityInputValue = ref('')
const cityInputRef = ref(null)

const updateDateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const backgroundStyle = computed(() => {
  if (settings.value.wallpaper_mode === 'disabled' || !wallpaperUrl.value) {
    return { backgroundColor: '#1a1a2e' }
  }
  return {
    backgroundImage: `url(${wallpaperUrl.value})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed'
  }
})

// 图标缓存（缓存1小时）
const ICON_CACHE_DURATION = 60 * 60 * 1000
const iconCache = ref({})

const initIconCache = () => {
  try {
    const cached = localStorage.getItem('iconCache')
    if (cached) {
      const { data, timestamp } = JSON.parse(cached)
      if (Date.now() - timestamp < ICON_CACHE_DURATION) {
        iconCache.value = data
      } else {
        localStorage.removeItem('iconCache')
      }
    }
  } catch {
    localStorage.removeItem('iconCache')
  }
}

const saveIconCache = () => {
  try {
    localStorage.setItem('iconCache', JSON.stringify({
      data: iconCache.value,
      timestamp: Date.now()
    }))
  } catch (e) {
    console.error('保存图标缓存失败:', e)
  }
}

const getCachedIcon = (key, generator) => {
  if (iconCache.value[key]) {
    return iconCache.value[key]
  }
  const url = generator()
  if (url) {
    iconCache.value[key] = url
    saveIconCache()
  }
  return url
}

const getShortcutIcon = (shortcut) => {
  if (shortcut.icon) {
    return shortcut.icon
  }
  return getCachedIcon(`shortcut_${shortcut.id}`, () => {
    try {
      const url = new URL(shortcut.url)
      return `https://www.google.com/s2/favicons?domain=${url.hostname}&sz=64`
    } catch {
      return ''
    }
  })
}

const getEngineIcon = (engine) => {
  if (!engine) return ''
  if (engine.icon) {
    return engine.icon
  }
  return getCachedIcon(`engine_${engine.id}`, () => {
    try {
      const url = new URL(engine.url_template)
      return `https://www.google.com/s2/favicons?domain=${url.hostname}&sz=64`
    } catch {
      return ''
    }
  })
}

const handleIconError = (e, shortcut) => {
  e.target.style.display = 'none'
  iconErrors.value[shortcut.id] = true
}

const handleEngineIconError = (e, engine) => {
  if (engine) {
    engineIconErrors.value[engine.id] = true
  }
}

// 天气相关函数
const getWeatherEmoji = (code) => {
  const weatherCode = parseInt(code)
  if (weatherCode === 113) return '☀️'
  if (weatherCode === 116) return '⛅'
  if (weatherCode === 119 || weatherCode === 122) return '☁️'
  if ([143, 248, 260].includes(weatherCode)) return '🌫️'
  if ([176, 263, 266, 293, 296, 299, 302, 305, 308, 311, 314, 353, 356, 359].includes(weatherCode)) return '🌧️'
  if ([179, 182, 185, 281, 284, 317, 320, 350, 362, 365, 374, 377].includes(weatherCode)) return '🌨️'
  if ([200, 386, 389, 392, 395].includes(weatherCode)) return '⛈️'
  if ([227, 230, 323, 326, 329, 332, 335, 338, 368, 371].includes(weatherCode)) return '❄️'
  return '🌤️'
}

// 天气缓存时间（30分钟）
const WEATHER_CACHE_DURATION = 30 * 60 * 1000

const getWeatherCache = (city) => {
  try {
    const cached = localStorage.getItem('weatherCache')
    if (!cached) return null
    const { data, timestamp, cachedCity } = JSON.parse(cached)
    if (cachedCity !== city) return null
    if (Date.now() - timestamp > WEATHER_CACHE_DURATION) return null
    return data
  } catch {
    return null
  }
}

const setWeatherCache = (city, data) => {
  try {
    localStorage.setItem('weatherCache', JSON.stringify({
      data,
      timestamp: Date.now(),
      cachedCity: city
    }))
  } catch (e) {
    console.error('缓存天气数据失败:', e)
  }
}

const fetchWeather = async (city, forceRefresh = false) => {
  if (!city) return

  // 检查缓存
  if (!forceRefresh) {
    const cached = getWeatherCache(city)
    if (cached) {
      weather.value = cached
      currentCity.value = city
      weatherLoading.value = false
      return
    }
  }

  weatherLoading.value = true
  try {
    const response = await axios.get('/api/weather', { params: { city } })
    weather.value = response.data
    currentCity.value = city
    localStorage.setItem('weatherCity', city)
    setWeatherCache(city, response.data)
  } catch (error) {
    console.error('获取天气失败:', error)
    weather.value = null
  } finally {
    weatherLoading.value = false
  }
}

const fetchLocation = async () => {
  try {
    const response = await axios.get('/api/location')
    return response.data.city || '北京'
  } catch (error) {
    console.error('获取位置失败:', error)
    return '北京'
  }
}

const initWeather = async () => {
  const savedCity = localStorage.getItem('weatherCity')
  if (savedCity) {
    await fetchWeather(savedCity)
  } else {
    const city = await fetchLocation()
    await fetchWeather(city)
  }
}

const toggleCityInput = () => {
  showCityInput.value = !showCityInput.value
  if (showCityInput.value) {
    cityInputValue.value = currentCity.value
    nextTick(() => {
      cityInputRef.value?.focus()
    })
  }
}

const confirmCity = () => {
  if (cityInputValue.value.trim()) {
    fetchWeather(cityInputValue.value.trim(), true)  // 手动设置城市时强制刷新
    showCityInput.value = false
  }
}

const autoLocate = async () => {
  weatherLoading.value = true
  showCityInput.value = false
  localStorage.removeItem('weatherCity')
  localStorage.removeItem('weatherCache')  // 清除缓存
  const city = await fetchLocation()
  await fetchWeather(city, true)  // 强制刷新
}

// 数据获取函数
const fetchShortcuts = async () => {
  try {
    const response = await axios.get('/api/shortcuts')
    shortcuts.value = response.data
  } catch (error) {
    console.error('获取快捷方式失败:', error)
  }
}

const fetchSettings = async () => {
  try {
    const response = await axios.get('/api/settings')
    settings.value = response.data
    // 设置网站标题
    if (settings.value.site_title) {
      document.title = settings.value.site_title
    }
    await loadWallpaper()
    if (searchEngines.value.length > 0) {
      currentEngine.value = searchEngines.value.find(e => e.id === settings.value.default_search_engine_id) || searchEngines.value[0]
    }
  } catch (error) {
    console.error('获取设置失败:', error)
  }
}

const fetchSearchEngines = async () => {
  try {
    const response = await axios.get('/api/search-engines')
    searchEngines.value = response.data
    const savedEngineId = localStorage.getItem('selectedSearchEngineId')
    if (savedEngineId) {
      currentEngine.value = searchEngines.value.find(e => e.id === parseInt(savedEngineId)) || searchEngines.value[0]
    } else {
      currentEngine.value = searchEngines.value[0]
    }
  } catch (error) {
    console.error('获取搜索引擎失败:', error)
  }
}

const loadWallpaper = async () => {
  if (settings.value.wallpaper_mode === 'bing') {
    try {
      const response = await axios.get('/api/bing-wallpaper')
      wallpaperUrl.value = response.data.url
      wallpaperCopyright.value = response.data.copyright
    } catch (error) {
      console.error('获取Bing壁纸失败:', error)
    }
  } else if (settings.value.wallpaper_mode === 'custom') {
    wallpaperUrl.value = settings.value.custom_wallpaper_url
    wallpaperCopyright.value = ''
  } else {
    wallpaperUrl.value = ''
    wallpaperCopyright.value = ''
  }
}

const toggleEngineDropdown = () => {
  showEngineDropdown.value = !showEngineDropdown.value
}

const selectEngine = (engine) => {
  currentEngine.value = engine
  showEngineDropdown.value = false
  localStorage.setItem('selectedSearchEngineId', engine.id.toString())
}

const search = () => {
  if (searchQuery.value.trim() && currentEngine.value) {
    const url = currentEngine.value.url_template.replace('{query}', encodeURIComponent(searchQuery.value))
    window.open(url, '_blank')
    showSuggestions.value = false
  }
}

const fetchSuggestions = async () => {
  if (!searchQuery.value.trim()) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }

  try {
    const engineName = currentEngine.value?.name || 'google'
    const response = await axios.get('/api/search-suggestions', {
      params: { q: searchQuery.value, engine: engineName }
    })
    suggestions.value = response.data
    showSuggestions.value = suggestions.value.length > 0
    selectedSuggestionIndex.value = -1
  } catch (error) {
    console.error('获取搜索建议失败:', error)
  }
}

const onSearchInput = () => {
  if (suggestionTimeout) clearTimeout(suggestionTimeout)
  suggestionTimeout = setTimeout(fetchSuggestions, 200)
}

const onSearchFocus = () => {
  if (suggestions.value.length > 0) {
    showSuggestions.value = true
  }
}

const onSearchBlur = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 150)
}

const onSearchKeydown = (e) => {
  if (!showSuggestions.value || suggestions.value.length === 0) {
    if (e.key === 'Enter') search()
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedSuggestionIndex.value = Math.min(
      selectedSuggestionIndex.value + 1,
      suggestions.value.length - 1
    )
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedSuggestionIndex.value = Math.max(selectedSuggestionIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (selectedSuggestionIndex.value >= 0) {
      selectSuggestion(suggestions.value[selectedSuggestionIndex.value])
    } else {
      search()
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
  }
}

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion
  showSuggestions.value = false
  search()
}

const handleClickOutside = (e) => {
  if (!e.target.closest('.search-container')) {
    showEngineDropdown.value = false
    showSuggestions.value = false
  }
  if (!e.target.closest('.weather-wrapper')) {
    showCityInput.value = false
  }
}

onMounted(() => {
  initIconCache()
  updateDateTime()
  timeInterval = setInterval(updateDateTime, 1000)
  fetchSearchEngines()
  fetchShortcuts()
  fetchSettings()
  initWeather()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 12vh;
  position: relative;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.2) 100%);
  pointer-events: none;
}

.content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 900px;
  padding: 2rem;
  padding-bottom: 8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 头部区域：时间日期和天气 */
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2.5rem;
  color: white;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.time {
  font-size: 6rem;
  font-weight: 200;
  letter-spacing: 4px;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  margin-bottom: 0.75rem;
}

/* 日期和天气合并行 */
.date-weather-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
  opacity: 0.9;
}

.date {
  font-weight: 400;
  letter-spacing: 1px;
}

.row-divider {
  opacity: 0.4;
  font-weight: 300;
}

/* 天气信息 - 内嵌样式 */
.weather-wrapper {
  position: relative;
}

.weather-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  margin: -0.25rem -0.5rem;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.weather-inline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.weather-loading-text {
  opacity: 0.7;
}

.weather-icon {
  font-size: 1.1rem;
}

.weather-temp {
  font-weight: 500;
}

.weather-desc {
  opacity: 0.9;
}

.weather-city-group {
  display: inline-flex;
  align-items: center;
}

.weather-city {
  opacity: 0.8;
}

.weather-city::before {
  content: "·";
  margin: 0 0.4rem;
  opacity: 0.5;
}

.weather-placeholder {
  opacity: 0.7;
}

/* 城市输入弹窗 */
.city-input-popup {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 12px;
  padding: 0.875rem;
  min-width: 220px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  color: #333;
  z-index: 100;
}

.city-input {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.city-input:focus {
  border-color: #667eea;
}

.city-input-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.btn-auto, .btn-confirm {
  flex: 1;
  padding: 0.5rem 0.6rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-auto {
  background: #f5f5f5;
  color: #555;
}

.btn-auto:hover {
  background: #eee;
}

.btn-confirm {
  background: #667eea;
  color: white;
}

.btn-confirm:hover {
  background: #5a6fd6;
}

/* 搜索框 */
.search-container {
  width: 100%;
  max-width: 620px;
  margin-bottom: 3rem;
  position: relative;
}

.search-box {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  transform: scale(1.02);
}

.engine-selector {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.9rem 0.6rem 0.9rem 1.2rem;
  cursor: pointer;
  border-right: 1px solid #e8e8e8;
  transition: background 0.2s;
}

.engine-selector:hover {
  background: rgba(0, 0, 0, 0.04);
}

.engine-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
}

.engine-name {
  font-size: 0.85rem;
  color: #555;
  white-space: nowrap;
}

.engine-fallback {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 4px;
}

.engine-fallback-small {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 4px;
}

.arrow {
  color: #888;
}

.search-input {
  flex: 1;
  padding: 1.1rem 1rem 1.1rem 1rem;
  font-size: 1.1rem;
  border: none;
  background: transparent;
  outline: none;
}

.search-btn {
  padding: 0.9rem 1.2rem;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  color: #333;
  background: rgba(0, 0, 0, 0.04);
}

.engine-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 100;
  min-width: 160px;
}

.engine-option {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.9rem 1.2rem;
  cursor: pointer;
  transition: background 0.2s;
}

.engine-option:hover {
  background: #f5f5f5;
}

.engine-option.active {
  background: #e8f0fe;
  color: #1a73e8;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 99;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.85rem 1.2rem;
  cursor: pointer;
  transition: background 0.15s;
  color: #333;
}

.suggestion-item:hover,
.suggestion-item.active {
  background: #f5f5f5;
}

.suggestion-icon {
  color: #999;
  flex-shrink: 0;
}

.suggestion-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 快捷方式网格 */
.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 1.5rem;
  width: 100%;
  max-width: 700px;
  padding: 0 1rem;
  justify-items: center;
}

.shortcut-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  width: 85px;
  transition: transform 0.25s ease;
}

.shortcut-item:hover {
  transform: scale(1.1) translateY(-4px);
}

.shortcut-item:hover .icon-wrapper {
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.25s ease;
  overflow: hidden;
}

.icon-wrapper img {
  width: 38px;
  height: 38px;
  object-fit: contain;
}

.icon-fallback {
  font-size: 1.6rem;
  font-weight: 600;
  color: white;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.item-label {
  font-size: 12px;
  color: white;
  text-align: center;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  line-height: 1.3;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 壁纸版权信息 - 右下角 */
.wallpaper-copyright {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
  max-width: 45vw;
  text-align: right;
  line-height: 1.5;
}

/* 网站版权和备案号 - 左下角 */
.site-footer {
  position: fixed;
  bottom: 1rem;
  left: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
  max-width: 45vw;
  line-height: 1.5;
}

.footer-divider {
  opacity: 0.4;
}

.site-footer .icp {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.2s;
}

.site-footer .icp:hover {
  color: rgba(255, 255, 255, 0.95);
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home {
    padding-top: 8vh;
  }

  .content {
    padding: 1.5rem;
  }

  .header-section {
    margin-bottom: 2rem;
  }

  .time {
    font-size: 4.5rem;
    letter-spacing: 2px;
    margin-bottom: 0.6rem;
  }

  .date-weather-row {
    font-size: 0.9rem;
    gap: 0.6rem;
  }

  .weather-icon {
    font-size: 1rem;
  }

  .search-container {
    margin-bottom: 2rem;
  }

  .search-input {
    padding: 0.9rem 1rem;
    font-size: 1rem;
  }

  .engine-selector {
    padding: 0.7rem 0.5rem 0.7rem 0.9rem;
  }

  .shortcuts-grid {
    grid-template-columns: repeat(auto-fill, minmax(75px, 1fr));
    gap: 1.25rem;
  }

  .shortcut-item {
    width: 70px;
  }

  .icon-wrapper {
    width: 54px;
    height: 54px;
    border-radius: 14px;
  }

  .icon-wrapper img {
    width: 32px;
    height: 32px;
  }

  .item-label {
    font-size: 11px;
  }

  .wallpaper-copyright {
    font-size: 0.6rem;
    max-width: 180px;
  }

  .site-footer {
    font-size: 0.65rem;
  }

  .city-input-popup {
    min-width: 200px;
  }
}

@media (max-width: 480px) {
  .home {
    padding-top: 6vh;
  }

  .header-section {
    margin-bottom: 1.5rem;
  }

  .time {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
  }

  .date-weather-row {
    flex-wrap: wrap;
    justify-content: center;
    font-size: 0.85rem;
    gap: 0.5rem;
  }

  .weather-icon {
    font-size: 0.95rem;
  }

  .weather-city-group {
    display: none;
  }

  .shortcuts-grid {
    grid-template-columns: repeat(auto-fill, minmax(65px, 1fr));
    gap: 1rem;
  }

  .shortcut-item {
    width: 65px;
  }

  .icon-wrapper {
    width: 50px;
    height: 50px;
    border-radius: 12px;
  }

  .icon-wrapper img {
    width: 28px;
    height: 28px;
  }

  .icon-fallback {
    font-size: 1.3rem;
  }

  .item-label {
    font-size: 10px;
  }
}
</style>
