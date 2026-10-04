<template>
  <div class="analysis-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>数据分析中心</h1>
          <p>深入了解您的情绪模式和变化趋势</p>
        </div>
        <el-button size="small" type="primary" @click="exportPDFReport" :loading="isExporting">
          <el-icon><document /></el-icon>
          导出分析报告
        </el-button>
      </div>
    </div>

    <!-- 空状态提示 -->
    <el-card class="empty-state-card" shadow="hover" v-if="totalPredictions === 0">
      <el-empty description="还没有数据">
        <template #image>
          <el-icon style="font-size: 72px; color: #CBD5E1;"><component :is="'DataAnalysis'" /></el-icon>
        </template>
        <p style="color: var(--color-mahogany); margin-bottom: 1rem;">
          请先在首页上传照片进行情绪识别，系统会为您生成详细的数据分析
        </p>
        <el-button type="primary" @click="$router.push('/home')">
          前往首页识别
        </el-button>
      </el-empty>
      <el-divider />
      <div style="color: var(--color-mahogany); line-height: 1.8;">
        <h3 style="margin-bottom: 1rem;">数据分析功能预览</h3>
        <ul style="padding-left: 2rem;">
          <li>情绪分布饼图 - 直观展示各种情绪占比</li>
          <li>情绪趋势折线图 - 追踪情绪随时间的变化</li>
          <li>置信度分布统计 - 了解识别准确度分布</li>
          <li>24小时活动分析 - 发现情绪规律</li>
          <li>日历热力图 - GitHub风格的活跃度展示</li>
          <li>详细数据表格 - 支持搜索、导出、删除</li>
        </ul>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards" v-else>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
              <el-icon><data-line /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalPredictions }}</div>
              <div class="stat-label">总识别次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
              <el-icon><avatar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dominantEmotion }}</div>
              <div class="stat-label">主导情绪</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
              <el-icon><trend-charts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ avgConfidence }}%</div>
              <div class="stat-label">平均置信度</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
              <el-icon><calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ activeDays }}</div>
              <div class="stat-label">活跃天数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据来源统计 -->
    <el-card class="data-source-card" shadow="hover" v-if="totalPredictions > 0">
      <template #header>
        <div class="card-header">
          <span>数据来源分布</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <div class="source-stat">
            <div class="source-icon" style="background: var(--el-color-primary-light-9)">
              📸
            </div>
            <div class="source-info">
              <div class="source-value">{{ imageCount }}</div>
              <div class="source-label">图片识别</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <div class="source-stat">
            <div class="source-icon" style="background: var(--el-color-primary-light-9)">
              🎬
            </div>
            <div class="source-info">
              <div class="source-value">{{ videoCount }}</div>
              <div class="source-label">视频帧分析</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <div class="source-stat">
            <div class="source-icon" style="background: var(--el-color-primary-light-9)">
              📹
            </div>
            <div class="source-info">
              <div class="source-value">{{ videoStore.videoHistory.length }}</div>
              <div class="source-label">视频文件数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 视频情绪变化分析 -->
    <el-card class="video-analysis-card" shadow="hover" v-if="videoStore.videoHistory.length > 0">
      <template #header>
        <div class="card-header">
          <span>视频情绪变化趋势</span>
          <div style="display: flex; gap: 10px; align-items: center;">
            <el-select 
              v-model="selectedVideoId" 
              placeholder="选择视频" 
              size="small" 
              style="width: 280px"
              filterable
              clearable
              @clear="selectedVideoId = null"
            >
              <el-option
                v-for="video in videoStore.videoHistory"
                :key="video.video_id"
                :label="`${video.video_id} (${video.results?.total_frames || 0}帧)`"
                :value="video.video_id"
              >
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ video.video_id.slice(0, 20) }}{{ video.video_id.length > 20 ? '...' : '' }}</span>
                  <el-tag size="small" type="info">{{ video.results?.total_frames || 0 }}帧</el-tag>
                </div>
              </el-option>
            </el-select>
            <el-button 
              v-if="selectedVideoId" 
              size="small" 
              type="danger" 
              @click="deleteSelectedVideo"
              :icon="Delete"
            >
              删除此视频
            </el-button>
            <el-tag v-if="videoStore.videoHistory.length > 0" type="info" size="small">
              共 {{ videoStore.videoHistory.length }} 个视频
            </el-tag>
          </div>
        </div>
      </template>
      
      <!-- 视频快速选择列表 -->
      <div v-if="videoStore.videoHistory.length > 1" class="video-quick-list">
        <el-scrollbar max-height="120px">
          <div class="video-list-container">
            <div 
              v-for="video in videoStore.videoHistory" 
              :key="video.video_id"
              class="video-item"
              :class="{ active: selectedVideoId === video.video_id }"
              @click="selectedVideoId = video.video_id"
            >
              <div class="video-item-content">
                <div class="video-item-icon">🎬</div>
                <div class="video-item-info">
                  <div class="video-item-name">{{ video.video_id.slice(0, 25) }}{{ video.video_id.length > 25 ? '...' : '' }}</div>
                  <div class="video-item-meta">
                    <el-tag size="small" type="info">{{ video.results?.total_frames || 0 }}帧</el-tag>
                    <span class="video-item-time">{{ formatTime(video.timestamp) }}</span>
                  </div>
                </div>
                <el-button 
                  size="small" 
                  type="danger" 
                  :icon="Delete"
                  circle
                  @click.stop="deleteVideo(video)"
                />
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
      
      <div v-if="selectedVideoData">
        <div class="video-summary">
          <el-row :gutter="16">
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-label">总帧数</div>
                <div class="summary-value">{{ selectedVideoData.total_frames }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-label">主要情绪</div>
                <div class="summary-value">{{ selectedVideoData.dominant_emotion }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-label">平均置信度</div>
                <div class="summary-value">{{ selectedVideoData.avg_confidence }}%</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="summary-item">
                <div class="summary-label">情绪稳定性</div>
                <div class="summary-value">{{ selectedVideoData.stability }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
        <div ref="videoEmotionChart" class="chart-container" style="margin-top: 20px;"></div>
        <div class="video-insights">
          <el-alert :title="selectedVideoData.insight_title" :type="selectedVideoData.insight_type" :closable="false">
            <p>{{ selectedVideoData.insight_description }}</p>
          </el-alert>
        </div>
      </div>
      <el-empty v-else description="请选择一个视频查看详细分析" />
    </el-card>

    <!-- 情绪健康评分卡片 -->
    <el-card class="health-score-card" shadow="hover" v-if="totalPredictions > 0">
      <div class="health-score-content">
        <div class="score-left">
          <div class="score-circle" :class="healthScore.level">
            <div class="score-value">{{ healthScore.score }}</div>
            <div class="score-max">/100</div>
          </div>
          <div class="score-level">
            <el-tag :type="healthScore.tagType" size="large" effect="dark">
              {{ healthScore.level_text }}
            </el-tag>
          </div>
        </div>
        <div class="score-right">
          <h3>情绪健康评分</h3>
          <div class="score-details">
            <div class="detail-item">
              <span class="label">积极情绪占比:</span>
              <el-progress :percentage="healthScore.positive_rate" color="#67c23a" :stroke-width="12" />
            </div>
            <div class="detail-item">
              <span class="label">消极情绪占比:</span>
              <el-progress :percentage="healthScore.negative_rate" color="#f56c6c" :stroke-width="12" />
            </div>
            <div class="detail-item">
              <span class="label">情绪波动指数:</span>
              <el-progress :percentage="healthScore.stability" :color="getStabilityColor(healthScore.stability)" :stroke-width="12" />
            </div>
          </div>
          <div class="score-advice">
            <el-icon><warning-filled /></el-icon>
            <span>{{ healthScore.advice }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <el-row :gutter="20" v-if="totalPredictions > 0">
      <!-- 情绪分布饼图 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>情绪分布</span>
              <el-tag>总计 {{ totalPredictions }} 次</el-tag>
            </div>
          </template>
          <div ref="emotionPieChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 情绪趋势折线图 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>情绪趋势</span>
              <el-select v-model="trendPeriod" size="small" @change="updateTrendChart">
                <el-option label="最近7天" value="7d" />
                <el-option label="最近30天" value="30d" />
                <el-option label="全部" value="all" />
              </el-select>
            </div>
          </template>
          <div ref="emotionTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 置信度分布 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>置信度分布</span>
            </div>
          </template>
          <div ref="confidenceChart" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 时段分析 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>时段分析</span>
            </div>
          </template>
          <div ref="timeAnalysisChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 情绪日历热力图 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>情绪日历</span>
          <el-tag>{{ currentYear }}年</el-tag>
        </div>
      </template>
      <div ref="emotionCalendarChart" class="calendar-chart-container"></div>
    </el-card>

    <!-- 周期对比分析 -->
    <el-card class="chart-card" shadow="hover" v-if="totalPredictions > 0">
      <template #header>
        <div class="card-header">
          <span>周期对比分析</span>
          <el-radio-group v-model="comparisonPeriod" size="small" @change="updateComparisonChart">
            <el-radio-button label="week">本周 vs 上周</el-radio-button>
            <el-radio-button label="month">本月 vs 上月</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="comparisonChart" class="chart-container"></div>
      <div class="comparison-summary">
        <el-alert :title="comparisonSummary.title" :type="comparisonSummary.type" :closable="false">
          <p>{{ comparisonSummary.description }}</p>
        </el-alert>
      </div>
    </el-card>




  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useEmotionStore } from '../stores/emotion'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataLine,
  Avatar,
  TrendCharts,
  Calendar,
  Document,
  WarningFilled,
  Delete
} from '@element-plus/icons-vue'
import echarts from '../utils/echarts'
import { registerFacelensChartThemes, currentChartTheme, chartToken } from '../utils/chartTheme'
import { useVideoStore } from '../stores/video'
import api from '../api/client'

const emotionStore = useEmotionStore()
const videoStore = useVideoStore()

// 导出相关
const isExporting = ref(false)

// 合并图片识别和视频分析的数据（服务端历史优先，本地数据补充）
const allPredictions = computed(() => {
  const records = []

  // 服务端历史记录（/api/histories，含图片与视频帧）
  ;(emotionStore.serverHistories || []).forEach(rec => {
    records.push({
      emotion: rec.emotion,
      emotion_cn: rec.emotion_cn,
      confidence: rec.confidence,
      timestamp: rec.created_at,
      model_used: rec.model_used,
      source: (rec.input_type || 'image') === 'video' ? 'video' : 'image',
      origin: 'server'
    })
  })

  const serverHistoryIds = new Set((emotionStore.serverHistories || []).map(r => r.id))

  // 本地图片预测：仅补充服务端没有的（离线/历史遗留）记录
  ;(emotionStore.predictions || []).forEach(pred => {
    // 仅当服务端已拉取到同 ID 记录时跳过；分页外的服务端记录由本地副本兜底展示
    if (pred.history_id && serverHistoryIds.has(pred.history_id)) return
    records.push({
      ...pred,
      source: 'image',
      origin: 'local'
    })
  })

  // 本地视频帧：服务端没有视频记录时兜底
  const serverHasVideo = (emotionStore.serverHistories || []).some(r => (r.input_type || 'image') === 'video')
  if (!serverHasVideo && videoStore.videoHistory && Array.isArray(videoStore.videoHistory)) {
    videoStore.videoHistory.forEach(video => {
      if (video.results && video.results.timeline && Array.isArray(video.results.timeline)) {
        video.results.timeline.forEach(frame => {
          records.push({
            emotion: frame.emotion,
            emotion_cn: frame.emotion_cn,
            confidence: frame.confidence,
            timestamp: video.timestamp, // frame.timestamp 是视频内秒数，不能当日期
            model_used: video.model || 'CNN',
            source: 'video',
            video_id: video.video_id,
            frame_number: frame.frame_number,
            origin: 'local'
          })
        })
      }
    })
  }

  return records
})

// 数据来源统计
const imageCount = computed(() => {
  return allPredictions.value.filter(p => p.source !== 'video').length
})

const videoCount = computed(() => {
  return allPredictions.value.filter(p => p.source === 'video').length
})

// 统计数据
const totalPredictions = computed(() => allPredictions.value.length)

const dominantEmotion = computed(() => {
  if (allPredictions.value.length === 0) return '-'
  
  const emotionCounts = {}
  allPredictions.value.forEach(pred => {
    emotionCounts[pred.emotion_cn] = (emotionCounts[pred.emotion_cn] || 0) + 1
  })
  
  let maxEmotion = ''
  let maxCount = 0
  for (const [emotion, count] of Object.entries(emotionCounts)) {
    if (count > maxCount) {
      maxCount = count
      maxEmotion = emotion
    }
  }
  
  return maxEmotion
})

const avgConfidence = computed(() => {
  if (allPredictions.value.length === 0) return 0
  
  const sum = allPredictions.value.reduce((acc, pred) => acc + pred.confidence, 0)
  return (sum / allPredictions.value.length * 100).toFixed(1)
})

const activeDays = computed(() => {
  if (allPredictions.value.length === 0) return 0
  
  const dates = new Set()
  allPredictions.value.forEach(pred => {
    const date = new Date(pred.timestamp).toDateString()
    dates.add(date)
  })
  
  return dates.size
})

// 服务端健康评估（/health/assessment，登录用户按日生成）
const serverAssessment = ref(null)

// 情绪健康评分：优先展示服务端评估结果，本地计算作为兜底
const healthScore = computed(() => {
  const local = computeLocalHealthScore()
  const srv = serverAssessment.value
  if (!srv || (srv.health_score == null && !srv.alert_title)) return local

  const tagType = srv.alert_type === 'error' ? 'danger' : (srv.alert_type || local.tagType)
  const suggestions = Array.isArray(srv.suggestions) ? srv.suggestions : []
  return {
    score: srv.health_score ?? local.score,
    level: local.level,
    level_text: srv.risk_level_cn || srv.alert_title || local.level_text,
    tagType,
    positive_rate: srv.positive_rate ?? local.positive_rate,
    negative_rate: srv.negative_rate ?? local.negative_rate,
    stability: local.stability,
    advice: srv.alert_description || local.advice,
    suggestions,
    fromServer: true
  }
})

function computeLocalHealthScore() {
  if (allPredictions.value.length === 0) {
    return {
      score: 0,
      level: 'normal',
      level_text: '暂无数据',
      tagType: 'info',
      positive_rate: 0,
      negative_rate: 0,
      stability: 0,
      advice: '请先进行情绪识别以获取健康评分'
    }
  }

  // 积极情绪：happy, normal
  // 消极情绪：anger, sad, fear, disgust
  // 中性情绪：surprised
  let positiveCount = 0
  let negativeCount = 0
  const emotionValues = []
  const emotionMap = { anger: 1, disgust: 2, fear: 3, sad: 4, normal: 5, surprised: 6, happy: 7 }

  allPredictions.value.forEach(pred => {
    if (pred.emotion === 'happy' || pred.emotion === 'normal') {
      positiveCount++
    } else if (['anger', 'sad', 'fear', 'disgust'].includes(pred.emotion)) {
      negativeCount++
    }
    emotionValues.push(emotionMap[pred.emotion] || 5)
  })

  const total = allPredictions.value.length
  const positiveRate = Math.round((positiveCount / total) * 100)
  const negativeRate = Math.round((negativeCount / total) * 100)

  // 计算情绪波动（使用标准差的倒数作为稳定性指标）
  const mean = emotionValues.reduce((a, b) => a + b, 0) / emotionValues.length
  const variance = emotionValues.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / emotionValues.length
  const stdDev = Math.sqrt(variance)
  const stability = Math.max(0, Math.min(100, 100 - stdDev * 20)) // 标准差越小越稳定

  // 计算总分（积极占比40%，消极占比的反向30%，稳定性30%）
  const score = Math.round(positiveRate * 0.4 + (100 - negativeRate) * 0.3 + stability * 0.3)

  let level, level_text, tagType, advice
  if (score >= 85) {
    level = 'excellent'
    level_text = '优秀'
    tagType = 'success'
    advice = '您的情绪状态非常健康！保持积极乐观的心态，继续加油！'
  } else if (score >= 70) {
    level = 'good'
    level_text = '良好'
    tagType = 'success'
    advice = '您的情绪状态良好，继续保持规律作息和适度运动。'
  } else if (score >= 55) {
    level = 'normal'
    level_text = '一般'
    tagType = 'warning'
    advice = '建议多参与社交活动，尝试放松技巧，如冥想、瑜伽等。'
  } else {
    level = 'need-attention'
    level_text = '需要关注'
    tagType = 'danger'
    advice = '您的情绪波动较大，建议咨询专业心理咨询师，及时调整心态。'
  }

  return {
    score,
    level,
    level_text,
    tagType,
    positive_rate: positiveRate,
    negative_rate: negativeRate,
    stability: Math.round(stability),
    advice
  }
}

function getStabilityColor(stability) {
  if (stability >= 70) return '#67c23a'
  if (stability >= 40) return '#e6a23c'
  return '#f56c6c'
}

// 周期对比分析
const comparisonPeriod = ref('week')
const comparisonSummary = ref({
  title: '对比分析',
  type: 'info',
  description: '暂无对比数据'
})

// 情绪映射
const emotionEmojiMap = {
  anger: '😠',
  disgust: '🤢',
  fear: '😨',
  happy: '😊',
  normal: '😐',
  sad: '😢',
  surprised: '😲'
}

const emotionCnMap = {
  anger: '生气',
  disgust: '厌恶',
  fear: '害怕',
  happy: '高兴',
  normal: '平静',
  sad: '悲伤',
  surprised: '惊讶'
}

function getEmotionEmoji(emotion) {
  return emotionEmojiMap[emotion] || '😐'
}

// ===== 视频分析相关 =====
const selectedVideoId = ref(null)
const videoEmotionChart = ref(null)

// 选中视频的详细数据分析
const selectedVideoData = computed(() => {
  if (!selectedVideoId.value) return null
  
  const video = videoStore.videoHistory.find(v => v.video_id === selectedVideoId.value)
  if (!video || !video.results || !video.results.timeline) return null
  
  const timeline = video.results.timeline
  
  // 检查 timeline 是否是数组
  if (!Array.isArray(timeline) || timeline.length === 0) {
    console.warn('⚠️ [Analysis] timeline 不是数组或为空:', timeline)
    return null
  }
  
  const totalFrames = timeline.length
  
  // 计算主要情绪
  const emotionCounts = {}
  timeline.forEach(frame => {
    emotionCounts[frame.emotion_cn] = (emotionCounts[frame.emotion_cn] || 0) + 1
  })
  
  let dominantEmotion = ''
  let maxCount = 0
  for (const [emotion, count] of Object.entries(emotionCounts)) {
    if (count > maxCount) {
      maxCount = count
      dominantEmotion = emotion
    }
  }
  
  // 计算平均置信度
  const avgConfidence = (timeline.reduce((sum, frame) => sum + frame.confidence, 0) / totalFrames * 100).toFixed(1)
  
  // 计算情绪稳定性（情绪变化次数越少越稳定）
  let emotionChanges = 0
  for (let i = 1; i < timeline.length; i++) {
    if (timeline[i].emotion !== timeline[i-1].emotion) {
      emotionChanges++
    }
  }
  const stabilityRate = Math.max(0, 100 - (emotionChanges / totalFrames * 100))
  let stability = stabilityRate >= 70 ? '稳定' : stabilityRate >= 40 ? '一般' : '波动较大'
  
  // 生成分析洞察
  let insightTitle = ''
  let insightType = 'info'
  let insightDescription = ''
  
  const dominantRate = (maxCount / totalFrames * 100).toFixed(1)
  
  if (stabilityRate >= 70) {
    insightTitle = '情绪状态稳定'
    insightType = 'success'
    insightDescription = `视频中 ${dominantRate}% 的时间保持${dominantEmotion}状态，情绪变化平稳，心理状态良好。`
  } else if (stabilityRate >= 40) {
    insightTitle = '情绪有所波动'
    insightType = 'warning'
    insightDescription = `视频中情绪出现 ${emotionChanges} 次变化，建议关注情绪管理，保持心态平和。`
  } else {
    insightTitle = '情绪波动明显'
    insightType = 'error'
    insightDescription = `视频中情绪频繁变化（${emotionChanges} 次），可能处于压力或焦虑状态，建议进行放松调节。`
  }
  
  return {
    video_id: video.video_id,
    total_frames: totalFrames,
    dominant_emotion: dominantEmotion,
    avg_confidence: avgConfidence,
    stability,
    stability_rate: stabilityRate.toFixed(1),
    emotion_changes: emotionChanges,
    timeline,
    insight_title: insightTitle,
    insight_type: insightType,
    insight_description: insightDescription
  }
})

// 监听视频选择变化，更新图表
watch(selectedVideoData, (newData) => {
  if (newData) {
    nextTick(() => {
      updateVideoEmotionChart()
    })
  }
})

// 初始化时选择第一个视频
onMounted(() => {
  if (videoStore.videoHistory.length > 0) {
    selectedVideoId.value = videoStore.videoHistory[0].video_id
  }
})

// 监听视频历史记录变化
watch(() => videoStore.videoHistory.length, (newLength, oldLength) => {
  // 如果视频被删除了
  if (newLength < oldLength) {
    // 如果当前选中的视频被删除，自动选择第一个视频
    if (selectedVideoId.value && !videoStore.videoHistory.find(v => v.video_id === selectedVideoId.value)) {
      selectedVideoId.value = videoStore.videoHistory.length > 0 ? videoStore.videoHistory[0].video_id : null
    }
  }
})

// 删除选中的视频
function deleteSelectedVideo() {
  if (!selectedVideoId.value) return
  
  const video = videoStore.videoHistory.find(v => v.video_id === selectedVideoId.value)
  if (!video) return
  
  deleteVideo(video)
}

// 删除视频（通用函数）：仅删除本地缓存记录（服务端视频文件由管理员统一管理）
function deleteVideo(video) {
  ElMessageBox.confirm(
    `确定要删除视频 "${video.video_id}" 的本地分析记录吗？（服务端识别数据不受影响）`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    }
  ).then(() => {
    // 删除视频
    videoStore.deleteHistoryItem(video.id)
    ElMessage.success('本地视频记录已删除')

    // 自动选择下一个视频
    if (videoStore.videoHistory.length > 0) {
      selectedVideoId.value = videoStore.videoHistory[0].video_id
    } else {
      selectedVideoId.value = null
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getEmotionTagType(emotion) {
  const typeMap = {
    happy: 'success',
    normal: 'info',
    sad: 'warning',
    anger: 'danger',
    fear: 'warning',
    disgust: 'danger',
    surprised: 'primary'
  }
  return typeMap[emotion] || 'info'
}

function getProgressColor(confidence) {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

function formatDateTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 图表
const emotionPieChart = ref(null)
const emotionTrendChart = ref(null)
const confidenceChart = ref(null)
const timeAnalysisChart = ref(null)
const emotionCalendarChart = ref(null)

// 图表实例注册表：复用实例，避免数据刷新时重复 echarts.init 产生孤儿实例
// （旧实现每次 initAllCharts 都新建实例 + 追加 resize 监听器，长时间使用持续泄漏）
const chartInstances = {}
let chartsResizeBound = false
function handleChartsResize() {
  Object.values(chartInstances).forEach((c) => {
    if (c && !c.isDisposed()) c.resize()
  })
}
function getChart(name, el) {
  if (!el) return null
  registerFacelensChartThemes()
  const theme = currentChartTheme()
  const existing = chartInstances[name]
  if (existing && !existing.isDisposed() && existing.getDom() === el) {
    if (existing.__facelensTheme === theme) {
      existing.clear() // 清空旧配置，随后的 setOption 以干净状态重建
      return existing
    }
    // 主题切换：以新主题重建实例
    existing.dispose()
  }
  if (existing && !existing.isDisposed()) existing.dispose()
  const chart = echarts.init(el, theme)
  chart.__facelensTheme = theme
  chartInstances[name] = chart
  if (!chartsResizeBound) {
    chartsResizeBound = true
    window.addEventListener('resize', handleChartsResize)
  }
  return chart
}
onUnmounted(() => {
  if (themeObserver) {
    themeObserver.disconnect()
    themeObserver = null
  }
  if (chartsResizeBound) {
    window.removeEventListener('resize', handleChartsResize)
    chartsResizeBound = false
  }
  Object.values(chartInstances).forEach((c) => {
    try { if (!c.isDisposed()) c.dispose() } catch (e) { /* 忽略 */ }
  })
})

const trendPeriod = ref('7d')
const currentYear = ref(new Date().getFullYear())

// 初始化饼图
function initPieChart() {
  if (!emotionPieChart.value) return
  
  const chart = getChart('pie', emotionPieChart.value)
  
  // 统计情绪分布
  const emotionCounts = {}
  allPredictions.value.forEach(pred => {
    const cn = pred.emotion_cn
    emotionCounts[cn] = (emotionCounts[cn] || 0) + 1
  })
  
  const data = Object.entries(emotionCounts).map(([name, value]) => ({
    name,
    value
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 次 ({d}%)'
    },
    legend: {
      bottom: 0,
      left: 'center'
    },
    series: [
      {
        name: '情绪分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: chartToken('--color-surface'),
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ],
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
  }
  
  chart.setOption(option)
  
  // 响应式
}

// 初始化趋势图
function initTrendChart() {
  updateTrendChart()
}

function updateTrendChart() {
  if (!emotionTrendChart.value) return
  
  const chart = getChart('trend', emotionTrendChart.value)
  
  // 获取时间范围
  let days = 7
  if (trendPeriod.value === '30d') days = 30
  else if (trendPeriod.value === 'all') days = 365
  
  // 按日期分组
  const dateMap = {}
  const now = new Date()
  
  allPredictions.value.forEach(pred => {
    const date = new Date(pred.timestamp)
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
    
    if (diffDays < days) {
      const dateStr = date.toLocaleDateString('zh-CN')
      if (!dateMap[dateStr]) {
        dateMap[dateStr] = {}
      }
      const emotion = pred.emotion_cn
      dateMap[dateStr][emotion] = (dateMap[dateStr][emotion] || 0) + 1
    }
  })
  
  // 准备数据
  const dates = Object.keys(dateMap).sort()
  const emotions = ['生气', '厌恶', '害怕', '高兴', '平静', '悲伤', '惊讶']
  const series = emotions.map(emotion => ({
    name: emotion,
    type: 'line',
    smooth: true,
    data: dates.map(date => dateMap[date][emotion] || 0)
  }))
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: emotions,
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: series
  }
  
  chart.setOption(option)
}

// 初始化置信度分布图
function initConfidenceChart() {
  if (!confidenceChart.value) return
  
  const chart = getChart('confidence', confidenceChart.value)
  
  // 按区间统计
  const ranges = [
    { name: '0-60%', min: 0, max: 0.6, count: 0 },
    { name: '60-70%', min: 0.6, max: 0.7, count: 0 },
    { name: '70-80%', min: 0.7, max: 0.8, count: 0 },
    { name: '80-90%', min: 0.8, max: 0.9, count: 0 },
    { name: '90-100%', min: 0.9, max: 1.0, count: 0 }
  ]
  
  allPredictions.value.forEach(pred => {
    const conf = pred.confidence
    for (const range of ranges) {
      if (conf >= range.min && conf <= range.max) {
        range.count++
        break
      }
    }
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ranges.map(r => r.name)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '次数',
        type: 'bar',
        data: ranges.map(r => r.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 初始化时段分析图
function initTimeAnalysisChart() {
  if (!timeAnalysisChart.value) return
  
  const chart = getChart('time', timeAnalysisChart.value)
  
  // 按小时统计
  const hourCounts = Array(24).fill(0)
  
  allPredictions.value.forEach(pred => {
    const hour = new Date(pred.timestamp).getHours()
    hourCounts[hour]++
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 24 }, (_, i) => `${i}:00`)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '识别次数',
        type: 'bar',
        data: hourCounts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#fbc2eb' },
            { offset: 1, color: '#a6c1ee' }
          ])
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 初始化日历热力图
function initCalendarChart() {
  if (!emotionCalendarChart.value) return
  
  const chart = getChart('calendar', emotionCalendarChart.value)
  
  // 准备日历数据
  const dateMap = {}
  allPredictions.value.forEach(pred => {
    const date = new Date(pred.timestamp)
    if (isNaN(date.getTime())) return // 非法时间戳跳过，避免 toISOString 抛错中断图表
    const dateStr = date.toISOString().split('T')[0]
    dateMap[dateStr] = (dateMap[dateStr] || 0) + 1
  })
  
  const data = Object.entries(dateMap).map(([date, count]) => [date, count])
  
  const option = {
    tooltip: {
      position: 'top',
      formatter: (params) => {
        return `${params.data[0]}<br/>识别次数: ${params.data[1]}`
      }
    },
    visualMap: {
      min: 0,
      max: Math.max(1, ...Object.values(dateMap)),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      top: 0,
      inRange: {
        color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
      }
    },
    calendar: {
      top: 80,
      left: 50,
      right: 50,
      cellSize: ['auto', 15],
      range: currentYear.value,
      itemStyle: {
        borderWidth: 0.5
      },
      yearLabel: { show: false }
    },
    series: [
      {
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: data
      }
    ]
  }
  
  chart.setOption(option)
}



// 初始化对比图表
const comparisonChart = ref(null)

function initComparisonChart() {
  updateComparisonChart()
}

function updateComparisonChart() {
  if (!comparisonChart.value) return
  
  const chart = getChart('comparison', comparisonChart.value)
  const now = new Date()
  let currentData = {}
  let previousData = {}
  let currentLabel = ''
  let previousLabel = ''
  
  if (comparisonPeriod.value === 'week') {
    // 本周 vs 上周
    currentLabel = '本周'
    previousLabel = '上周'
    
    allPredictions.value.forEach(pred => {
      const date = new Date(pred.timestamp)
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      const emotion = pred.emotion_cn
      
      if (diffDays < 7) {
        currentData[emotion] = (currentData[emotion] || 0) + 1
      } else if (diffDays >= 7 && diffDays < 14) {
        previousData[emotion] = (previousData[emotion] || 0) + 1
      }
    })
  } else {
    // 本月 vs 上月
    currentLabel = '本月'
    previousLabel = '上月'
    const currentMonth = now.getMonth()
    const currentYear = now.getFullYear()
    
    allPredictions.value.forEach(pred => {
      const date = new Date(pred.timestamp)
      const emotion = pred.emotion_cn
      
      if (date.getFullYear() === currentYear && date.getMonth() === currentMonth) {
        currentData[emotion] = (currentData[emotion] || 0) + 1
      } else if (date.getFullYear() === currentYear && date.getMonth() === currentMonth - 1) {
        previousData[emotion] = (previousData[emotion] || 0) + 1
      } else if (currentMonth === 0 && date.getFullYear() === currentYear - 1 && date.getMonth() === 11) {
        previousData[emotion] = (previousData[emotion] || 0) + 1
      }
    })
  }
  
  const emotions = ['生气', '厌恶', '害怕', '高兴', '平静', '悲伤', '惊讶']
  const currentValues = emotions.map(e => currentData[e] || 0)
  const previousValues = emotions.map(e => previousData[e] || 0)
  
  // 计算总数和变化
  const currentTotal = currentValues.reduce((a, b) => a + b, 0)
  const previousTotal = previousValues.reduce((a, b) => a + b, 0)
  const currentPositive = (currentData['高兴'] || 0) + (currentData['平静'] || 0)
  const previousPositive = (previousData['高兴'] || 0) + (previousData['平静'] || 0)
  
  // 更新对比总结
  if (currentTotal > 0 && previousTotal > 0) {
    const change = ((currentTotal - previousTotal) / previousTotal * 100).toFixed(1)
    const positiveChange = currentPositive - previousPositive
    
    if (positiveChange > 0) {
      comparisonSummary.value = {
        title: '积极变化 📈',
        type: 'success',
        description: `${currentLabel}相比${previousLabel}，识别次数${change > 0 ? '增加' : '减少'}了${Math.abs(change)}%，积极情绪增加了${positiveChange}次。继续保持！`
      }
    } else if (positiveChange < 0) {
      comparisonSummary.value = {
        title: '需要关注 ⚠️',
        type: 'warning',
        description: `${currentLabel}相比${previousLabel}，积极情绪减少了${Math.abs(positiveChange)}次。建议多参与放松活动，调整心态。`
      }
    } else {
      comparisonSummary.value = {
        title: '保持稳定 ✨',
        type: 'info',
        description: `${currentLabel}相比${previousLabel}，情绪状态保持稳定。`
      }
    }
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: [currentLabel, previousLabel],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: emotions
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: previousLabel,
        type: 'bar',
        data: previousValues,
        itemStyle: {
          color: '#91cc75',
          opacity: 0.6
        }
      },
      {
        name: currentLabel,
        type: 'bar',
        data: currentValues,
        itemStyle: {
          color: '#5470c6'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 视频情绪变化图表
function updateVideoEmotionChart() {
  if (!videoEmotionChart.value || !selectedVideoData.value) return
  
  const chart = getChart('videoEmotion', videoEmotionChart.value)
  const timeline = selectedVideoData.value.timeline
  
  // 准备数据
  const frameNumbers = timeline.map((_, index) => `帧${index + 1}`)
  const emotionValues = timeline.map(frame => {
    const emotionMap = { anger: 1, disgust: 2, fear: 3, sad: 4, normal: 5, surprised: 6, happy: 7 }
    return emotionMap[frame.emotion] || 5
  })
  const confidenceValues = timeline.map(frame => (frame.confidence * 100).toFixed(1))
  
  // 情绪标签映射
  const emotionLabels = ['', '愤怒', '厌恶', '恐惧', '悲伤', '平静', '惊讶', '开心']
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const frameIndex = params[0].dataIndex
        const frame = timeline[frameIndex]
        return `帧 ${frameIndex + 1}<br/>
                情绪: ${frame.emotion_cn}<br/>
                置信度: ${(frame.confidence * 100).toFixed(1)}%`
      }
    },
    legend: {
      data: ['情绪变化', '置信度'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: frameNumbers,
      axisLabel: {
        interval: Math.floor(timeline.length / 10) || 0,
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '情绪',
        min: 0,
        max: 8,
        interval: 1,
        axisLabel: {
          formatter: (value) => emotionLabels[value] || ''
        }
      },
      {
        type: 'value',
        name: '置信度(%)',
        min: 0,
        max: 100,
        position: 'right'
      }
    ],
    dataZoom: [
      {
        type: 'slider',
        show: timeline.length > 20,
        start: 0,
        end: Math.min(100, (20 / timeline.length) * 100),
        height: 20,
        bottom: 40
      },
      {
        type: 'inside',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '情绪变化',
        type: 'line',
        data: emotionValues,
        smooth: true,
        yAxisIndex: 0,
        itemStyle: {
          color: chartToken('--color-accent')
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
            ]
          }
        }
      },
      {
        name: '置信度',
        type: 'line',
        data: confidenceValues,
        smooth: true,
        yAxisIndex: 1,
        itemStyle: {
          color: '#43e97b'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 导出PDF报告 - 完全基于html2canvas渲染解决中文乱码问题
async function exportPDFReport() {
  try {
    isExporting.value = true
    ElMessage.info('正在生成报告，请稍候...')
    
    // 动态导入库
    const html2canvas = (await import('html2canvas')).default
    const { jsPDF } = await import('jspdf')
    
    // 创建PDF实例
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    
    // 创建一个临时DOM元素来渲染所有需要导出的内容
    // 这样可以确保所有中文都能正确显示，而不是直接使用pdf.text()
    const tempContainer = document.createElement('div')
    tempContainer.style.position = 'fixed'
    tempContainer.style.top = '0'
    tempContainer.style.left = '-9999px' // 移出可视区域
    tempContainer.style.width = '794px' // A4宽度 (72dpi)
    tempContainer.style.backgroundColor = 'white'
    tempContainer.style.padding = '20px'
    tempContainer.style.fontFamily = 'Arial, "Microsoft YaHei", sans-serif'
    document.body.appendChild(tempContainer)
    
    // 添加标题
    const title = document.createElement('h1')
    title.style.textAlign = 'center'
    title.style.fontSize = '24px'
    title.style.marginBottom = '10px'
    title.textContent = '情绪识别分析报告'
    tempContainer.appendChild(title)
    
    // 添加生成日期
    const date = document.createElement('p')
    date.style.textAlign = 'center'
    date.style.fontSize = '14px'
    date.style.marginBottom = '20px'
    const formattedDate = `${new Date().toLocaleDateString('zh-CN')} ${new Date().toLocaleTimeString('zh-CN')}`
    date.textContent = `生成日期: ${formattedDate}`
    tempContainer.appendChild(date)
    
    // 添加数据统计部分
    const statsSection = document.createElement('div')
    statsSection.style.marginBottom = '20px'
    
    const statsTitle = document.createElement('h2')
    statsTitle.style.fontSize = '18px'
    statsTitle.style.marginBottom = '10px'
    statsTitle.textContent = '📊 数据统计'
    statsSection.appendChild(statsTitle)
    
    const statsList = document.createElement('ul')
    statsList.style.listStyleType = 'none'
    statsList.style.paddingLeft = '20px'
    
    const statsItems = [
      `总识别次数: ${totalPredictions.value}`,
      `主导情绪: ${dominantEmotion.value}`,
      `平均置信度: ${avgConfidence.value}%`,
      `活跃天数: ${activeDays.value}`
    ]
    
    statsItems.forEach(item => {
      const li = document.createElement('li')
      li.style.fontSize = '14px'
      li.style.marginBottom = '8px'
      li.textContent = item
      statsList.appendChild(li)
    })
    
    statsSection.appendChild(statsList)
    tempContainer.appendChild(statsSection)
    
    // 添加健康评分部分
    const healthSection = document.createElement('div')
    healthSection.style.marginBottom = '20px'
    
    const healthTitle = document.createElement('h2')
    healthTitle.style.fontSize = '18px'
    healthTitle.style.marginBottom = '10px'
    healthTitle.textContent = '💚 情绪健康评分'
    healthSection.appendChild(healthTitle)
    
    const healthList = document.createElement('ul')
    healthList.style.listStyleType = 'none'
    healthList.style.paddingLeft = '20px'
    
    const healthItems = [
      `评分: ${healthScore.value.score}/100 (${healthScore.value.level_text})`,
      `积极情绪占比: ${healthScore.value.positive_rate}%`,
      `消极情绪占比: ${healthScore.value.negative_rate}%`,
      `情绪稳定性: ${healthScore.value.stability}%`
    ]
    
    healthItems.forEach(item => {
      const li = document.createElement('li')
      li.style.fontSize = '14px'
      li.style.marginBottom = '8px'
      li.textContent = item
      healthList.appendChild(li)
    })
    
    healthSection.appendChild(healthList)
    
    // 添加建议
    const adviceTitle = document.createElement('h3')
    adviceTitle.style.fontSize = '16px'
    adviceTitle.style.marginTop = '15px'
    adviceTitle.style.marginBottom = '10px'
    adviceTitle.textContent = '健康建议:'
    healthSection.appendChild(adviceTitle)
    
    const advicePara = document.createElement('p')
    advicePara.style.fontSize = '14px'
    advicePara.style.lineHeight = '1.6'
    advicePara.style.paddingLeft = '20px'
    advicePara.textContent = healthScore.value.advice
    healthSection.appendChild(advicePara)
    
    tempContainer.appendChild(healthSection)
    
    // 等待DOM渲染完成
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // 使用html2canvas渲染整个内容
    const canvas = await html2canvas(tempContainer, {
      scale: 2, // 提高清晰度
      backgroundColor: '#ffffff',
      useCORS: true,
      logging: false,
      letterRendering: true, // 确保字体平滑渲染
      timeout: 30000,
      allowTaint: true // 允许加载跨域图像
    })
    
    // 移除临时容器
    document.body.removeChild(tempContainer)
    
    // 计算图像在PDF中的尺寸
    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    const imgWidth = pageWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    
    // 如果内容超过一页，需要分割
    let heightLeft = imgHeight
    let position = 0
    let pageNum = 1
    const totalPages = Math.ceil(imgHeight / pageHeight)
    
    // 添加第一页
    pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
    
    // 添加剩余页面（如果需要）
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
      pageNum++
    }
    
    // 添加页码
    for (let i = 1; i <= totalPages; i++) {
      pdf.setPage(i)
      pdf.setFontSize(10)
      // 使用英文页码避免乱码问题
      pdf.text(
        `Page ${i} / Total ${totalPages}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      )
    }
    
    // 保存PDF - 使用英文文件名避免编码问题
    const fileName = `emotion_analysis_report_${new Date().toISOString().split('T')[0]}.pdf`
    pdf.save(fileName)
    ElMessage.success('报告导出成功！')
    
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('报告导出失败: ' + error.message)
  } finally {
    isExporting.value = false
  }
}

// 初始化所有图表
function initAllCharts() {
  nextTick(() => {
    initPieChart()
    initTrendChart()
    initConfidenceChart()
    initTimeAnalysisChart()
    initCalendarChart()
    initComparisonChart()
  })
}

// 数据到达后刷新所有图表（服务端历史为异步加载）
watch(() => allPredictions.value.length, () => {
  initAllCharts()
})

let themeObserver = null

onMounted(async () => {
  // html.dark class 变化即视为主题切换，重建图表以应用新主题
  themeObserver = new MutationObserver(() => initAllCharts())
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })

  initAllCharts()

  // 拉取服务端历史与健康评估（失败时静默降级为本地数据）
  try {
    await emotionStore.fetchServerHistories(100, 5)
  } catch (error) {
    console.warn('服务端历史拉取失败，使用本地数据', error)
  }
  try {
    const response = await api.get('/health/assessment')
    const data = response.data?.data
    serverAssessment.value = Array.isArray(data) ? data[data.length - 1] : data || null
  } catch (error) {
    console.warn('健康评估获取失败，使用本地计算', error)
  }
})
</script>

<style scoped>
.analysis-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
  padding: 2rem;
  background: var(--color-surface);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .page-header h1 {
    text-align: center;
  }
  
  .page-header p {
    text-align: center;
  }
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--color-ink);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--color-mahogany);
  font-size: 1.1rem;
}

.stats-cards {
  margin-bottom: 2rem;
}

.stat-card {
  margin-bottom: 1rem;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--color-ink);
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-ink);
  margin-bottom: 0.25rem;
}

.stat-label {
  color: var(--color-mahogany);
  font-size: 0.9rem;
}

/* 数据来源统计卡片 */
.data-source-card {
  margin-bottom: 2rem;
}

.source-stat {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.source-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.source-info {
  flex: 1;
}

.source-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--color-ink);
  margin-bottom: 0.25rem;
}

.source-label {
  color: var(--color-mahogany);
  font-size: 0.9rem;
}

.chart-card {
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  font-size: 1.1rem;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.calendar-chart-container {
  width: 100%;
  height: 250px;
}

/* 视频分析卡片 */
.video-analysis-card {
  margin-bottom: 2rem;
}

.video-summary {
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 12px;
}

.summary-item {
  text-align: center;
  padding: 15px;
}

.summary-label {
  font-size: 14px;
  color: var(--color-mahogany);
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--color-ink);
}

.video-insights {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .stat-content {
    gap: 1rem;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .chart-container {
    height: 300px;
  }
}

/* 情绪健康评分卡片样式 */
.health-score-card {
  margin-bottom: 2rem;
}

.health-score-content {
  display: flex;
  align-items: center;
  gap: 3rem;
  padding: 1rem;
}

.score-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.score-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.score-circle.excellent {
  background: var(--color-accent);
}

.score-circle.good {
  background: var(--color-accent);
}

.score-circle.normal {
  background: var(--color-accent);
}

.score-circle.need-attention {
  background: var(--color-accent);
}

.score-value {
  font-size: 3rem;
  font-weight: bold;
  color: white;
  line-height: 1;
}

.score-max {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 0.25rem;
}

.score-level {
  margin-top: 0.5rem;
}

.score-right {
  flex: 1;
}

.score-right h3 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--color-ink);
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.detail-item .label {
  width: 120px;
  font-weight: 500;
  color: var(--color-mahogany);
}

.score-advice {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 1rem;
  background: #f0f9ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  color: var(--color-mahogany);
  line-height: 1.6;
}

.score-advice .el-icon {
  color: #409eff;
  margin-top: 2px;
}

/* 对比分析样式 */
.comparison-summary {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .health-score-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .score-circle {
    width: 120px;
    height: 120px;
  }
  
  .score-value {
    font-size: 2.5rem;
  }
  
  .score-right h3 {
    font-size: 1.2rem;
    text-align: center;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-item .label {
    width: 100%;
  }
}

/* 视频快速选择列表样式 */
.video-quick-list {
  margin-bottom: 20px;
  border-radius: 8px;
  background: var(--el-color-primary-light-9);
  padding: 10px;
}

.video-list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.video-item {
  background: var(--color-surface);
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.video-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.video-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.video-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.video-item-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.video-item-info {
  flex: 1;
  min-width: 0;
}

.video-item-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-ink);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-item-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.video-item-time {
  font-size: 12px;
  color: var(--color-mahogany);
}
</style>
