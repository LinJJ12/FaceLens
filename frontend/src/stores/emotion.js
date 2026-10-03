import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'
import {
  saveImagePredictions, 
  loadImagePredictions, 
  clearImagePredictions,
  cleanupImagePredictionData 
} from '../utils/imagePredictionDB'

export const useEmotionStore = defineStore('emotion', () => {
  const isHealthy = ref(false)
  const availableModels = ref([])
  const currentModel = ref('cnn')
  const predictions = ref([])
  const isLoading = ref(false)
  const currentPrediction = ref(null) // 当前正在查看的预测结果
  // 服务端历史（/api/histories），供历史/分析页共用
  const serverHistories = ref([])
  const serverHistoriesTotal = ref(0)
  const serverHistoriesLoading = ref(false)
  const serverHistoriesError = ref(false)

  // 获取当前用户名（与 video store 保持一致，直接读 localStorage 的登录态。
  // 此前经由 IndexedDB 的 storageManager 读取，登录/登出不会同步过去，
  // 会导致预测记录串号或"丢失"）
  async function getCurrentUsername() {
    try {
      const userInfo = localStorage.getItem('userInfo')
      if (userInfo) {
        const user = JSON.parse(userInfo)
        return user.username || 'guest'
      }
    } catch (error) {
      console.error('获取用户名失败:', error)
    }
    return 'guest'
  }

  // 从 IndexedDB 加载数据（按用户名隔离）
  async function loadFromStorage() {
    try {
      const username = await getCurrentUsername()
      
      console.log(`🔄 [EmotionStore] 开始从 IndexedDB 加载用户数据 [用户: ${username}]`)
      
      // 先清空旧数据，防止显示上一个用户的数据
      predictions.value = []
      currentPrediction.value = null
      
      const data = await loadImagePredictions(username)
      
      if (data) {
        predictions.value = data.predictions || []
        currentPrediction.value = data.currentPrediction || null
        console.log(`✅ 成功从 IndexedDB 恢复用户 ${username} 的图片分析数据:`, predictions.value.length, '条记录')
      } else {
        console.log(`ℹ️  用户 ${username} 暂无历史数据`)
      }
    } catch (error) {
      console.error('❌ 从 IndexedDB 加载数据失败:', error)
      predictions.value = []
      currentPrediction.value = null
    }
  }

  // 保存到 IndexedDB（按用户名隔离）
  async function saveToStorage() {
    try {
      const username = await getCurrentUsername()
      
      await saveImagePredictions(
        predictions.value,
        currentPrediction.value,
        currentModel.value,
        username
      )
      
      console.log(`✅ 图片预测已保存到 IndexedDB（包含完整数据）[用户: ${username}]`)
    } catch (error) {
      console.error('❌ 保存图片预测到 IndexedDB 失败:', error)
    }
  }

  // 清理图片数据
  async function cleanupImageData() {
    try {
      const username = await getCurrentUsername()
      const count = await cleanupImagePredictionData(username)
      console.log(`✅ 已清理 ${count} 条图片预测的图片数据`)
      
      // 重新加载数据
      await loadFromStorage()
      return count
    } catch (error) {
      console.error('❌ 清理图片数据失败:', error)
      return 0
    }
  }

  // 检查后端健康状态
  async function checkHealth() {
    try {
      const response = await api.get('/health')
      isHealthy.value = response.data.status === 'ok'
      availableModels.value = response.data.available_models || []
      return true
    } catch (error) {
      console.error('后端服务连接失败:', error)
      isHealthy.value = false
      return false
    }
  }

  // 获取可用模型
  async function fetchModels() {
    try {
      const response = await api.get('/models')
      availableModels.value = response.data.models
    } catch (error) {
      console.error('获取模型列表失败:', error)
    }
  }

  // 从服务端拉取识别历史（多页，带兜底）
  async function fetchServerHistories(perPage = 100, maxPages = 3) {
    serverHistoriesLoading.value = true
    serverHistoriesError.value = false
    try {
      const response = await api.get('/histories', { params: { page: 1, per_page: perPage } })
      const total = response.data.total || 0
      const all = [...(response.data.histories || [])]
      const totalPages = Math.min(Math.ceil(total / perPage) || 1, maxPages)
      for (let p = 2; p <= totalPages; p++) {
        try {
          const next = await api.get('/histories', { params: { page: p, per_page: perPage } })
          all.push(...(next.data.histories || []))
        } catch (error) {
          break
        }
      }
      serverHistories.value = all
      serverHistoriesTotal.value = total
      return all
    } catch (error) {
      console.error('获取服务端历史失败:', error)
      serverHistoriesError.value = true
      return []
    } finally {
      serverHistoriesLoading.value = false
    }
  }

  // 删除服务端历史记录（仅本人）
  async function deleteServerHistory(serverId) {
    await api.delete(`/histories/${serverId}`)
    serverHistories.value = serverHistories.value.filter((h) => h.id !== serverId)
    serverHistoriesTotal.value = Math.max(0, serverHistoriesTotal.value - 1)
  }

  // 预测情绪
  async function predictEmotion(imageData, detectFace = true) {
    isLoading.value = true
    try {
      const response = await api.post('/predict', {
        image: imageData,
        model: currentModel.value,
        detect_face: detectFace
      })
      
      if (response.data.success) {
        // 保存原始图片数据到预测结果中
        const predictionWithImage = {
          ...response.data,
          // 保存图片数据（使用统一的字段名）
          image: imageData,  // 原始上传的图片
          original_image: imageData,  // 原始图片（与 image 相同）
          face_image: response.data.preprocessed_image,  // 人脸区域图片
          // 保存模型信息
          model: response.data.model_used,  // 从 model_used 复制到 model
          // 服务端记录ID（用于与服务端历史去重/删除）
          history_id: response.data.history_id ?? null,
          // 添加唯一ID
          id: Date.now(),
          // 保留后端返回的所有其他字段
          imageUrl: imageData  // 向后兼容旧代码
        }
        predictions.value.unshift(predictionWithImage)
        currentPrediction.value = predictionWithImage
        
        // 保存到 IndexedDB
        await saveToStorage()
        
        return predictionWithImage
      }
      return null
    } catch (error) {
      console.error('预测失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 设置当前预测结果
  async function setCurrentPrediction(prediction) {
    currentPrediction.value = prediction
    await saveToStorage()
  }

  // 清除当前预测结果
  async function clearCurrentPrediction() {
    currentPrediction.value = null
    await saveToStorage()
  }

  // 删除预测记录
  async function deletePrediction(id) {
    // 🧹 删除指定记录（该记录的图片数据会被自动释放）
    // 其他记录保持不变，包括它们的图片
    predictions.value = predictions.value.filter(p => p.id !== id)
    if (currentPrediction.value?.id === id) {
      currentPrediction.value = null
    }
    await saveToStorage()
    console.log(`🗑️ 已删除预测记录并释放该记录的图片数据 [ID: ${id}]`)
  }

  // 清除所有预测记录
  async function clearAllPredictions() {
    const username = await getCurrentUsername()
    await clearImagePredictions(username)
    predictions.value = []
    currentPrediction.value = null
    console.log('🗑️ 已清空所有预测记录')
  }

  // 批量预测
  async function batchPredict(images, detectFace = true) {
    isLoading.value = true
    try {
      const response = await api.post('/batch_predict', {
        images,
        model: currentModel.value,
        detect_face: detectFace
      })
      return response.data
    } catch (error) {
      console.error('批量预测失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 初始化时加载数据（延迟执行以确保 IndexedDB 已准备好）
  setTimeout(async () => {
    const username = await getCurrentUsername()
    if (username && username !== 'guest') {
      console.log(`📸 [EmotionStore] 初始化从 IndexedDB 加载用户数据 [用户: ${username}]`)
      await loadFromStorage()
    } else {
      console.log('📸 [EmotionStore] 未检测到登录用户，等待登录后加载数据')
    }
  }, 200)

  return {
    isHealthy,
    availableModels,
    currentModel,
    predictions,
    isLoading,
    currentPrediction,
    serverHistories,
    serverHistoriesTotal,
    serverHistoriesLoading,
    serverHistoriesError,
    checkHealth,
    fetchModels,
    fetchServerHistories,
    deleteServerHistory,
    predictEmotion,
    batchPredict,
    setCurrentPrediction,
    clearCurrentPrediction,
    deletePrediction,
    clearAllPredictions,
    saveToStorage,
    loadFromStorage,
    getCurrentUsername,
    cleanupImageData  // 🆕 导出清理函数
  }
})
