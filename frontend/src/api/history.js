/**
 * 服务端识别历史 API
 * 对应后端 /api/histories（按当前用户过滤，page/per_page 分页）
 */
import api from './client'

/**
 * 分页获取当前用户的历史记录
 * @returns {Promise<{histories: Array, total: number, page: number}>}
 */
export async function fetchHistories(page = 1, perPage = 50) {
  const response = await api.get('/histories', { params: { page, per_page: perPage } })
  return {
    histories: response.data.histories || [],
    total: response.data.total || 0,
    page: response.data.page || page
  }
}

/**
 * 拉取多页历史（用于数据分析统计场景），最多拉取 maxPages 页
 */
export async function fetchAllHistories(perPage = 100, maxPages = 5) {
  const first = await fetchHistories(1, perPage)
  const all = [...first.histories]
  const totalPages = Math.min(Math.ceil(first.total / perPage) || 1, maxPages)
  for (let p = 2; p <= totalPages; p++) {
    try {
      const next = await fetchHistories(p, perPage)
      all.push(...next.histories)
    } catch (error) {
      break
    }
  }
  return all
}

/** 删除一条历史记录（仅本人） */
export async function deleteHistory(id) {
  const response = await api.delete(`/histories/${id}`)
  return response.data
}

/** 将服务端记录映射为前端展示结构（图片经 /api/uploads 鉴权访问） */
export function mapServerHistory(record) {
  return {
    id: `server-${record.id}`,
    serverId: record.id,
    historyId: record.id,
    emotion: record.emotion,
    emotion_cn: record.emotion_cn,
    confidence: record.confidence,
    model: record.model_used,
    timestamp: record.created_at,
    input_type: record.input_type || 'image',
    frame_timestamp: record.frame_timestamp,
    frame_index: record.frame_index,
    probabilities: record.probabilities?.en || record.probabilities || null,
    probabilities_cn: record.probabilities?.cn || null,
    source: 'server',
    imagePath: record.thumbnail_path || record.preprocessed_image_path || record.original_image_path || ''
  }
}
