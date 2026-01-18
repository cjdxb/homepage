import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import { API_BASE_URL } from './config'
import './style.css'

// 配置axios默认地址
axios.defaults.baseURL = API_BASE_URL
axios.defaults.withCredentials = true

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
