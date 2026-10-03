/**
 * 心理健康API接口
 * 用于调用后端心理健康相关的接口
 */

import api from './client'

/**
 * 获取情绪统计汇总
 * @param {string} date - 日期 (YYYY-MM-DD)
 * @param {number} days - 查询天数
 */
export const getEmotionSummary = async (date = null, days = 1) => {
  try {
    const params = {}
    if (date) params.date = date
    if (days > 1) params.days = days

    const response = await api.get('/health/emotion-summary', { params })
    return response.data
  } catch (error) {
    console.error('获取情绪汇总失败:', error)
    throw error
  }
}

/**
 * 获取心理健康评估
 * @param {string} date - 日期 (YYYY-MM-DD)
 */
export const getHealthAssessment = async (date = null) => {
  try {
    const params = {}
    if (date) params.date = date

    const response = await api.get('/health/assessment', { params })
    return response.data
  } catch (error) {
    console.error('获取健康评估失败:', error)
    throw error
  }
}

/**
 * 保存情绪日记
 * @param {object} data - 日记数据
 * @param {string} data.content - 日记内容
 * @param {string} data.emotion - 情绪(可选)
 * @param {string} data.emotion_cn - 情绪中文(可选)
 */
export const saveJournal = async (data) => {
  try {
    const response = await api.post('/health/journal', data)
    return response.data
  } catch (error) {
    console.error('保存日记失败:', error)
    throw error
  }
}

/**
 * 获取情绪日记列表
 * @param {number} limit - 查询数量限制
 * @param {number} offset - 偏移量
 */
export const getJournals = async (limit = 50, offset = 0) => {
  try {
    const response = await api.get('/health/journal', { 
      params: { limit, offset } 
    })
    return response.data
  } catch (error) {
    console.error('获取日记列表失败:', error)
    throw error
  }
}

/**
 * 获取单条日记详情
 * @param {number} journalId - 日记ID
 */
export const getJournal = async (journalId) => {
  try {
    const response = await api.get(`/health/journal/${journalId}`)
    return response.data
  } catch (error) {
    console.error('获取日记详情失败:', error)
    throw error
  }
}

/**
 * 更新日记
 * @param {number} journalId - 日记ID
 * @param {object} data - 更新数据
 * @param {string} data.content - 日记内容
 */
export const updateJournal = async (journalId, data) => {
  try {
    const response = await api.put(`/health/journal/${journalId}`, data)
    return response.data
  } catch (error) {
    console.error('更新日记失败:', error)
    throw error
  }
}

/**
 * 删除日记
 * @param {number} journalId - 日记ID
 */
export const deleteJournal = async (journalId) => {
  try {
    const response = await api.delete(`/health/journal/${journalId}`)
    return response.data
  } catch (error) {
    console.error('删除日记失败:', error)
    throw error
  }
}

/**
 * 保存感恩记录
 * @param {object} data - 感恩记录数据
 * @param {string[]} data.items - 感恩事项列表
 */
export const saveGratitude = async (data) => {
  try {
    const response = await api.post('/health/gratitude', data)
    return response.data
  } catch (error) {
    console.error('保存感恩记录失败:', error)
    throw error
  }
}

/**
 * 获取感恩记录列表
 * @param {number} limit - 查询数量限制
 */
export const getGratitudes = async (limit = 50) => {
  try {
    const response = await api.get('/health/gratitude', { 
      params: { limit } 
    })
    return response.data
  } catch (error) {
    console.error('获取感恩记录列表失败:', error)
    throw error
  }
}

/**
 * 获取单条感恩记录详情
 * @param {number} gratitudeId - 感恩记录ID
 */
export const getGratitude = async (gratitudeId) => {
  try {
    const response = await api.get(`/health/gratitude/${gratitudeId}`)
    return response.data
  } catch (error) {
    console.error('获取感恩记录详情失败:', error)
    throw error
  }
}

/**
 * 删除感恩记录
 * @param {number} gratitudeId - 感恩记录ID
 */
export const deleteGratitude = async (gratitudeId) => {
  try {
    const response = await api.delete(`/health/gratitude/${gratitudeId}`)
    return response.data
  } catch (error) {
    console.error('删除感恩记录失败:', error)
    throw error
  }
}

export default {
  getEmotionSummary,
  getHealthAssessment,
  saveJournal,
  getJournals,
  getJournal,
  updateJournal,
  deleteJournal,
  saveGratitude,
  getGratitudes,
  getGratitude,
  deleteGratitude
}
