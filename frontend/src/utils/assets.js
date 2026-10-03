/**
 * 服务端资源（头像、识别图片、视频帧）URL 解析
 * 后端 /api/uploads/<path> 需要 JWT：Header 不可用于 <img>，统一以 ?token= 传递
 */
export function getAuthToken() {
  return localStorage.getItem('token') || ''
}

/**
 * 将后端存储的相对路径解析为可直接访问的 URL
 * 支持：http(s) 完整地址、data: URL、/uploads 相对路径
 */
export function resolveAssetUrl(path) {
  if (!path) return ''
  if (/^(https?:|data:|blob:)/i.test(path)) return path
  const clean = String(path).replace(/^\/+/, '')
  if (clean.startsWith('api/')) return `/${clean}?token=${encodeURIComponent(getAuthToken())}`
  return `/api/uploads/${clean}?token=${encodeURIComponent(getAuthToken())}`
}

/** 从预测记录中取可展示的图片（服务端路径优先，其次本地 base64） */
export function resolveRecordImage(record) {
  if (!record) return ''
  return (
    resolveAssetUrl(record.thumbnail_path) ||
    resolveAssetUrl(record.preprocessed_image_path) ||
    resolveAssetUrl(record.original_image_path) ||
    record.face_image ||
    record.image ||
    record.original_image ||
    ''
  )
}
