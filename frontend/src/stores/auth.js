import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    username: ''
  }),
  actions: {
    async checkAuth() {
      try {
        const response = await axios.get('/api/check-auth')
        this.isAuthenticated = response.data.authenticated
        this.username = response.data.username || ''
      } catch {
        this.isAuthenticated = false
        this.username = ''
      }
    },
    async login(username, password) {
      const response = await axios.post('/api/login', { username, password })
      this.isAuthenticated = true
      this.username = response.data.username
      return response.data
    },
    async logout() {
      await axios.post('/api/logout')
      this.isAuthenticated = false
      this.username = ''
    }
  }
})
