import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import dbHelper, { STORES } from '../utils/indexedDB'
import { saveVideoHistory, loadVideoHistory, deleteVideoHistoryItem, clearVideoHistory } from '../utils/videoHistoryDB'

export const useVideoStore = defineStore('video', () => {
  // 状态
  const currentVideo = ref(null) // 当前上传的视频信息
  const analysisResults = ref(null) // 当前分析结果
  const isUploading = ref(false) // 是否正在上传
  const isAnalyzing = ref(false) // 是否正在分析
  const uploadProgress = ref(0) // 上传进度
  const analysisProgress = ref(0) // 分析进度
  const videoHistory = ref([]) // 视频分析历史记录

  // 🔑 获取当前登录的用户名（从 localStorage 的 userInfo 中提取）
  function getCurrentUsername() {
    try {
      const userInfo = localStorage.getItem('userInfo')
      if (userInfo) {
        const parsed = JSON.parse(userInfo)
        return parsed.username || null
      }
    } catch (e) {
      console.error('解析 userInfo 失败:', e)
    }
    return null
  }

  // 🧹 深度清理数据，移除不可序列化的对象（函数、循环引用等）
  function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') {
      return obj
    }
    
    // 处理日期对象
    if (obj instanceof Date) {
      return obj.toISOString()
    }
    
    // 处理数组
    if (Array.isArray(obj)) {
      return obj.map(item => deepClone(item))
    }
    
    // 处理普通对象
    const cloned = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key]
        // 跳过函数和 undefined
        if (typeof value === 'function' || value === undefined) {
          continue
        }
        cloned[key] = deepClone(value)
      }
    }
    return cloned
  }

  // 计算属性
  const hasVideo = computed(() => currentVideo.value !== null)
  const hasResults = computed(() => analysisResults.value !== null)
  const totalFrames = computed(() => {
    return analysisResults.value?.total_frames || 0
  })
  const emotionTimeline = computed(() => {
    return analysisResults.value?.timeline || null
  })
  const emotionFlow = computed(() => {
    return analysisResults.value?.emotion_flow || ''
  })
  const emotionTransitions = computed(() => {
    return analysisResults.value?.transitions || []
  })
  const statistics = computed(() => {
    return analysisResults.value?.statistics || null
  })

  // 方法
  function setCurrentVideo(videoInfo) {
    currentVideo.value = videoInfo
  }

  async function setAnalysisResults(results) {
    console.log('🎬 [VideoStore] setAnalysisResults 被调用')
    console.log('🎬 [VideoStore] 原始 results:', results)
    console.log('🎬 [VideoStore] timeline 类型:', typeof results?.timeline)
    console.log('🎬 [VideoStore] timeline 是否为数组:', Array.isArray(results?.timeline))
    
    // 规范化数据结构：后端返回的 timeline 是一个对象，包含 timeline, emotion_sequence 等
    // 我们需要将 timeline.timeline（数组）提取出来作为主要的 timeline 数据
    if (results && results.timeline && typeof results.timeline === 'object' && !Array.isArray(results.timeline)) {
      console.log('📝 [VideoStore] 规范化 timeline 数据结构')
      console.log('📝 [VideoStore] timeline.timeline:', results.timeline.timeline)
      results = {
        ...results,
        timeline: results.timeline.timeline || [], // 提取实际的帧数组
        emotion_sequence: results.timeline.emotion_sequence || [],
        emotion_flow: results.timeline.emotion_flow || '',
        transitions: results.timeline.transitions || []
      }
      console.log('📝 [VideoStore] 规范化后的 results:', results)
    }
    
    analysisResults.value = results
    console.log('✅ [VideoStore] analysisResults 已更新')
    
    // 保存完整数据到 IndexedDB
    await saveCurrentAnalysis()
    console.log('✅ [VideoStore] 当前分析已保存到 IndexedDB')
    
    // 保存到历史记录
    if (results && currentVideo.value) {
      // 🔍 检查是否已经存在相同 video_id 的记录（避免重复添加）
      const existingIndex = videoHistory.value.findIndex(
        item => item.video_id === currentVideo.value.video_id
      )
      
      if (existingIndex !== -1) {
        console.log('⚠️ [VideoStore] 该视频已存在历史记录，更新而非新增')
        // 更新现有记录
        videoHistory.value[existingIndex] = {
          ...videoHistory.value[existingIndex],
          results: results,
          timestamp: new Date().toISOString(),
          model: results.model_used
        }
      } else {
        // 添加新记录
        const historyItem = {
          id: Date.now(),
          video_id: currentVideo.value.video_id,
          video_info: currentVideo.value.video_info,
          thumbnail: currentVideo.value.thumbnail,
          results: results,
          timestamp: new Date().toISOString(),
          model: results.model_used
        }
        
        console.log('📚 [VideoStore] 添加新历史记录:', historyItem.id)
        videoHistory.value.unshift(historyItem)
        
        // 限制历史记录数量
        if (videoHistory.value.length > 20) {
          videoHistory.value = videoHistory.value.slice(0, 20)
        }
      }
      
      // 保存到 IndexedDB
      await saveHistory()
      console.log('✅ [VideoStore] 历史记录已保存到 IndexedDB，当前记录数:', videoHistory.value.length)
    } else {
      console.warn('⚠️ [VideoStore] 无法保存历史记录 - results 或 currentVideo 为空')
    }
  }

  function clearCurrentVideo() {
    currentVideo.value = null
    analysisResults.value = null
    uploadProgress.value = 0
    analysisProgress.value = 0
  }

  function setUploadProgress(progress) {
    uploadProgress.value = progress
  }

  function setAnalysisProgress(progress) {
    analysisProgress.value = progress
  }

  function startUpload() {
    isUploading.value = true
    uploadProgress.value = 0
  }

  function finishUpload() {
    isUploading.value = false
    uploadProgress.value = 100
  }

  function startAnalysis() {
    isAnalyzing.value = true
    analysisProgress.value = 0
  }

  function finishAnalysis() {
    isAnalyzing.value = false
    analysisProgress.value = 100
  }

  async function saveCurrentAnalysis() {
    try {
      const username = getCurrentUsername()
      
      console.log(`💾 [VideoStore] 保存当前分析到 IndexedDB [用户: ${username}]`)
      
      // 深度克隆数据，移除不可序列化的对象
      const cleanData = {
        username,
        currentVideo: deepClone(currentVideo.value),
        analysisResults: deepClone(analysisResults.value),
        timestamp: new Date().toISOString()
      }
      
      // 保存完整的当前分析结果（包括图片）到 IndexedDB
      await dbHelper.put(STORES.VIDEO_ANALYSIS, cleanData)
      
      console.log(`✅ 当前分析已保存到 IndexedDB（包含完整数据）[用户: ${username}]`)
    } catch (error) {
      console.error('❌ 保存当前视频分析失败:', error)
    }
  }

  async function loadCurrentAnalysis() {
    try {
      const username = getCurrentUsername()
      
      console.log(`📂 [VideoStore] 从 IndexedDB 加载当前分析 [用户: ${username}]`)
      
      // VIDEO_ANALYSIS 使用 username 作为主键，直接用 get() 方法
      const data = await dbHelper.get(STORES.VIDEO_ANALYSIS, username)
      
      if (data) {
        currentVideo.value = data.currentVideo
        
        // 规范化 timeline 数据
        let results = data.analysisResults
        if (results?.timeline && typeof results.timeline === 'object' && !Array.isArray(results.timeline)) {
          console.log('📝 [VideoStore] 规范化当前分析的 timeline 数据')
          results = {
            ...results,
            timeline: results.timeline.timeline || [],
            emotion_sequence: results.timeline.emotion_sequence || [],
            emotion_flow: results.timeline.emotion_flow || '',
            transitions: results.timeline.transitions || []
          }
        }
        
        analysisResults.value = results
        console.log(`✅ 成功从 IndexedDB 恢复视频分析数据 [用户: ${username}]`)
        return true
      }
    } catch (error) {
      console.error('❌ 从 IndexedDB 加载当前视频分析失败:', error)
    }
    return false
  }

  async function saveHistory() {
    const username = getCurrentUsername()
    await saveVideoHistory(videoHistory.value, username)
  }

  async function loadHistory() {
    const username = getCurrentUsername()
    videoHistory.value = await loadVideoHistory(username)
  }

  async function deleteHistoryItem(id) {
    await deleteVideoHistoryItem(id)
    videoHistory.value = videoHistory.value.filter(item => item.id !== id)
  }

  async function clearHistory() {
    const username = getCurrentUsername()
    await clearVideoHistory(username)
    videoHistory.value = []
  }

  async function clearCurrentAnalysis() {
    const username = getCurrentUsername()
    // VIDEO_ANALYSIS 使用 username 作为主键，直接用 delete() 方法
    await dbHelper.delete(STORES.VIDEO_ANALYSIS, username)
    console.log(`🗑️ 已从 IndexedDB 清空当前视频分析 [用户: ${username}]`)
  }
  
  // 🔄 重新加载当前用户的数据（用于用户切换后）
  async function loadFromStorage() {
    const username = getCurrentUsername()
    console.log(`🔄 [VideoStore] 重新加载用户数据 [用户: ${username}]`)
    
    // 清空旧数据
    currentVideo.value = null
    analysisResults.value = null
    videoHistory.value = []
    
    // 加载新用户数据（从 IndexedDB）
    await loadHistory()
    await loadCurrentAnalysis()
  }

  // 初始化时加载数据（如果已经有用户登录）
  // 延迟执行以确保 localStorage 中的 userInfo 已经加载
  setTimeout(async () => {
    const username = getCurrentUsername()
    if (username) {
      console.log(`🎬 [VideoStore] 初始化加载用户数据 [用户: ${username}]`)
      // 从 IndexedDB 加载完整数据
      await loadHistory()
      await loadCurrentAnalysis()
    } else {
      console.log('🎬 [VideoStore] 未检测到登录用户，等待登录后加载数据')
    }
  }, 100)

  return {
    // 状态
    currentVideo,
    analysisResults,
    isUploading,
    isAnalyzing,
    uploadProgress,
    analysisProgress,
    videoHistory,
    
    // 计算属性
    hasVideo,
    hasResults,
    totalFrames,
    emotionTimeline,
    emotionFlow,
    emotionTransitions,
    statistics,
    
    // 方法
    setCurrentVideo,
    setAnalysisResults,
    clearCurrentVideo,
    setUploadProgress,
    setAnalysisProgress,
    startUpload,
    finishUpload,
    startAnalysis,
    finishAnalysis,
    deleteHistoryItem,
    clearHistory,
    saveCurrentAnalysis,
    loadCurrentAnalysis,
    clearCurrentAnalysis,
    loadFromStorage, // 🆕 用户切换时重新加载
    getCurrentUsername // 🆕 暴露给外部使用
  }
})
