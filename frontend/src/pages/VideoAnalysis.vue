<template>
  <div class="video-analysis-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>视频情绪分析</h1>
      <p>上传视频，智能识别视频中的人脸情绪变化</p>
    </div>

    <!-- 步骤指示器 -->
    <el-card class="steps-card" shadow="hover">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="上传视频" icon="Upload" />
        <el-step title="配置参数" icon="Setting" />
        <el-step title="分析中" icon="Loading" />
        <el-step title="查看结果" icon="View" />
      </el-steps>
    </el-card>

    <!-- 步骤1: 上传视频 -->
    <el-card v-if="currentStep === 0" class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>上传视频文件</span>
        </div>
      </template>

      <el-upload
        ref="uploadRef"
        class="video-upload"
        drag
        :auto-upload="false"
        :show-file-list="false"
        accept="video/*"
        :on-change="handleVideoSelect"
        :disabled="videoStore.isUploading"
      >
        <div v-if="!selectedFile" class="upload-placeholder">
          <el-icon class="upload-icon" :size="80"><video-camera /></el-icon>
          <div class="upload-text">拖拽视频到这里或点击上传</div>
          <div class="upload-hint">支持 MP4, AVI, MOV, MKV 等常见格式</div>
          <div class="upload-hint">建议视频时长不超过5分钟</div>
        </div>
        <div v-else class="video-preview">
          <video v-if="videoPreviewUrl" :src="videoPreviewUrl" controls class="preview-video"></video>
          <div class="video-info">
            <p><strong>文件名:</strong> {{ selectedFile.name }}</p>
            <p><strong>大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
          </div>
        </div>
      </el-upload>

      <div v-if="videoStore.isUploading" class="upload-progress">
        <el-progress :percentage="videoStore.uploadProgress" :status="videoStore.uploadProgress === 100 ? 'success' : ''" />
        <p>正在上传视频...</p>
      </div>

      <div class="action-buttons">
        <el-button
          v-if="!selectedFile"
          type="primary"
          size="large"
          @click="triggerUpload"
        >
          选择视频
        </el-button>
        <template v-else>
          <el-button
            type="primary"
            size="large"
            :loading="videoStore.isUploading"
            @click="uploadVideo"
          >
            <el-icon><upload-filled /></el-icon>
            确认上传
          </el-button>
          <el-button
            size="large"
            @click="clearSelection"
            :disabled="videoStore.isUploading"
          >
            重新选择
          </el-button>
        </template>
      </div>
    </el-card>

    <!-- 步骤2: 配置参数 -->
    <el-card v-if="currentStep === 1" class="config-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>分析参数配置</span>
        </div>
      </template>

      <!-- 视频信息展示 -->
      <div v-if="videoStore.currentVideo" class="video-info-display">
        <el-descriptions title="视频信息" :column="2" border>
          <el-descriptions-item label="分辨率">
            {{ videoStore.currentVideo.video_info.width }} × {{ videoStore.currentVideo.video_info.height }}
          </el-descriptions-item>
          <el-descriptions-item label="时长">
            {{ videoStore.currentVideo.video_info.duration_formatted }}
          </el-descriptions-item>
          <el-descriptions-item label="帧率">
            {{ videoStore.currentVideo.video_info.fps.toFixed(2) }} FPS
          </el-descriptions-item>
          <el-descriptions-item label="总帧数">
            {{ videoStore.currentVideo.video_info.total_frames }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="videoStore.currentVideo.thumbnail" class="video-thumbnail">
          <p style="margin-top: 20px; margin-bottom: 10px;"><strong>视频缩略图:</strong></p>
          <img :src="videoStore.currentVideo.thumbnail" alt="缩略图" style="max-width: 320px; border-radius: 8px;" />
        </div>
      </div>

      <el-divider />

      <!-- 参数配置表单 -->
      <el-form :model="analysisConfig" label-width="140px" class="config-form">
        <el-form-item label="识别模型" class="form-item-spacing">
          <el-radio-group v-model="analysisConfig.model" class="model-radio-group">
            <el-radio v-for="opt in modelRadioOptions" :key="opt.value" :label="opt.value" border>
              {{ opt.label }}{{ opt.recommended ? ' · 推荐' : '' }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="提取间隔" class="form-item-spacing">
          <div class="slider-container">
            <el-slider
              v-model="analysisConfig.interval"
              :min="1"
              :max="30"
              :step="1"
              :marks="{ 1: '1秒', 5: '5秒', 10: '10秒', 30: '30秒' }"
              show-input
              :show-input-controls="false"
              class="interval-slider"
            />
            <div class="hint-box">
              <p class="config-hint">每隔 <strong>{{ analysisConfig.interval }}</strong> 秒提取一帧进行分析</p>
              <p class="config-hint">预计提取约 <strong>{{ estimatedFrames }}</strong> 帧 (最多 {{ analysisConfig.maxFrames }} 帧)</p>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="最大帧数" class="form-item-spacing">
          <div class="input-container">
            <el-input-number
              v-model="analysisConfig.maxFrames"
              :min="10"
              :max="200"
              :step="10"
              class="max-frames-input"
            />
            <div class="hint-box">
              <p class="config-hint">限制提取的最大帧数，避免处理时间过长</p>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="人脸检测" class="form-item-spacing">
          <div class="switch-container">
            <el-switch
              v-model="analysisConfig.detectFace"
              active-text="启用"
              inactive-text="禁用"
              size="large"
            />
            <div class="hint-box">
              <p class="config-hint">自动检测并裁剪人脸区域，提高识别准确度</p>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <div class="action-buttons">
        <el-button size="large" @click="currentStep = 0">
          <el-icon><back /></el-icon>
          上一步
        </el-button>
        <el-button
          type="primary"
          size="large"
          @click="startAnalysis"
          :loading="videoStore.isAnalyzing"
        >
          <el-icon><video-play /></el-icon>
          开始分析
        </el-button>
      </div>
    </el-card>

    <!-- 步骤3: 分析中 -->
    <el-card v-if="currentStep === 2" class="analyzing-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>正在分析视频...</span>
        </div>
      </template>

      <div class="analyzing-content">
        <el-icon class="analyzing-icon" :size="100"><loading /></el-icon>
        <h3>AI正在努力分析视频中的情绪...</h3>
        <p>这可能需要几分钟时间，请耐心等待</p>

        <div class="progress-info">
          <el-progress
            :percentage="videoStore.analysisProgress"
            :status="videoStore.analysisProgress === 100 ? 'success' : ''"
            :stroke-width="20"
          />
          <p style="margin-top: 20px;">
            {{ analysisStatusText }}
          </p>
        </div>
      </div>
    </el-card>

    <!-- 步骤4: 查看结果 -->
    <div v-if="currentStep === 3 && videoStore.hasResults" ref="resultsRef">
      <!-- 分析概览 -->
      <el-row :gutter="20" class="stats-cards">
        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
                <el-icon><film /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ videoStore.totalFrames }}</div>
                <div class="stat-label">分析帧数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
                <el-icon><avatar /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ videoStore.statistics?.dominant_emotion || '-' }}</div>
                <div class="stat-label">主导情绪</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" style="background: var(--el-color-primary-light-9)">
                <el-icon><trend-charts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">
                  {{ ((videoStore.statistics?.average_confidence ?? 0) * 100).toFixed(1) }}%
                </div>
                <div class="stat-label">平均置信度</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
                <el-icon><connection /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ videoStore.emotionTransitions?.length || 0 }}</div>
                <div class="stat-label">情绪转换次数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 情绪时间轴 -->
      <el-card class="timeline-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>情绪变化时间轴</span>
          </div>
        </template>

        <div class="emotion-flow">
          <h3>情绪流向:</h3>
          <p class="flow-text">{{ videoStore.emotionFlow || '-' }}</p>
        </div>

        <el-divider />

        <!-- 情绪转换列表 -->
        <div v-if="videoStore.emotionTransitions?.length > 0" class="transitions-list">
          <h4>情绪转换记录:</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(transition, index) in videoStore.emotionTransitions"
              :key="index"
              :timestamp="transition.time_formatted"
              placement="top"
            >
              <span class="transition-text">
                {{ transition.from }} <el-icon><right /></el-icon> {{ transition.to }}
              </span>
            </el-timeline-item>
          </el-timeline>
        </div>
        <div v-else>
          <el-empty description="视频中情绪保持稳定，未发生明显转换" :image-size="60" />
        </div>
      </el-card>

      <!-- 帧浏览器 -->
      <el-card class="frames-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>帧浏览器 ({{ currentFrameIndex + 1 }} / {{ videoStore.totalFrames }})</span>
            <div>
              <el-button-group>
                <el-button
                  :disabled="currentFrameIndex === 0"
                  @click="previousFrame"
                >
                  <el-icon><arrow-left /></el-icon>
                  上一帧
                </el-button>
                <el-button
                  type="primary"
                  :disabled="currentFrameIndex === videoStore.totalFrames - 1"
                  @click="nextFrame"
                >
                  下一帧
                  <el-icon><arrow-right /></el-icon>
                </el-button>
              </el-button-group>
            </div>
          </div>
        </template>

        <div v-if="currentFrame" class="frame-detail">
          <el-row :gutter="20">
            <!-- 左侧: 图像展示 -->
            <el-col :xs="24" :sm="24" :md="12">
              <div class="frame-images">
                <div class="image-container">
                  <h4>原始帧</h4>
                  <img :src="currentFrame.original_frame" alt="原始帧" class="frame-image" />
                </div>
                <div class="image-container">
                  <h4>检测到的人脸</h4>
                  <img :src="currentFrame.face_image" alt="人脸" class="frame-image" />
                </div>
              </div>
            </el-col>

            <!-- 右侧: 分析结果 -->
            <el-col :xs="24" :sm="24" :md="12">
              <div class="frame-analysis">
                <h3>时间点: {{ currentFrame.time_formatted }}</h3>
                
                <el-divider />

                <div class="emotion-result">
                  <div class="emotion-display-large">
                    <span class="emotion-emoji">{{ getEmotionEmoji(currentFrame.emotion) }}</span>
                    <div>
                      <h2>{{ currentFrame.emotion_cn }}</h2>
                      <el-tag :type="getEmotionTagType(currentFrame.emotion)" size="large">
                        置信度: {{ (currentFrame.confidence * 100).toFixed(2) }}%
                      </el-tag>
                    </div>
                  </div>
                </div>

                <el-divider />

                <h4>情绪概率分布:</h4>
                <div class="probabilities-list">
                  <div
                    v-for="(prob, emotion) in currentFrame.probabilities_cn"
                    :key="emotion"
                    class="probability-item"
                  >
                    <span class="prob-label">{{ emotion }}</span>
                    <el-progress
                      :percentage="Math.round(prob * 100)"
                      :color="getEmotionColor(emotion)"
                    />
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>

          <!-- 导航滑块 -->
          <el-divider />
          <div class="frame-slider">
            <el-slider
              v-model="currentFrameIndex"
              :min="0"
              :max="videoStore.totalFrames - 1"
              :show-tooltip="false"
              @change="onFrameSliderChange"
            />
            <p style="text-align: center; margin-top: 10px;">
              拖动滑块快速浏览不同时间点的分析结果
            </p>
          </div>
        </div>
      </el-card>

      <!-- 情绪分布统计 -->
      <el-card class="distribution-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>情绪分布统计</span>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col
            v-for="(percentage, emotion) in videoStore.statistics?.emotion_percentages"
            :key="emotion"
            :xs="12"
            :sm="8"
            :md="6"
          >
            <div class="emotion-stat-item">
              <div class="emotion-stat-header">
                <span class="emotion-emoji">{{ getEmotionEmoji(emotion, true) }}</span>
                <span class="emotion-name">{{ emotion }}</span>
              </div>
              <el-progress
                type="circle"
                :percentage="Math.round(percentage)"
                :color="getEmotionColor(emotion)"
              />
              <p class="stat-count">
                {{ videoStore.statistics.emotion_distribution[emotion] }} 帧
              </p>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 操作按钮 -->
      <div class="final-actions">
        <el-button size="large" @click="resetAnalysis">
          <el-icon><refresh /></el-icon>
          重新分析
        </el-button>
        <el-button type="primary" size="large" :loading="isExporting" @click="downloadReport">
          <el-icon><download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  UploadFilled,
  VideoCamera,
  Upload,
  Setting,
  Loading,
  View,
  Back,
  VideoPlay,
  Film,
  Avatar,
  TrendCharts,
  Connection,
  Right,
  ArrowLeft,
  ArrowRight,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { useVideoStore } from '@/stores/video'
import api from '@/api/client'  // 🔑 导入封装好的 api，会自动附加 token

// Store
const videoStore = useVideoStore()

// 状态
const currentStep = ref(0)
const selectedFile = ref(null)
const videoPreviewUrl = ref(null)
const uploadRef = ref(null)
const currentFrameIndex = ref(0)

// 分析配置
const analysisConfig = ref({
  model: 'cnn',
  interval: 5,
  maxFrames: 100,
  detectFace: true
})

// 模型单选项：准确率从后端实时获取
const modelRadioOptions = ref([
  { value: 'cnn', label: 'CNN (83.77%)', recommended: true },
  { value: 'vgg', label: 'VGG16 (80%)', recommended: false },
  { value: 'se83', label: 'SE-Net (83%)', recommended: true }
])

async function loadModelOptions() {
  try {
    const response = await api.get('/models')
    const models = response.data.models || []
    if (models.length) {
      modelRadioOptions.value = models
        .filter((m) => ['cnn', 'vgg', 'se83'].includes(m.name))
        .map((m) => {
          const acc = typeof m.accuracy === 'number' && m.accuracy <= 1
            ? (m.accuracy * 100).toFixed(2)
            : m.accuracy
          return {
            value: m.name,
            label: `${m.display_name || m.name.toUpperCase()} (${acc}%)`,
            recommended: m.name === 'cnn' || m.name === 'se83'
          }
        })
    }
  } catch (error) {
    // 后端不可用时保留静态兜底
  }
}

// 计算属性
const estimatedFrames = computed(() => {
  if (!videoStore.currentVideo) return 0
  const duration = videoStore.currentVideo.video_info.duration
  const frames = Math.ceil(duration / analysisConfig.value.interval)
  return Math.min(frames, analysisConfig.value.maxFrames)
})

const analysisStatusText = computed(() => {
  const frames = estimatedFrames.value || analysisConfig.value.maxFrames
  return `服务器正在逐帧分析（约 ${frames} 帧）· 已耗时 ${analysisElapsed.value} 秒，请耐心等待`
})

const currentFrame = computed(() => {
  if (!videoStore.analysisResults?.frames) return null
  return videoStore.analysisResults.frames[currentFrameIndex.value]
})

// 方法
function triggerUpload() {
  uploadRef.value.$el.querySelector('input').click()
}

// 与后端 ALLOWED_VIDEO_EXTENSIONS / MAX_VIDEO_BYTES 一致
const ALLOWED_VIDEO_EXTS = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']
const MAX_VIDEO_BYTES = 200 * 1024 * 1024

function handleVideoSelect(file) {
  const raw = file.raw
  const ext = raw.name.split('.').pop().toLowerCase()
  if (!ALLOWED_VIDEO_EXTS.includes(ext)) {
    ElMessage.error('不支持的视频格式，支持：' + ALLOWED_VIDEO_EXTS.join(' / '))
    clearSelection()
    return
  }
  if (raw.size > MAX_VIDEO_BYTES) {
    ElMessage.error('视频过大（最大 200MB）')
    clearSelection()
    return
  }
  selectedFile.value = raw

  // 创建本地预览URL
  if (videoPreviewUrl.value) {
    URL.revokeObjectURL(videoPreviewUrl.value)
  }
  videoPreviewUrl.value = URL.createObjectURL(raw)

  ElMessage.success('视频选择成功')
}

function clearSelection() {
  selectedFile.value = null
  if (videoPreviewUrl.value) {
    URL.revokeObjectURL(videoPreviewUrl.value)
    videoPreviewUrl.value = null
  }
}

async function uploadVideo() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择视频文件')
    return
  }

  try {
    videoStore.startUpload()

    const formData = new FormData()
    formData.append('video', selectedFile.value)

    // 真实上传进度（axios onUploadProgress）
    const response = await api.post('/video/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000,  // 5分钟超时，适用于大视频文件上传
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          videoStore.setUploadProgress(Math.min(percent, 100))
        }
      }
    })

    videoStore.finishUpload()

    if (response.data.success) {
      videoStore.setCurrentVideo(response.data)
      currentStep.value = 1
      ElNotification({
        title: '上传成功',
        message: '视频上传成功，请配置分析参数',
        type: 'success'
      })
    }
  } catch (error) {
    videoStore.finishUpload()
    console.error('视频上传失败:', error)
    ElMessage.error(error.response?.data?.error || '视频上传失败')
  }
}

// 分析耗时计时器（用于展示诚实的进度信息）
let analysisTimer = null
let analysisStartTime = 0
const analysisElapsed = ref(0)

// 离开页面时必须清理定时器，否则分析进行中跳路由后定时器会永久运行
onUnmounted(() => {
  if (analysisTimer) {
    clearInterval(analysisTimer)
    analysisTimer = null
  }
})

async function startAnalysis() {
  if (!videoStore.currentVideo) {
    ElMessage.warning('请先上传视频')
    return
  }

  try {
    currentStep.value = 2
    videoStore.startAnalysis()

    // 后端暂无进度接口：进度条按耗时渐进逼近 90%（完成时立即到 100%），
    // 同时展示已耗时与预计帧数，如实反映分析状态
    analysisStartTime = Date.now()
    analysisElapsed.value = 0
    clearInterval(analysisTimer)
    analysisTimer = setInterval(() => {
      analysisElapsed.value = Math.floor((Date.now() - analysisStartTime) / 1000)
      const asymptotic = 90 * (1 - Math.exp(-analysisElapsed.value / 45))
      videoStore.setAnalysisProgress(Math.min(90, Math.round(asymptotic)))
    }, 500)

    // 🔑 使用 api 而不是 axios，会自动附加 Authorization header
    // 视频分析可能耗时较长，设置 10 分钟超时
    const response = await api.post('/video/analyze', {
      video_id: videoStore.currentVideo.video_id,
      model: analysisConfig.value.model,
      interval: analysisConfig.value.interval,
      max_frames: analysisConfig.value.maxFrames,
      detect_face: analysisConfig.value.detectFace
    }, {
      timeout: 600000  // 10分钟超时（600秒）
    })

    clearInterval(analysisTimer)
    videoStore.setAnalysisProgress(100)
    videoStore.finishAnalysis()

    if (response.data && response.data.success === true) {
      videoStore.setAnalysisResults(response.data)
      currentStep.value = 3
      currentFrameIndex.value = 0

      ElNotification({
        title: '分析完成',
        message: `成功分析 ${response.data.total_frames} 帧图像，耗时 ${analysisElapsed.value} 秒`,
        type: 'success',
        duration: 3000
      })
    } else {
      ElMessage.error('视频分析响应格式错误')
      currentStep.value = 1
    }
  } catch (error) {
    clearInterval(analysisTimer)
    videoStore.finishAnalysis()
    currentStep.value = 1
    console.error('视频分析异常:', error)
    ElMessage.error(error.response?.data?.error || '视频分析失败')
  }
}

function previousFrame() {
  if (currentFrameIndex.value > 0) {
    currentFrameIndex.value--
  }
}

function nextFrame() {
  if (currentFrameIndex.value < videoStore.totalFrames - 1) {
    currentFrameIndex.value++
  }
}

function onFrameSliderChange(value) {
  currentFrameIndex.value = value
}

function resetAnalysis() {
  currentStep.value = 0
  currentFrameIndex.value = 0
  videoStore.clearCurrentVideo()
  clearSelection()
}

// 报告导出：截图结果区域并生成 PDF（与数据分析页同一方案）
const resultsRef = ref(null)
const isExporting = ref(false)

async function downloadReport() {
  if (!resultsRef.value || isExporting.value) return
  isExporting.value = true
  try {
    ElMessage.info('正在生成 PDF 报告，请稍候...')
    const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
      import('html2canvas'),
      import('jspdf')
    ])

    const canvas = await html2canvas(resultsRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff'
    })

    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pageWidth - 20
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 10
    pdf.addImage(canvas.toDataURL('image/jpeg', 0.92), 'JPEG', 10, position, imgWidth, imgHeight)
    heightLeft -= pageHeight - 20

    while (heightLeft > 0) {
      pdf.addPage()
      position = 10 - (imgHeight - heightLeft)
      pdf.addImage(canvas.toDataURL('image/jpeg', 0.92), 'JPEG', 10, position, imgWidth, imgHeight)
      heightLeft -= pageHeight - 20
    }

    pdf.save(`video_emotion_report_${new Date().toISOString().split('T')[0]}.pdf`)
    ElMessage.success('报告导出成功！')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败：' + error.message)
  } finally {
    isExporting.value = false
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function getEmotionEmoji(emotion, isChinese = false) {
  const emotionMap = {
    'anger': '😠', '生气': '😠',
    'disgust': '🤢', '厌恶': '🤢',
    'fear': '😨', '害怕': '😨',
    'happy': '😊', '高兴': '😊',
    'normal': '😐', '平静': '😐',
    'sad': '😢', '悲伤': '😢',
    'surprised': '😲', '惊讶': '😲'
  }
  return emotionMap[emotion] || '😐'
}

function getEmotionTagType(emotion) {
  const typeMap = {
    'anger': 'danger',
    'disgust': 'warning',
    'fear': 'info',
    'happy': 'success',
    'normal': 'info',  // 使用 'info' 代替空字符串
    'sad': 'info',
    'surprised': 'warning'
  }
  return typeMap[emotion] || 'info'  // 默认值改为 'info'
}

function getEmotionColor(emotion) {
  const colorMap = {
    '生气': '#f56c6c',
    '厌恶': '#e6a23c',
    '害怕': 'var(--color-mahogany)',
    '高兴': '#67c23a',
    '平静': '#409eff',
    '悲伤': '#5470c6',
    '惊讶': '#fac858'
  }
  return colorMap[emotion] || '#409eff'
}

// 组件挂载时恢复数据
onMounted(() => {
  loadModelOptions()
  // 如果有保存的分析结果，自动跳转到结果页
  if (videoStore.hasResults) {
    currentStep.value = 3
    currentFrameIndex.value = 0

    ElNotification({
      title: '数据已恢复',
      message: '已自动恢复上次的视频分析结果',
      type: 'success',
      duration: 3000
    })
  }
})
</script>

<style scoped>
.video-analysis-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--el-color-primary-light-9);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.page-header p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.steps-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.upload-card,
.config-card,
.analyzing-card {
  margin-bottom: 30px;
}

.video-upload {
  margin-bottom: 20px;
}

.upload-placeholder {
  text-align: center;
  padding: 60px 20px;
}

.upload-icon {
  color: var(--el-color-primary);
  margin-bottom: 20px;
}

.upload-text {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--color-ink);
}

.upload-hint {
  color: var(--color-mahogany);
  margin: 5px 0;
}

.video-preview {
  text-align: center;
  padding: 20px;
}

.preview-video {
  width: 100%;
  max-width: 800px; /* 增大视频预览的最大宽度 */
  max-height: 600px; /* 增大最大高度 */
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: #000;
}

.video-info {
  margin-top: 20px;
  text-align: left;
  max-width: 800px; /* 与视频宽度保持一致 */
  margin-left: auto;
  margin-right: auto;
}

.upload-progress {
  margin: 20px 0;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.video-info-display {
  margin-bottom: 30px;
}

.video-thumbnail {
  margin-top: 20px;
}

/* 参数配置表单样式 */
.config-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.form-item-spacing {
  margin-bottom: 40px;
}

.model-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.model-radio-group .el-radio {
  margin-right: 0;
  padding: 12px 24px;
}

.slider-container,
.input-container,
.switch-container {
  width: 100%;
}

.interval-slider {
  margin-bottom: 20px;
}

.hint-box {
  background: var(--el-fill-color-light);
  border-left: 4px solid var(--el-color-primary);
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 12px;
}

.config-hint {
  margin: 8px 0;
  color: var(--color-mahogany);
  font-size: 14px;
  line-height: 1.6;
}

.config-hint strong {
  color: var(--el-color-primary);
  font-weight: 600;
}

.max-frames-input {
  width: 200px;
}

.analyzing-content {
  text-align: center;
  padding: 60px 20px;
}

.analyzing-icon {
  color: var(--el-color-primary);
  margin-bottom: 20px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-info {
  max-width: 600px;
  margin: 40px auto 0;
}

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-ink);
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--color-mahogany);
}

.timeline-card,
.frames-card,
.distribution-card {
  margin-bottom: 30px;
}

.emotion-flow {
  padding: 20px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--color-accent) 15%, transparent) 0%, color-mix(in srgb, var(--color-accent) 15%, transparent) 100%);
  border-radius: 8px;
  margin-bottom: 20px;
}

.flow-text {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--color-ink);
  margin-top: 10px;
}

.transitions-list {
  max-height: 400px;
  overflow-y: auto;
}

.transition-text {
  font-size: 1rem;
  font-weight: 500;
}

.frame-detail {
  padding: 20px;
}

.frame-images {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-container h4 {
  margin-bottom: 10px;
  color: var(--color-mahogany);
  width: 100%;
  text-align: left;
}

.frame-image {
  width: 100%;
  max-width: 400px; /* 统一最大宽度 */
  height: 300px; /* 统一高度 */
  object-fit: contain; /* 保持比例，完整显示 */
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  background-color: var(--el-color-primary-light-9); /* 添加背景色以便看清边界 */
}

.frame-analysis {
  padding: 20px;
}

.emotion-display-large {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: var(--el-color-primary-light-9);
  border-radius: 12px;
}

.emotion-emoji {
  font-size: 4rem;
}

.probabilities-list {
  margin-top: 15px;
}

.probability-item {
  margin-bottom: 15px;
}

.prob-label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: var(--color-mahogany);
}

.frame-slider {
  margin-top: 20px;
}

.emotion-stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: var(--el-color-primary-light-9);
  margin-bottom: 15px;
}

.emotion-stat-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: 600;
}

.emotion-stat-header .emotion-emoji {
  font-size: 1.5rem;
}

.stat-count {
  margin-top: 10px;
  color: var(--color-mahogany);
}

.final-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-bottom: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .frame-images {
    gap: 15px;
  }

  .emotion-display-large {
    flex-direction: column;
    text-align: center;
  }
}
</style>
