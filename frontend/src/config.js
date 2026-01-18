// API配置 - 支持环境变量
// 生产环境通过 .env.production 配置，开发环境默认使用 localhost:5000
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
