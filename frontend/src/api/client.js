import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,  // 5分钟超时，适用于视频分析等耗时操作
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 刷新令牌的单飞（single-flight）：并发多个 401 时只发一次刷新请求。
// 后端 refreshToken 是一次性的，若每个 401 各自刷新，除第一个外都会失败并误登出。
let refreshPromise = null

function clearCredentials() {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userInfo')
}

function redirectToLogin() {
  // 项目使用 hash 路由（createWebHashHistory），pathname 永远是 '/'，
  // 必须用 hash 跳转，否则整页重载
  if (window.location.hash.startsWith('#/login')) return
  const current = window.location.hash.slice(1) || '/'
  window.location.hash = `#/login?redirect=${encodeURIComponent(current)}`
}

async function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) throw new Error('no refresh token')
      const response = await axios.post('/api/auth/refresh', { refreshToken })
      const { token, refreshToken: newRefreshToken } = response.data
      localStorage.setItem('token', token)
      localStorage.setItem('refreshToken', newRefreshToken)
      return token
    })().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    const status = error.response?.status
    const data = error.response?.data || {}

    if (status === 401) {
      const token = localStorage.getItem('token')
      const refreshToken = localStorage.getItem('refreshToken')

      if (token && refreshToken && !error.config._retry) {
        error.config._retry = true
        try {
          const newToken = await refreshAccessToken()
          error.config.headers.Authorization = `Bearer ${newToken}`
          return api(error.config)
        } catch (refreshError) {
          // 刷新失败，清除用户信息并跳转到登录页
          clearCredentials()
          redirectToLogin()
          ElMessage.error('登录已过期，请重新登录')
          return Promise.reject(error)
        }
      }

      // 无刷新令牌可用：清理并提示（不再静默失败）
      if (error.config._retry || !refreshToken) {
        clearCredentials()
        redirectToLogin()
        ElMessage.error('登录已过期，请重新登录')
      }
      return Promise.reject(error)
    }

    let message = data.error || data.message || '请求失败'
    if (status === 400) message = data.error || '请求参数错误'
    else if (status === 403) message = data.error || '没有权限访问此资源'
    else if (status === 404) message = data.error || '请求的资源不存在'
    else if (status === 413) message = data.error || '上传内容过大'
    else if (status === 500) message = data.error || '服务器错误'
    else if (!error.response) message = '无法连接到服务器'

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api
