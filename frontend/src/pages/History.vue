<template>
  <div class="history-view">
    <el-card class="history-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>识别历史记录</h2>
          <div class="header-meta">
            <el-tag v-if="serverAvailable" type="success" size="small" effect="plain">服务端同步</el-tag>
            <el-tag v-else type="warning" size="small" effect="plain">本地数据</el-tag>
            <el-button size="small" :icon="Refresh" :loading="loading" @click="loadAll">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-container">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="情绪">
            <el-select v-model="searchForm.emotion" placeholder="选择情绪" clearable>
              <el-option v-for="(key, emotion) in cnToEnMap" :key="key" :label="`${emotionEmojiMap[key]} ${emotion}`" :value="emotion" />
            </el-select>
          </el-form-item>
          <el-form-item label="模型">
            <el-select v-model="searchForm.model" placeholder="选择模型" clearable>
              <el-option label="CNN" value="CNN" />
              <el-option label="VGG" value="VGG" />
              <el-option label="SE81" value="SE81" />
              <el-option label="SE83" value="SE83" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-config-provider :locale="zhCn">
              <el-date-picker v-model="searchForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" clearable />
            </el-config-provider>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="search">搜索</el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="info" plain @click="analyzeStorage">分析存储空间</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="warning" plain @click="cleanupStorage">清理本地图片</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="danger" plain @click="batchDelete" :disabled="selectedRecords.length === 0">
              批量删除 ({{ selectedRecords.length }})
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="filteredPredictions.length > 0">
        <el-table
          :data="filteredPredictions"
          style="width: 100%"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="情绪" width="120">
            <template #default="{ row }">
              <span style="font-size: 1.5rem; margin-right: 0.5rem;">{{ getEmotionEmoji(row.emotion) }}</span>
              <span>{{ row.emotion_cn }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="confidence" label="置信度" width="150">
            <template #default="{ row }">
              <el-progress :percentage="Math.round(row.confidence * 100)" :color="getProgressColor(row.confidence)" />
            </template>
          </el-table-column>

          <el-table-column prop="model_used" label="模型" width="100" />

          <el-table-column label="来源" width="150">
            <template #default="{ row }">
              <el-tag v-if="row.source === 'video'" type="success">
                视频 {{ row.video_time || `帧 #${row.frame_number ?? ''}` }}
              </el-tag>
              <el-tag v-else effect="plain">图片识别</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="存储" width="90">
            <template #default="{ row }">
              <el-tag :type="row.origin === 'server' ? 'success' : 'info'" size="small" effect="plain">
                {{ row.origin === 'server' ? '服务端' : '本地' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="{ row }">{{ formatFullTime(row.timestamp) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" plain @click="viewDetails(row)">查看详情</el-button>
              <el-button size="small" type="danger" plain @click="deleteRecord(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="search-result-info" v-if="isSearching">共找到 {{ filteredPredictions.length }} 条记录</div>
      </div>

      <el-empty v-else :description="loading ? '正在加载历史记录...' : (isSearching ? '未找到符合条件的记录' : '暂无识别记录')" />
    </el-card>

    <el-dialog v-model="showDetailDialog" title="识别详情" width="900px" :close-on-click-modal="false">
      <div v-if="selectedPrediction" class="result-content">
        <div class="image-compare" v-if="selectedPrediction.imageUrl || selectedPrediction.preprocessed_image">
          <div class="image-box">
            <div class="image-title">{{ selectedPrediction.source === 'video' ? '视频原始帧' : '原始图片' }}</div>
            <img v-if="selectedPrediction.imageUrl" :src="selectedPrediction.imageUrl" alt="原始图" />
            <div v-else class="no-image">无原始图片</div>
          </div>
          <div class="image-box">
            <div class="image-title">{{ selectedPrediction.source === 'video' ? '检测到的人脸' : '人脸区域' }}</div>
            <img v-if="selectedPrediction.preprocessed_image" :src="selectedPrediction.preprocessed_image" alt="检测到的人脸" />
            <div v-else class="no-image">无人脸区域数据</div>
          </div>
        </div>

        <div class="main-emotion">
          <div class="emotion-icon">{{ getEmotionEmoji(selectedPrediction.emotion) }}</div>
          <div class="emotion-info">
            <h2>{{ selectedPrediction.emotion_cn }}</h2>
            <p class="emotion-en">{{ selectedPrediction.emotion }}</p>
            <el-progress :percentage="Math.round(selectedPrediction.confidence * 100)" :color="getProgressColor(selectedPrediction.confidence)" :stroke-width="20" />
            <p class="confidence-text">置信度: {{ (selectedPrediction.confidence * 100).toFixed(2) }}%</p>
          </div>
        </div>

        <!-- 详细概率分布 -->
        <el-divider>详细概率分布</el-divider>
        <div class="probability-list" v-if="selectedPrediction.probabilities_cn || selectedPrediction.probabilities">
          <div
            v-for="(prob, emotion) in (selectedPrediction.probabilities_cn || selectedPrediction.probabilities)"
            :key="emotion"
            class="probability-item"
          >
            <div class="prob-label">
              <span class="prob-emoji">{{ getEmotionEmoji(getEnglishEmotion(emotion)) }}</span>
              <span>{{ emotion }}</span>
            </div>
            <el-progress
              :percentage="Math.round(prob * 100)"
              :show-text="true"
              :stroke-width="12"
            />
          </div>
        </div>

        <div class="meta-info">
          <el-tag effect="plain">模型: {{ selectedPrediction.model_used }}</el-tag>
          <el-tag type="info" effect="plain">时间: {{ formatFullTime(selectedPrediction.timestamp) }}</el-tag>
          <el-tag v-if="selectedPrediction.serverId" type="warning" effect="plain">编号: #{{ selectedPrediction.serverId }}</el-tag>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeDetailDialog">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useEmotionStore } from '../stores/emotion'
import { useVideoStore } from '../stores/video'
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { printStorageReport } from '../utils/storageAnalyzer'
import { resolveAssetUrl } from '../utils/assets'
import dbHelper, { STORES } from '../utils/indexedDB'

const emotionStore = useEmotionStore()
const videoStore = useVideoStore()

const loading = ref(false)
const serverAvailable = ref(false)

// 挂载时同时加载服务端历史与本地缓存
onMounted(async () => {
  await loadAll()
  // 本地缓存为空时兜底重载一次
  if (emotionStore.predictions.length === 0) {
    await emotionStore.loadFromStorage()
  }
})

async function loadAll() {
  loading.value = true
  try {
    // 并行：拉取服务端历史 + 确保本地缓存已加载
    await Promise.all([
      emotionStore.fetchServerHistories(100, 3),
      emotionStore.predictions.length === 0 ? emotionStore.loadFromStorage() : Promise.resolve()
    ])
    serverAvailable.value = !emotionStore.serverHistoriesError
  } finally {
    loading.value = false
  }
}

// 服务端记录 → 展示结构（图片经 /api/uploads 鉴权加载）
function mapServerRecord(rec) {
  const isVideo = (rec.input_type || 'image') === 'video'
  const frameTs = typeof rec.frame_timestamp === 'number' ? rec.frame_timestamp : null
  const mm = frameTs !== null ? String(Math.floor(frameTs / 60)).padStart(2, '0') : null
  const ss = frameTs !== null ? String(Math.floor(frameTs % 60)).padStart(2, '0') : null
  return {
    id: `server-${rec.id}`,
    serverId: rec.id,
    historyId: rec.id,
    emotion: rec.emotion,
    emotion_cn: rec.emotion_cn,
    confidence: rec.confidence,
    model_used: rec.model_used,
    timestamp: rec.created_at,
    source: isVideo ? 'video' : 'image',
    frame_number: rec.frame_index,
    video_time: mm !== null ? `${mm}:${ss}` : '',
    imageUrl: resolveAssetUrl(rec.original_image_path || rec.thumbnail_path || rec.preprocessed_image_path),
    preprocessed_image: resolveAssetUrl(rec.preprocessed_image_path || rec.thumbnail_path),
    probabilities: rec.probabilities?.en || null,
    probabilities_cn: rec.probabilities?.cn || null,
    origin: 'server'
  }
}

// 本地图片预测 → 展示结构
function mapLocalPrediction(pred) {
  return {
    ...pred,
    id: `local-${pred.id}`,
    historyId: pred.history_id ?? null,
    imageUrl: pred.original_image || pred.image,
    preprocessed_image: pred.face_image || pred.preprocessed_image,
    model_used: pred.model_used || pred.model,
    source: 'image',
    origin: 'local'
  }
}

// 本地视频帧 → 展示结构
function mapLocalVideoFrame(frame, video) {
  return {
    emotion: frame.emotion,
    emotion_cn: frame.emotion_cn,
    confidence: frame.confidence,
    timestamp: video.timestamp,
    video_time: frame.time_formatted,
    model_used: video.model || 'CNN',
    source: 'video',
    video_id: video.video_id,
    localVideoDbId: video.id,
    frame_number: frame.frame_number || frame.frame_index,
    imageUrl: frame.original_frame,
    preprocessed_image: frame.face_image,
    probabilities_cn: frame.probabilities_cn,
    probabilities: frame.probabilities,
    origin: 'local'
  }
}

// 合并记录：服务端优先，本地补遗（无服务端ID的旧记录）
const allHistoryRecords = computed(() => {
  const records = []
  const serverOk = serverAvailable.value

  if (serverOk) {
    const serverVideoExists = emotionStore.serverHistories.some((r) => (r.input_type || 'image') === 'video')
    const serverHistoryIds = new Set(
      emotionStore.serverHistories.map((r) => r.id)
    )

    records.push(...emotionStore.serverHistories.map(mapServerRecord))

    // 本地图片预测中没有服务端ID的（历史遗留/离线数据）
    ;(emotionStore.predictions || []).forEach((pred) => {
      if (pred.history_id && serverHistoryIds.has(pred.history_id)) return
      if (pred.history_id) return // 服务端已有同ID记录（可能超出分页范围）
      records.push(mapLocalPrediction(pred))
    })

    // 服务端没有任何视频帧记录时，用本地视频历史兜底展示
    if (!serverVideoExists) {
      ;(videoStore.videoHistory || []).forEach((video) => {
        if (video.results?.timeline && Array.isArray(video.results.timeline)) {
          video.results.timeline.forEach((frame) => records.push(mapLocalVideoFrame(frame, video)))
        }
      })
    }
  } else {
    // 服务端不可用：完整本地合并
    ;(emotionStore.predictions || []).forEach((pred) => records.push(mapLocalPrediction(pred)))
    ;(videoStore.videoHistory || []).forEach((video) => {
      if (video.results?.timeline && Array.isArray(video.results.timeline)) {
        video.results.timeline.forEach((frame) => records.push(mapLocalVideoFrame(frame, video)))
      }
    })
  }

  return records.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

// 详情对话框相关状态
const showDetailDialog = ref(false)
const selectedPrediction = ref(null)

// 搜索相关状态
const searchForm = ref({
  emotion: '',
  model: '',
  dateRange: []
})
const isSearching = ref(false)

// 批量删除相关
const selectedRecords = ref([])

// 过滤后的预测数据
const filteredPredictions = computed(() => {
  if (!isSearching.value) {
    return allHistoryRecords.value
  }

  return allHistoryRecords.value.filter(prediction => {
    // 情绪过滤
    if (searchForm.value.emotion) {
      const hasMatch =
        (prediction.emotion_cn && prediction.emotion_cn === searchForm.value.emotion) ||
        (prediction.emotion && cnToEnMap[searchForm.value.emotion] === prediction.emotion)

      if (!hasMatch) return false
    }

    // 模型过滤
    if (searchForm.value.model && !String(prediction.model_used || '').includes(searchForm.value.model)) {
      return false
    }

    // 时间范围过滤
    if (searchForm.value.dateRange && searchForm.value.dateRange.length === 2) {
      const [startDate, endDate] = searchForm.value.dateRange
      const predictionDate = new Date(prediction.timestamp).toISOString().split('T')[0]
      if (predictionDate < startDate || predictionDate > endDate) {
        return false
      }
    }

    return true
  })
})

// 搜索函数
function search() {
  isSearching.value = true
}

// 重置搜索
function resetSearch() {
  searchForm.value = {
    emotion: '',
    model: '',
    dateRange: []
  }
  isSearching.value = false
}

// 清理本地 IndexedDB 中的图片数据（真实本地功能）
async function cleanupStorage() {
  ElMessageBox.confirm(
    '此操作将清理本地缓存中的图片数据以释放浏览器存储空间，但会保留情绪分析结果和统计信息（服务端记录不受影响）。是否继续？',
    '清理本地图片缓存',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      let username = 'guest'
      if (emotionStore.getCurrentUsername) {
        try {
          const u = await emotionStore.getCurrentUsername()
          if (u) username = u
        } catch {}
      }

      const videoHistory = await dbHelper.getByIndex(STORES.VIDEO_HISTORY, 'username', username)

      if (videoHistory && videoHistory.length > 0) {
        for (const item of videoHistory) {
          const cleanedItem = {
            ...item,
            results: {
              ...item.results,
              timeline: item.results?.timeline?.map(frame => ({
                frame_number: frame.frame_number,
                frame_index: frame.frame_index,
                timestamp: frame.timestamp,
                time_formatted: frame.time_formatted,
                emotion: frame.emotion,
                emotion_cn: frame.emotion_cn,
                confidence: frame.confidence,
                probabilities: frame.probabilities,
                probabilities_cn: frame.probabilities_cn
              })) || []
            }
          }
          await dbHelper.put(STORES.VIDEO_HISTORY, cleanedItem)
        }
      }

      const currentAnalysis = await dbHelper.get(STORES.VIDEO_ANALYSIS, username)
      if (currentAnalysis) {
        const cleanedAnalysis = {
          ...currentAnalysis,
          analysisResults: {
            ...currentAnalysis.analysisResults,
            timeline: currentAnalysis.analysisResults?.timeline?.map(frame => ({
              frame_number: frame.frame_number,
              frame_index: frame.frame_index,
              timestamp: frame.timestamp,
              time_formatted: frame.time_formatted,
              emotion: frame.emotion,
              emotion_cn: frame.emotion_cn,
              confidence: frame.confidence,
              probabilities: frame.probabilities,
              probabilities_cn: frame.probabilities_cn
            })) || []
          }
        }
        await dbHelper.put(STORES.VIDEO_ANALYSIS, cleanedAnalysis)
      }

      const imageCount = await emotionStore.cleanupImageData?.()
      if (imageCount && imageCount > 0) {
        console.log(`已清理图片预测图片数据: ${imageCount} 条`)
      }

      ElMessage.success('本地图片缓存清理完成！服务端历史记录不受影响')

      await emotionStore.loadFromStorage?.()
      await videoStore.loadFromStorage?.()
    } catch (error) {
      console.error('清理本地存储失败:', error)
      ElMessage.error('清理失败：' + error.message)
    }
  }).catch(() => {
    ElMessage.info('已取消清理')
  })
}

// 分析本地存储空间使用情况
async function analyzeStorage() {
  try {
    ElMessage.info('正在分析浏览器本地存储空间...')
    const report = await printStorageReport()

    const h = (v) => (v ?? 0)
    let message = `总使用: ${report.indexedDB.totalMB} MB (${report.indexedDB.percentage}%)\n`
    message += `存储限制: ${(report.indexedDB.limit / 1024 / 1024).toFixed(2)} MB\n`
    message += `可用空间: ${((report.indexedDB.limit - report.indexedDB.total) / 1024 / 1024).toFixed(2)} MB\n\n`

    message += `存储详情：\n`
    message += `- 视频历史: ${h(report.indexedDB.stores.VIDEO_HISTORY?.count)} 条 (${h(report.indexedDB.stores.VIDEO_HISTORY?.sizeMB)} MB)\n`
    message += `- 当前分析: ${h(report.indexedDB.stores.VIDEO_ANALYSIS?.count)} 条 (${h(report.indexedDB.stores.VIDEO_ANALYSIS?.sizeMB)} MB)\n`
    message += `- 图片预测: ${h(report.indexedDB.stores.IMAGE_PREDICTIONS?.count)} 条 (${h(report.indexedDB.stores.IMAGE_PREDICTIONS?.sizeMB)} MB)\n`
    message += `- 用户数据: ${h(report.indexedDB.stores.USER_DATA?.count)} 条 (${h(report.indexedDB.stores.USER_DATA?.sizeMB)} MB)\n`
    message += `- 应用设置: ${h(report.indexedDB.stores.APP_SETTINGS?.count)} 条 (${h(report.indexedDB.stores.APP_SETTINGS?.sizeMB)} MB)\n\n`

    const hasImages =
      report.indexedDB.stores.VIDEO_HISTORY?.hasImages ||
      report.indexedDB.stores.VIDEO_ANALYSIS?.hasImages ||
      report.indexedDB.stores.IMAGE_PREDICTIONS?.hasImages

    if (hasImages) {
      message += `检测到本地图片数据，可通过"清理本地图片"释放空间\n\n`
    }

    if (report.warnings.length > 0) {
      message += `提示：\n`
      report.warnings.forEach(w => {
        message += `- ${w.message}\n`
      })
    } else {
      message += `存储使用正常`
    }

    ElMessageBox.alert(message.replace(/\n/g, '<br/>'), '浏览器本地存储分析', {
      confirmButtonText: '确定',
      type: report.indexedDB.percentage > 80 ? 'warning' : 'info',
      dangerouslyUseHTMLString: true
    })
  } catch (error) {
    console.error('分析存储空间失败:', error)
    ElMessage.error('分析失败：' + error.message)
  }
}

// 情绪到emoji的映射
const emotionEmojiMap = {
  anger: '😠',
  disgust: '🤢',
  fear: '😨',
  happy: '😊',
  normal: '😐',
  sad: '😢',
  surprised: '😲'
}

// 中文到英文映射
const cnToEnMap = {
  '生气': 'anger',
  '厌恶': 'disgust',
  '害怕': 'fear',
  '高兴': 'happy',
  '平静': 'normal',
  '悲伤': 'sad',
  '惊讶': 'surprised'
}

function getEmotionEmoji(emotion) {
  return emotionEmojiMap[emotion] || '😐'
}

function getEnglishEmotion(cnEmotion) {
  return cnToEnMap[cnEmotion] || 'normal'
}

function getProgressColor(confidence) {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

function formatFullTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 查看详情
function viewDetails(row) {
  selectedPrediction.value = JSON.parse(JSON.stringify(row))
  showDetailDialog.value = true
}

// 关闭详情对话框
function closeDetailDialog() {
  showDetailDialog.value = false
  selectedPrediction.value = null
}

// 删除记录（服务端记录走 API，本地记录走 IndexedDB）
function deleteRecord(row) {
  ElMessageBox.confirm(
    row.origin === 'server'
      ? '确定要删除这条服务端记录吗？此操作不可恢复！'
      : `确定要删除这条${row.source === 'video' ? '视频的全部本地帧记录' : '本地识别'}记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      if (row.origin === 'server') {
        await emotionStore.deleteServerHistory(row.serverId)
        ElMessage.success('已从服务端删除该记录')
      } else if (row.source === 'video') {
        const video = videoStore.videoHistory.find(v => v.video_id === row.video_id)
        if (video) {
          videoStore.deleteHistoryItem(video.id)
          ElMessage.success('已删除该视频的本地帧记录')
        }
      } else {
        const localId = row.id.replace(/^local-/, '')
        await emotionStore.deletePrediction(Number(localId) || localId)
        ElMessage.success('删除成功')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败：' + (error.response?.data?.error || error.message))
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 选择变化处理
function handleSelectionChange(selection) {
  selectedRecords.value = selection
}

// 批量删除记录
function batchDelete() {
  const count = selectedRecords.value.length
  if (count === 0) return

  ElMessageBox.confirm(
    `确定要删除选中的 ${count} 条记录吗？此操作不可恢复！`,
    '批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    let successCount = 0
    let failCount = 0

    const serverRecords = selectedRecords.value.filter(r => r.origin === 'server')
    const localImageRecords = selectedRecords.value.filter(r => r.origin === 'local' && r.source === 'image')
    const videoIds = new Set(selectedRecords.value.filter(r => r.origin === 'local' && r.source === 'video').map(r => r.video_id))

    // 服务端逐条删除
    for (const record of serverRecords) {
      try {
        await emotionStore.deleteServerHistory(record.serverId)
        successCount++
      } catch (err) {
        console.error('删除服务端记录失败:', err)
        failCount++
      }
    }

    // 本地图片记录
    for (const record of localImageRecords) {
      try {
        const localId = record.id.replace(/^local-/, '')
        await emotionStore.deletePrediction(Number(localId) || localId)
        successCount++
      } catch (err) {
        console.error('删除本地图片记录失败:', err)
        failCount++
      }
    }

    // 本地视频记录（按 video_id 去重）
    for (const videoId of videoIds) {
      try {
        const video = videoStore.videoHistory.find(v => v.video_id === videoId)
        if (video) {
          videoStore.deleteHistoryItem(video.id)
          successCount++
        }
      } catch (err) {
        console.error('删除本地视频记录失败:', err)
        failCount++
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount} 条记录${failCount > 0 ? `，失败 ${failCount} 条` : ''}`)
    } else {
      ElMessage.error('删除失败')
    }

    selectedRecords.value = []
  }).catch(() => {
    // 用户取消删除
  })
}
</script>

<style scoped>
.history-view {
  width: 100%;
  max-width: 1600px;
}

/* 搜索栏样式 */
.search-container {
  margin-bottom: 20px;
}

.search-form {
  background-color: var(--el-color-primary-light-9);
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 0;
  align-items: center;
  width: 100%;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 4px;
  margin-right: 16px;
  flex-shrink: 0;
}

.search-form :deep(.el-form-item:last-child) {
  margin-right: 0;
}

.search-result-info {
  text-align: right;
  color: var(--color-mahogany);
  margin-top: 10px;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  letter-spacing: -0.01em;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* 识别结果内容样式 */
.result-content {
  padding: 10px 0;
}

/* 图片对比区域 */
.image-compare {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.image-box {
  text-align: center;
  margin-bottom: 20px;
  width: 300px;
}

.image-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--color-mahogany);
}

.image-box img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid var(--color-sand);
  background: var(--el-color-primary-light-9);
}

.no-image {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-color-primary-light-9);
  border: 1px dashed var(--color-sand);
  border-radius: 8px;
  color: var(--color-mahogany);
}

/* 主要情绪显示 */
.main-emotion {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 30px 0;
  padding: 24px;
  background: var(--color-accent);
  border-radius: 16px;
  color: #fafafa;
}

.emotion-icon {
  font-size: 7rem;
  margin-right: 30px;
}

.emotion-info {
  flex: 1;
  text-align: left;
}

.emotion-info h2 {
  margin: 0 0 10px 0;
  font-size: 2.25rem;
  letter-spacing: -0.02em;
}

.emotion-en {
  margin: 0 0 20px 0;
  opacity: 0.8;
  font-size: 1.2rem;
}

.confidence-text {
  margin: 10px 0 0 0;
  font-size: 1.1rem;
  font-weight: 600;
}

/* 概率分布 */
.probability-list {
  margin-bottom: 30px;
}

.probability-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: var(--el-color-primary-light-9);
  border-radius: 8px;
}

.prob-label {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.prob-emoji {
  font-size: 1.5rem;
  margin-right: 10px;
}

/* 元信息 */
.meta-info {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-emotion {
    flex-direction: column;
    text-align: center;
  }

  .emotion-icon {
    margin-right: 0;
    margin-bottom: 20px;
    font-size: 5rem;
  }

  .emotion-info {
    text-align: center;
  }

  .image-compare {
    flex-direction: column;
    align-items: center;
  }
}
</style>
