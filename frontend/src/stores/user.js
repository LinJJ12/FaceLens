import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/client'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const isLoading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const userInfo = computed(() => user.value)
  const userRole = computed(() => user.value?.role || 'user')
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 设置用户信息
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('userInfo', JSON.stringify(userData))
  }

  // 设置token
  const setToken = (newToken, newRefreshToken = '') => {
    token.value = newToken
    refreshToken.value = newRefreshToken
    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
  }

  // 清除用户信息
  const clearUser = () => {
    user.value = null
    token.value = ''
    refreshToken.value = ''
    localStorage.removeItem('userInfo')
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    // 注意：不清除 lastLoginUsername 和历史记录，
    // 这样同一用户重新登录时可以保留历史记录
  }

  // 登录
  const login = async (credentials) => {
    try {
      isLoading.value = true
      const response = await api.post('/auth/login', credentials)
      
      const { user: userData, token: newToken, refreshToken: newRefreshToken } = response.data
      
      setUser(userData)
      setToken(newToken, newRefreshToken)
      
      // 登录成功后，通知 emotion store 和 video store 重新加载当前用户的数据
      // 这样会自动从对应的用户键加载历史记录
      try {
        const { useEmotionStore } = await import('./emotion')
        const emotionStore = useEmotionStore()
        emotionStore.loadFromStorage()
        
        const { useVideoStore } = await import('./video')
        const videoStore = useVideoStore()
        videoStore.loadFromStorage()
        
        console.log('✅ 已重新加载用户的图片和视频历史记录')
      } catch (error) {
        console.error('重新加载用户历史记录失败:', error)
      }
      
      ElMessage.success('登录成功！')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('登录失败:', error)
      const errorMessage = error.response?.data?.error || '登录失败，请重试'
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      isLoading.value = true
      const response = await api.post('/auth/register', userData)
      
      ElMessage.success('注册成功！请登录')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('注册失败:', error)
      const errorMessage = error.response?.data?.error || '注册失败，请重试'
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/auth/logout', {}, {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        })
      }
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      clearUser()
      ElMessage.success('已退出登录')
    }
  }

  // 刷新token
  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      const response = await api.post('/auth/refresh', {
        refreshToken: refreshToken.value
      })

      const { token: newToken, refreshToken: newRefreshToken } = response.data
      setToken(newToken, newRefreshToken)
      
      return newToken
    } catch (error) {
      console.error('Token刷新失败:', error)
      clearUser()
      throw error
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      if (!token.value) {
        return false
      }

      const response = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      setUser(response.data.user)
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      if (error.response?.status === 401) {
        // Token过期，尝试刷新
        try {
          await refreshAccessToken()
          return await fetchUserInfo()
        } catch (refreshError) {
          clearUser()
          return false
        }
      }
      return false
    }
  }

  // 更新用户信息
  const updateUserInfo = async (userData) => {
    try {
      isLoading.value = true
      const response = await api.put('/auth/profile', userData, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      setUser(response.data.user)
      ElMessage.success('用户信息更新成功')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('更新用户信息失败:', error)
      const errorMessage = error.response?.data?.error || '更新失败，请重试'
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 修改密码
  const changePassword = async (passwordData) => {
    try {
      isLoading.value = true
      await api.post('/auth/change-password', passwordData, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      ElMessage.success('密码修改成功')
      return { success: true }
    } catch (error) {
      console.error('修改密码失败:', error)
      const errorMessage = error.response?.data?.error || '修改失败，请重试'
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 忘记密码
  const forgotPassword = async (email) => {
    try {
      isLoading.value = true
      await api.post('/auth/forgot-password', { email })
      
      ElMessage.success('重置密码链接已发送到您的邮箱')
      return { success: true }
    } catch (error) {
      console.error('发送重置邮件失败:', error)
      const errorMessage = error.response?.data?.error || '发送失败，请重试'
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 初始化用户状态（从localStorage恢复）
  const initializeUser = () => {
    try {
      const savedUserInfo = localStorage.getItem('userInfo')
      const savedToken = localStorage.getItem('token')
      
      if (savedUserInfo && savedToken) {
        user.value = JSON.parse(savedUserInfo)
        token.value = savedToken
        refreshToken.value = localStorage.getItem('refreshToken') || ''
        
        // 验证token是否仍然有效
        fetchUserInfo()
      }
    } catch (error) {
      console.error('初始化用户状态失败:', error)
      clearUser()
    }
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    isLoading,
    
    // 计算属性
    isLoggedIn,
    userInfo,
    userRole,
    isAdmin,
    
    // 方法
    setUser,
    setToken,
    clearUser,
    login,
    register,
    logout,
    refreshAccessToken,
    fetchUserInfo,
    updateUserInfo,
    changePassword,
    forgotPassword,
    initializeUser
  }
})
