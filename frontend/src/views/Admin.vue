<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>后台管理</h1>
      <div class="header-actions">
        <a href="/" class="btn-link">查看主页</a>
        <button @click="handleLogout" class="btn-logout">退出登录</button>
      </div>
    </header>

    <main class="admin-content">
      <!-- 快捷方式管理 -->
      <section class="section">
        <div class="section-header">
          <h2>快捷方式管理</h2>
          <button @click="openAddModal" class="btn-primary">添加快捷方式</button>
        </div>

        <div class="shortcuts-list">
          <div v-if="shortcuts.length === 0" class="empty-state">
            暂无快捷方式，点击上方按钮添加
          </div>
          <div
            v-for="shortcut in shortcuts"
            :key="shortcut.id"
            class="shortcut-item"
          >
            <div class="shortcut-info">
              <div class="shortcut-icon">
                <img :src="getShortcutIcon(shortcut)" :alt="shortcut.name" @error="handleIconError" />
              </div>
              <div class="shortcut-details">
                <strong>{{ shortcut.name }}</strong>
                <span class="url">{{ shortcut.url }}</span>
              </div>
            </div>
            <div class="shortcut-actions">
              <button @click="openEditModal(shortcut)" class="btn-edit">编辑</button>
              <button @click="deleteShortcut(shortcut.id)" class="btn-delete">删除</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 搜索引擎管理 -->
      <section class="section">
        <div class="section-header">
          <h2>搜索引擎管理</h2>
          <button @click="openAddEngineModal" class="btn-primary">添加搜索引擎</button>
        </div>

        <div class="shortcuts-list">
          <div
            v-for="engine in searchEngines"
            :key="engine.id"
            class="shortcut-item"
          >
            <div class="shortcut-info">
              <div class="shortcut-icon">
                <img v-if="engine.icon" :src="engine.icon" :alt="engine.name" @error="handleIconError" />
                <span v-else class="default-icon">{{ engine.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="shortcut-details">
                <strong>{{ engine.name }}</strong>
                <span class="url">{{ engine.url_template }}</span>
                <span v-if="engine.is_default" class="badge">预置</span>
              </div>
            </div>
            <div class="shortcut-actions">
              <button @click="openEditEngineModal(engine)" class="btn-edit">编辑</button>
              <button
                v-if="!engine.is_default"
                @click="deleteSearchEngine(engine.id)"
                class="btn-delete"
              >删除</button>
            </div>
          </div>
        </div>

        <div class="form-group" style="margin-top: 1rem;">
          <label>默认搜索引擎</label>
          <select v-model="settings.default_search_engine_id" @change="saveSettings">
            <option v-for="engine in searchEngines" :key="engine.id" :value="engine.id">
              {{ engine.name }}
            </option>
          </select>
        </div>
      </section>

      <!-- 壁纸设置 -->
      <section class="section">
        <h2>壁纸设置</h2>
        <div class="settings-form">
          <div class="form-group">
            <label>壁纸模式</label>
            <select v-model="settings.wallpaper_mode" @change="saveSettings">
              <option value="bing">Bing每日壁纸</option>
              <option value="custom">自定义壁纸</option>
              <option value="disabled">禁用壁纸</option>
            </select>
          </div>

          <div v-if="settings.wallpaper_mode === 'custom'" class="form-group">
            <label>自定义壁纸URL</label>
            <input
              v-model="settings.custom_wallpaper_url"
              type="url"
              placeholder="请输入壁纸图片URL"
              @blur="saveSettings"
            />
          </div>
        </div>
      </section>

      <!-- 网站设置 -->
      <section class="section">
        <h2>网站设置</h2>
        <div class="settings-form">
          <div class="form-group">
            <label>网站标题</label>
            <input
              v-model="settings.site_title"
              type="text"
              placeholder="例如：我的主页"
              @blur="saveSettings"
            />
            <span class="form-hint">显示在浏览器标签页上的标题</span>
          </div>
          <div class="form-group">
            <label>ICP备案号</label>
            <input
              v-model="settings.icp_number"
              type="text"
              placeholder="例如：京ICP备12345678号"
              @blur="saveSettings"
            />
            <span class="form-hint">留空则不显示备案号</span>
          </div>
        </div>
      </section>

      <!-- 修改密码 -->
      <section class="section">
        <h2>修改密码</h2>
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label>当前密码</label>
            <input v-model="passwordForm.old_password" type="password" required />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.new_password" type="password" required />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="passwordForm.confirm_password" type="password" required />
          </div>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          <div v-if="passwordSuccess" class="success-message">{{ passwordSuccess }}</div>
          <button type="submit" class="btn-primary">修改密码</button>
        </form>
      </section>
    </main>

    <!-- 添加/编辑快捷方式模态框 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingShortcut ? '编辑快捷方式' : '添加快捷方式' }}</h3>
        <form @submit.prevent="saveShortcut">
          <div class="form-group">
            <label>名称 *</label>
            <input v-model="form.name" type="text" required placeholder="例如：Google" />
          </div>
          <div class="form-group">
            <label>URL *</label>
            <input v-model="form.url" type="url" required placeholder="例如：https://www.google.com" />
          </div>
          <div class="form-group">
            <label>图标URL（可选，留空自动获取网站图标）</label>
            <input v-model="form.icon" type="url" placeholder="例如：https://www.google.com/favicon.ico" />
          </div>
          <div class="form-group">
            <label>排序（数字越小越靠前）</label>
            <input v-model.number="form.order" type="number" placeholder="0" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 添加/编辑搜索引擎模态框 -->
    <div v-if="showEngineModal" class="modal-overlay" @click.self="closeEngineModal">
      <div class="modal">
        <h3>{{ editingEngine ? '编辑搜索引擎' : '添加搜索引擎' }}</h3>
        <form @submit.prevent="saveSearchEngine">
          <div class="form-group">
            <label>名称 *</label>
            <input v-model="engineForm.name" type="text" required placeholder="例如：DuckDuckGo" />
          </div>
          <div class="form-group">
            <label>搜索URL模板 *</label>
            <input
              v-model="engineForm.url_template"
              type="text"
              required
              placeholder="例如：https://duckduckgo.com/?q={query}"
            />
            <small class="hint">使用 {query} 作为搜索词占位符</small>
          </div>
          <div class="form-group">
            <label>图标URL（可选）</label>
            <input v-model="engineForm.icon" type="url" placeholder="例如：https://duckduckgo.com/favicon.ico" />
          </div>
          <div class="form-group">
            <label>排序（数字越小越靠前）</label>
            <input v-model.number="engineForm.order" type="number" placeholder="0" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeEngineModal" class="btn-cancel">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const shortcuts = ref([])
const searchEngines = ref([])
const settings = ref({ wallpaper_mode: 'bing', custom_wallpaper_url: '', default_search_engine_id: 1, icp_number: '', site_title: '' })

const showModal = ref(false)
const editingShortcut = ref(null)
const form = ref({ name: '', url: '', icon: '', order: 0 })

const showEngineModal = ref(false)
const editingEngine = ref(null)
const engineForm = ref({ name: '', url_template: '', icon: '', order: 0 })

const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const passwordError = ref('')
const passwordSuccess = ref('')

const getShortcutIcon = (shortcut) => {
  if (shortcut.icon) {
    return shortcut.icon
  }
  try {
    const url = new URL(shortcut.url)
    return `https://www.google.com/s2/favicons?domain=${url.hostname}&sz=64`
  } catch {
    return ''
  }
}

const fetchShortcuts = async () => {
  try {
    const response = await axios.get('/api/shortcuts')
    shortcuts.value = response.data
  } catch (error) {
    console.error('获取快捷方式失败:', error)
  }
}

const fetchSearchEngines = async () => {
  try {
    const response = await axios.get('/api/search-engines')
    searchEngines.value = response.data
  } catch (error) {
    console.error('获取搜索引擎失败:', error)
  }
}

const fetchSettings = async () => {
  try {
    const response = await axios.get('/api/settings')
    settings.value = response.data
  } catch (error) {
    console.error('获取设置失败:', error)
  }
}

// 快捷方式相关
const openAddModal = () => {
  editingShortcut.value = null
  form.value = { name: '', url: '', icon: '', order: 0 }
  showModal.value = true
}

const openEditModal = (shortcut) => {
  editingShortcut.value = shortcut
  form.value = { ...shortcut }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingShortcut.value = null
}

const saveShortcut = async () => {
  try {
    if (editingShortcut.value) {
      await axios.put(`/api/shortcuts/${editingShortcut.value.id}`, form.value)
    } else {
      await axios.post('/api/shortcuts', form.value)
    }
    closeModal()
    fetchShortcuts()
  } catch (error) {
    console.error('保存失败:', error)
    alert(error.response?.data?.error || '保存失败')
  }
}

const deleteShortcut = async (id) => {
  if (!confirm('确定要删除这个快捷方式吗？')) return

  try {
    await axios.delete(`/api/shortcuts/${id}`)
    fetchShortcuts()
  } catch (error) {
    console.error('删除失败:', error)
    alert(error.response?.data?.error || '删除失败')
  }
}

// 搜索引擎相关
const openAddEngineModal = () => {
  editingEngine.value = null
  engineForm.value = { name: '', url_template: '', icon: '', order: 0 }
  showEngineModal.value = true
}

const openEditEngineModal = (engine) => {
  editingEngine.value = engine
  engineForm.value = { ...engine }
  showEngineModal.value = true
}

const closeEngineModal = () => {
  showEngineModal.value = false
  editingEngine.value = null
}

const saveSearchEngine = async () => {
  try {
    if (editingEngine.value) {
      await axios.put(`/api/search-engines/${editingEngine.value.id}`, engineForm.value)
    } else {
      await axios.post('/api/search-engines', engineForm.value)
    }
    closeEngineModal()
    fetchSearchEngines()
  } catch (error) {
    console.error('保存失败:', error)
    alert(error.response?.data?.error || '保存失败')
  }
}

const deleteSearchEngine = async (id) => {
  if (!confirm('确定要删除这个搜索引擎吗？')) return

  try {
    await axios.delete(`/api/search-engines/${id}`)
    fetchSearchEngines()
  } catch (error) {
    console.error('删除失败:', error)
    alert(error.response?.data?.error || '删除失败')
  }
}

const saveSettings = async () => {
  try {
    await axios.put('/api/settings', settings.value)
  } catch (error) {
    console.error('保存设置失败:', error)
    alert(error.response?.data?.error || '保存设置失败')
  }
}

const changePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }

  try {
    await axios.post('/api/change-password', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    passwordSuccess.value = '密码修改成功'
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (error) {
    passwordError.value = error.response?.data?.error || '密码修改失败'
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const handleIconError = (e) => {
  e.target.style.display = 'none'
}

onMounted(() => {
  fetchShortcuts()
  fetchSearchEngines()
  fetchSettings()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.admin-header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.admin-header h1 {
  font-size: 1.5rem;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-link {
  color: #667eea;
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-logout {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-logout:hover {
  background: #c0392b;
}

.admin-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section h2 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  margin-bottom: 0;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.3s, transform 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background 0.3s;
}

.shortcut-item:hover {
  background: #eef1f5;
}

.shortcut-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.shortcut-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.shortcut-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
}

.default-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
  border-radius: 8px;
}

.shortcut-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.shortcut-details strong {
  color: #333;
}

.shortcut-details .url {
  font-size: 0.85rem;
  color: #888;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background: #667eea;
  color: white;
  font-size: 0.7rem;
  border-radius: 4px;
  margin-top: 0.3rem;
  width: fit-content;
}

.shortcut-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-edit {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-edit:hover {
  background: #2980b9;
}

.btn-delete {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-delete:hover {
  background: #c0392b;
}

.settings-form,
.password-form {
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.hint,
.form-hint {
  display: block;
  margin-top: 0.3rem;
  font-size: 0.8rem;
  color: #888;
}

.error-message {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.success-message {
  color: #27ae60;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }

  .admin-content {
    padding: 1rem;
  }

  .section {
    padding: 1rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .shortcut-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .shortcut-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .modal {
    padding: 1.5rem;
  }
}
</style>
