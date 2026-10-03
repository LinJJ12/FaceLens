<template>
  <div class="history-view">
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <h2>识别历史记录</h2>
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
            <el-button type="info" @click="analyzeStorage">分析存储空间</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="warning" @click="cleanupStorage">清理存储空间</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="danger" @click="batchDelete" :disabled="selectedRecords.length === 0">
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

          <el-table-column label="来源" width="140">
            <template #default="{ row }">
              <el-tag v-if="row.source === 'video'" type="success">视频帧 #{{ row.frame_number }}</el-tag>
              <el-tag v-else type="primary">图片识别</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="{ row }">{{ formatFullTime(row.timestamp) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="viewDetails(row)">查看详情</el-button>
              <el-button size="small" type="danger" @click="deleteRecord(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="search-result-info" v-if="isSearching">共找到 {{ filteredPredictions.length }} 条记录</div>
      </div>

      <el-empty v-else :description="isSearching ? '未找到符合条件的记录' : '暂无识别记录'" />
    </el-card>

    <el-dialog v-model="showDetailDialog" title="📊 识别详情" width="900px" :close-on-click-modal="false">
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
          <el-tag>模型: {{ selectedPrediction.model_used }}</el-tag>
          <el-tag type="info">时间: {{ formatFullTime(selectedPrediction.timestamp) }}</el-tag>
          <el-tag v-if="selectedPrediction.id" type="warning">编号: {{ selectedPrediction.id }}</el-tag>
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
import { useEmotionStore } from '../stores/emotion'
import { useVideoStore } from '../stores/video'
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { printStorageReport } from '../utils/storageAnalyzer'
import dbHelper, { STORES } from '../utils/indexedDB'

const emotionStore = useEmotionStore()
const videoStore = useVideoStore()

// 组件挂载时确保数据已加载
onMounted(async () => {
  console.log('📜 [History] 组件挂载，检查数据加载状态')
  console.log('📸 图片预测数据:', emotionStore.predictions.length, '条')
  console.log('🎬 视频历史数据:', videoStore.videoHistory.length, '条')
  
  // 如果数据为空，尝试重新加载
  if (emotionStore.predictions.length === 0) {
    console.log('⚠️ 图片预测数据为空，尝试重新加载...')
    await emotionStore.loadFromStorage()
  }
  
  // 打印第一条数据用于调试
  if (emotionStore.predictions.length > 0) {
    const firstPred = emotionStore.predictions[0]
    console.log('📊 第一条图片预测数据（原始）:', {
      emotion: firstPred.emotion,
      model: firstPred.model,
      hasImage: !!firstPred.image,
      hasOriginalImage: !!firstPred.original_image,
      hasFaceImage: !!firstPred.face_image,
      imageLength: firstPred.image?.length,
      originalImageLength: firstPred.original_image?.length,
      faceImageLength: firstPred.face_image?.length,
      allKeys: Object.keys(firstPred)
    })
  }
})

// 合并图片识别和视频分析的所有历史记录（仅当前会话的本地数据）
const allHistoryRecords = computed(() => {
  // 映射图片识别数据的字段名
  const imagePredictions = (emotionStore.predictions || []).map((pred, index) => {
    const mapped = {
      ...pred,
      // 映射图片字段到详情对话框期望的字段
      imageUrl: pred.original_image || pred.image,  // 原始图片
      preprocessed_image: pred.face_image,  // 人脸区域
      model_used: pred.model,
      source: 'image'
    }
    
    // 调试：打印映射后的数据（仅第一条）
    if (index === 0 && pred) {
      console.log('🔍 映射后的图片预测数据（第一条）:', {
        hasImageUrl: !!mapped.imageUrl,
        hasPreprocessedImage: !!mapped.preprocessed_image,
        model_used: mapped.model_used,
        imageUrlLength: mapped.imageUrl?.length,
        preprocessedImageLength: mapped.preprocessed_image?.length
      })
    }
    
    return mapped
  })
  
  const videoPredictions = []
  
  // 从视频历史记录中提取所有帧的预测结果
  if (videoStore.videoHistory && Array.isArray(videoStore.videoHistory)) {
    videoStore.videoHistory.forEach(video => {
      if (video.results && video.results.timeline && Array.isArray(video.results.timeline)) {
        video.results.timeline.forEach(frame => {
          videoPredictions.push({
            emotion: frame.emotion,
            emotion_cn: frame.emotion_cn,
            confidence: frame.confidence,
            // 使用视频分析的时间戳，而不是视频中的相对时间
            timestamp: video.timestamp,
            // 保留视频内的相对时间用于显示
            video_time: frame.time_formatted,  // 视频时间戳（如 "00:05"）
            time_formatted: frame.time_formatted,
            model_used: video.model || 'CNN',
            source: 'video',
            video_id: video.video_id,
            frame_number: frame.frame_number || frame.frame_index,
            // 映射视频帧的图片字段到详情对话框期望的字段
            imageUrl: frame.original_frame,  // 原始视频帧
            preprocessed_image: frame.face_image,  // 检测到的人脸
            // 保留概率分布
            probabilities_cn: frame.probabilities_cn,
            probabilities: frame.probabilities
          })
        })
      }
    })
  }
  
  return [...imagePredictions, ...videoPredictions].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  )
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
      // 尝试匹配emotion_cn，如果不存在则使用emotion字段的中文映射
      const hasMatch = 
        (prediction.emotion_cn && prediction.emotion_cn === searchForm.value.emotion) ||
        (prediction.emotion && cnToEnMap[searchForm.value.emotion] === prediction.emotion)
      
      if (!hasMatch) return false
    }
    
    // 模型过滤
    if (searchForm.value.model && !prediction.model_used.includes(searchForm.value.model)) {
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

// 清理存储空间（移除历史记录中的图片数据）
async function cleanupStorage() {
  ElMessageBox.confirm(
    '此操作将清理历史记录中的图片数据以释放存储空间，但会保留情绪分析结果和统计信息。是否继续？',
    '清理存储空间',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      // 统一从 EmotionStore 获取当前用户名（异步，确保与 IndexedDB 用户隔离一致）
      let username = 'guest'
      if (emotionStore.getCurrentUsername) {
        try {
          const u = await emotionStore.getCurrentUsername()
          if (u) username = u
        } catch {}
      }
      
      // 🧹 清理 IndexedDB 中的视频历史图片数据
      console.log('🧹 [清理] 开始清理 IndexedDB 视频历史数据...')
      
      // 1. 获取当前用户的所有视频历史记录
      const videoHistory = await dbHelper.getByIndex(STORES.VIDEO_HISTORY, 'username', username)
      
      if (videoHistory && videoHistory.length > 0) {
        console.log(`📊 找到 ${videoHistory.length} 条视频历史记录`)
        
        // 2. 清理每条记录中的图片数据
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
                // 移除 original_frame, face_image 等图片字段
              })) || []
            }
          }
          
          // 更新 IndexedDB 中的记录
          await dbHelper.put(STORES.VIDEO_HISTORY, cleanedItem)
        }
        
        console.log('✅ 视频历史记录图片数据已清理')
      }
      
      // 3. 清理当前分析的图片数据
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
        console.log('✅ 当前视频分析图片数据已清理')
      }
      
      // 4. 清理图片预测历史（IndexedDB）
      const imageCount = await emotionStore.cleanupImageData?.()
      if (imageCount && imageCount > 0) {
        console.log(`✅ 图片预测历史图片数据已清理: ${imageCount} 条`)
      }
      
      ElMessage.success('存储空间清理完成！已移除所有历史记录中的图片数据')
      
      // 重新加载数据
      await emotionStore.loadFromStorage?.()
      await videoStore.loadFromStorage?.()
    } catch (error) {
      console.error('❌ 清理存储空间失败:', error)
      ElMessage.error('清理失败：' + error.message)
    }
  }).catch(() => {
    ElMessage.info('已取消清理')
  })
}

// 分析存储空间使用情况（仅 IndexedDB）
async function analyzeStorage() {
  try {
    ElMessage.info('正在分析 IndexedDB 存储空间，请查看控制台...')
    const report = await printStorageReport()
    
    // 构建弹窗消息
    let message = `📊 IndexedDB 存储空间分析\n\n`
    message += `�️ 总使用: ${report.indexedDB.totalMB} MB (${report.indexedDB.percentage}%)\n`
    message += `� 存储限制: ${(report.indexedDB.limit / 1024 / 1024).toFixed(2)} MB\n`
    message += `💚 可用空间: ${((report.indexedDB.limit - report.indexedDB.total) / 1024 / 1024).toFixed(2)} MB\n\n`
    
    // 详细信息
    message += `📝 存储详情：\n`
    message += `- 视频历史: ${report.indexedDB.stores.VIDEO_HISTORY?.count || 0} 条 (${report.indexedDB.stores.VIDEO_HISTORY?.sizeMB || 0} MB)\n`
    message += `- 当前分析: ${report.indexedDB.stores.VIDEO_ANALYSIS?.count || 0} 条 (${report.indexedDB.stores.VIDEO_ANALYSIS?.sizeMB || 0} MB)\n`
    message += `- 图片预测: ${report.indexedDB.stores.IMAGE_PREDICTIONS?.count || 0} 条 (${report.indexedDB.stores.IMAGE_PREDICTIONS?.sizeMB || 0} MB)\n`
    message += `- 用户数据: ${report.indexedDB.stores.USER_DATA?.count || 0} 条 (${report.indexedDB.stores.USER_DATA?.sizeMB || 0} MB)\n`
    message += `- 应用设置: ${report.indexedDB.stores.APP_SETTINGS?.count || 0} 条 (${report.indexedDB.stores.APP_SETTINGS?.sizeMB || 0} MB)\n\n`
    
    // 图片检测
    const hasImages = 
      report.indexedDB.stores.VIDEO_HISTORY?.hasImages ||
      report.indexedDB.stores.VIDEO_ANALYSIS?.hasImages ||
      report.indexedDB.stores.IMAGE_PREDICTIONS?.hasImages
    
    if (hasImages) {
      message += `🖼️ 检测到图片数据，可通过"清理存储空间"释放空间\n\n`
    }
    
    // 警告
    if (report.warnings.length > 0) {
      message += `⚠️ 提示：\n`
      report.warnings.forEach(w => {
        const icon = w.level === 'danger' ? '🔴' : w.level === 'warning' ? '🟡' : 'ℹ️'
        message += `${icon} ${w.message}\n`
      })
    } else {
      message += `✅ 存储使用正常`
    }
    
    ElMessageBox.alert(message, 'IndexedDB 存储空间分析', {
      confirmButtonText: '确定',
      type: report.indexedDB.percentage > 80 ? 'warning' : 'info',
      dangerouslyUseHTMLString: false
    })
    
    console.log('💡 详细信息已输出到控制台，请按 F12 查看')
  } catch (error) {
    console.error('❌ 分析存储空间失败:', error)
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

function getQualityColor(score) {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
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
  // 深拷贝确保不修改原始数据
  selectedPrediction.value = JSON.parse(JSON.stringify(row))
  showDetailDialog.value = true
}

// 关闭详情对话框
function closeDetailDialog() {
  showDetailDialog.value = false
  selectedPrediction.value = null
}

// 删除记录
function deleteRecord(row) {
  ElMessageBox.confirm(
    `确定要删除这条${row.source === 'video' ? '视频帧' : '图片识别'}记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    if (row.source === 'video') {
      // 删除视频记录：需要找到对应的视频并删除整个视频
      const videoId = row.video_id
      const video = videoStore.videoHistory.find(v => v.video_id === videoId)
      if (video) {
        videoStore.deleteHistoryItem(video.id)
        ElMessage.success('已删除该视频的所有帧记录')
      }
    } else {
      // 删除图片识别记录（使用 id 字段）
      if (row.id) {
        emotionStore.deletePrediction(row.id)
        ElMessage.success('删除成功')
      } else {
        ElMessage.error('无法删除：记录缺少ID')
      }
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
  ).then(() => {
    let successCount = 0
    let failCount = 0
    
    // 分别处理图片和视频记录
    const imageRecords = selectedRecords.value.filter(r => r.source === 'image')
    const videoIds = new Set(selectedRecords.value.filter(r => r.source === 'video').map(r => r.video_id))
    
    // 删除图片记录
    imageRecords.forEach(record => {
      try {
        if (record.id) {
          emotionStore.deletePrediction(record.id)
          successCount++
        }
      } catch (err) {
        console.error('删除图片记录失败:', err)
        failCount++
      }
    })
    
    // 删除视频记录（按video_id去重）
    videoIds.forEach(videoId => {
      try {
        const video = videoStore.videoHistory.find(v => v.video_id === videoId)
        if (video) {
          videoStore.deleteHistoryItem(video.id)
          successCount++
        }
      } catch (err) {
        console.error('删除视频记录失败:', err)
        failCount++
      }
    })
    
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
  max-width: 1600px; /* 增大布局宽度以容纳所有按钮 */
}

/* 搜索栏样式 */
.search-container {
  margin-bottom: 20px;
}

.search-form {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  display: flex;
  flex-wrap: nowrap; /* 强制单行显示 */
  align-items: center;
  width: fit-content; /* 让表单宽度适应内容 */
  min-width: 100%; /* 最小宽度100% */
}

.search-form :deep(.el-form-item) {
  margin-bottom: 0; /* 移除底部间距 */
  margin-right: 20px; /* 增大按钮间距 */
  flex-shrink: 0; /* 防止表单项收缩 */
}

.search-form :deep(.el-form-item:last-child) {
  margin-right: 15px; /* 最后一个按钮保持合适的右边距 */
}

.search-result-info {
  text-align: right;
  color: #606266;
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
  font-weight: bold;
  margin-bottom: 10px;
  color: #606266;
}

.image-box img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}

.image-note {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}

.no-image {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  color: #909399;
}

/* 主要情绪显示 */
.main-emotion {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 30px 0;
  padding: 20px;
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  border-radius: 16px;
  color: white;
}

.emotion-icon {
  font-size: 8rem;
  margin-right: 30px;
}

.emotion-info {
  flex: 1;
  text-align: left;
}

.emotion-info h2 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
}

.emotion-en {
  margin: 0 0 20px 0;
  opacity: 0.8;
  font-size: 1.2rem;
}

.confidence-text {
  margin: 10px 0 0 0;
  font-size: 1.1rem;
  font-weight: bold;
}

/* 概率分布 */
.probability-list {
  margin-bottom: 30px;
}

.probability-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f9f9f9;
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

/* 人脸质量评估 */
.quality-info {
  margin-bottom: 30px;
}

.quality-score {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.quality-level {
  margin-left: 30px;
  font-size: 1.2rem;
}

.quality-percentage {
  font-size: 1.2rem;
  font-weight: bold;
}

.quality-details {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
}

.quality-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  width: 200px;
}

.quality-item span {
  margin: 0 10px;
  min-width: 60px;
}

.quality-warnings {
  margin-top: 20px;
}

/* 性能信息 */
.performance-info {
  margin-bottom: 30px;
}

/* 元信息 */
.meta-info {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #909399;
  background-color: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 30px;
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
    font-size: 6rem;
  }
  
  .emotion-info {
    text-align: center;
  }
  
  .image-compare {
    flex-direction: column;
    align-items: center;
  }
  
  .quality-score {
    flex-direction: column;
  }
  
  .quality-level {
    margin-left: 0;
    margin-top: 20px;
  }
  
  .quality-details {
    flex-direction: column;
    align-items: center;
  }
  
  .quality-item {
    width: 100%;
    justify-content: center;
  }
}
</style>
