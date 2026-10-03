<template>
  <div class="image-analysis-view">
    <el-row :gutter="20">
      <!-- 左侧：上传和配置 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="10">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>上传图片</span>
            </div>
          </template>
          
          <!-- 模型选择 -->
          <div class="model-selector">
            <el-text>选择模型:</el-text>
            <el-radio-group v-model="emotionStore.currentModel" class="model-group">
              <el-radio v-for="opt in modelOptions" :key="opt.value" :label="opt.value">
                {{ opt.label }}{{ opt.recommended ? ' · 推荐' : '' }}
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 人脸检测开关 -->
          <div class="face-detect-switch">
            <el-switch
              v-model="detectFace"
              active-text="启用人脸检测"
              inactive-text="使用完整图片"
            />
          </div>

          <!-- 图片上传区域 -->
          <el-upload
            class="upload-area"
            drag
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="handleFileChange"
          >
            <div v-if="!previewImage" class="upload-placeholder">
              <el-icon class="upload-icon"><upload-filled /></el-icon>
              <div class="upload-text">拖拽图片到这里或点击上传</div>
              <div class="upload-hint">支持 JPG, PNG, GIF 格式</div>
            </div>
            <div v-else class="preview-container">
              <img :src="previewImage" alt="预览" />
            </div>
          </el-upload>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :loading="emotionStore.isLoading"
              :disabled="!previewImage"
              @click="handlePredict"
            >
              <el-icon><camera /></el-icon>
              开始识别
            </el-button>
            <el-button
              size="large"
              :disabled="!previewImage"
              @click="handleClear"
            >
              清除
            </el-button>
          </div>

          <!-- 摄像头按钮 -->
          <div class="camera-section">
            <el-button @click="showCameraDialog = true" class="camera-btn">
              <el-icon><video-camera /></el-icon>
              使用摄像头
            </el-button>
          </div>
        </el-card>

        <!-- 历史记录卡片 -->
        <el-card v-if="emotionStore.predictions.length > 0" class="history-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>识别历史</span>
              <el-button text @click="$router.push('/history')">查看全部</el-button>
            </div>
          </template>
          <div class="history-list">
            <div
              v-for="(pred, index) in emotionStore.predictions.slice(0, 5)"
              :key="index"
              class="history-item"
              @click="handleHistoryItemClick(pred)"
              style="cursor: pointer"
            >
              <span class="history-emoji">{{ getEmotionEmoji(pred.emotion) }}</span>
              <span class="history-emotion">{{ pred.emotion_cn }}</span>
              <span class="history-confidence">{{ (pred.confidence * 100).toFixed(1) }}%</span>
              <span class="history-time">{{ formatTime(pred.timestamp) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：识别结果 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="14">
        <el-card class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>识别结果</span>
            </div>
          </template>

          <div v-if="currentResult" class="result-content">
            <!-- 人脸检测对比 -->
            <el-divider>人脸检测与对齐</el-divider>
            <div class="image-compare">
              <div class="image-box">
                <div class="image-title">原始图片</div>
                <img :src="previewImage" alt="原始图" />
              </div>
              <div class="image-box">
                <div class="image-title">人脸区域</div>
                <img v-if="displayFaceImage" :src="displayFaceImage" alt="检测到的人脸" />
                <div v-else class="no-image">暂无人脸区域图片</div>
                <div class="image-note" v-if="displayFaceImage">已检测并对齐人脸区域</div>
              </div>
            </div>
            
            <!-- 主要情绪显示 -->
            <div class="main-emotion">
              <div class="emotion-icon">{{ getEmotionEmoji(currentResult.emotion) }}</div>
              <div class="emotion-info">
                <h2>{{ currentResult.emotion_cn }}</h2>
                <p class="emotion-en">{{ currentResult.emotion }}</p>
                <el-progress
                  :percentage="Math.round(currentResult.confidence * 100)"
                  :color="getProgressColor(currentResult.confidence)"
                  :stroke-width="20"
                />
                <p class="confidence-text">
                  置信度: {{ (currentResult.confidence * 100).toFixed(2) }}%
                </p>
                
                <!-- 心理健康建议按钮 -->
                <el-button 
                  type="success" 
                  size="large" 
                  @click="goToHealth"
                  class="health-btn"
                >
                  <el-icon><reading /></el-icon>
                  查看心理健康建议
                </el-button>
              </div>
            </div>

            <!-- 详细概率分布 -->
            <el-divider>详细概率分布</el-divider>
            <div class="probability-list">
              <div
                v-for="(prob, emotion) in currentResult.probabilities_cn"
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

            <!-- 元信息 -->
            <div class="meta-info">
              <el-tag>模型: {{ currentResult.model_used }}</el-tag>
              <el-tag type="info">
                时间: {{ formatTime(currentResult.timestamp) }}
              </el-tag>
            </div>
          </div>

          <el-empty
            v-else
            description="等待上传图片并识别"
            :image-size="200"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 摄像头对话框 -->
    <el-dialog
      v-model="showCameraDialog"
      title="使用摄像头拍照"
      width="600px"
      :before-close="handleCameraClose"
    >
      <div class="camera-container">
        <video ref="videoRef" autoplay playsinline class="camera-video"></video>
        <canvas ref="canvasRef" style="display: none;"></canvas>
      </div>
      <template #footer>
        <el-button @click="handleCameraClose">取消</el-button>
        <el-button type="primary" @click="handleCapture">拍照</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled, Camera, VideoCamera, Reading } from '@element-plus/icons-vue'
import { useEmotionStore } from '../stores/emotion'

const emotionStore = useEmotionStore()
const router = useRouter()

// 响应式状态
const previewImage = ref('')
const currentResult = ref(null)
const detectFace = ref(true)
const showCameraDialog = ref(false)
const videoRef = ref(null)
const canvasRef = ref(null)
let mediaStream = null

// 展示用的人脸图像（多重兜底）：preprocessed_image -> face_image -> null
const displayFaceImage = computed(() => {
  const r = currentResult.value
  if (!r) return null
  return r.preprocessed_image || r.face_image || null
})

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

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN')
}

// 文件选择处理
function handleFileChange(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    previewImage.value = e.target.result
    currentResult.value = null
  }
  reader.readAsDataURL(file.raw)
}

// 清除
function handleClear() {
  previewImage.value = ''
  currentResult.value = null
}

// 识别
async function handlePredict() {
  if (!previewImage.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  try {
    const result = await emotionStore.predictEmotion(
      previewImage.value,
      detectFace.value
    )
    currentResult.value = result
    
    // 识别成功后提示查看心理健康建议
    ElMessage({
      message: '识别成功! 点击下方按钮查看专业心理健康建议',
      type: 'success',
      duration: 3000
    })
  } catch (error) {
    ElMessage.error('识别失败: ' + error.message)
  }
}

// 点击历史记录项查看详细结果
function handleHistoryItemClick(prediction) {
  // 设置当前结果为点击的历史记录
  currentResult.value = prediction
  // 如果历史记录中包含原始图片，则设置预览图片
  if (prediction.original_image) {
    previewImage.value = prediction.original_image
  } else {
    // 否则使用预处理后的图片作为预览
    previewImage.value = prediction.preprocessed_image
  }
  // 显示提示消息
  ElMessage({
    message: '已加载历史识别结果',
    type: 'info',
    duration: 2000
  })
}

// 跳转到心理健康页面
function goToHealth() {
  router.push('/health')
}

// 摄像头功能
async function startCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
  } catch (error) {
    ElMessage.error('无法访问摄像头: ' + error.message)
  }
}

function handleCapture() {
  if (!videoRef.value || !canvasRef.value) return
  
  const video = videoRef.value
  const canvas = canvasRef.value
  
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)
  
  previewImage.value = canvas.toDataURL('image/jpeg')
  handleCameraClose()
  ElMessage.success('拍照成功!')
}

function handleCameraClose() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  showCameraDialog.value = false
}

// 卸载页面时确保摄像头指示灯熄灭（对话框未关直接跳路由的场景）
onUnmounted(() => {
  handleCameraClose()
})

onMounted(() => {
  emotionStore.checkHealth()
  loadModelOptions()

  // 恢复上次的预测结果
  if (emotionStore.currentPrediction) {
    currentResult.value = emotionStore.currentPrediction
    if (emotionStore.currentPrediction.original_image) {
      previewImage.value = emotionStore.currentPrediction.original_image
    } else {
      previewImage.value = emotionStore.currentPrediction.preprocessed_image
    }
  }
})

// 模型选项：准确率从后端实时获取，失败时使用静态兜底
const modelOptions = ref([
  { value: 'cnn', label: 'CNN (83.77%)', recommended: true },
  { value: 'vgg', label: 'VGG16 (80%)', recommended: false },
  { value: 'se81', label: 'SE-Net (81%)', recommended: false },
  { value: 'se83', label: 'SE-Net (83%)', recommended: true }
])

async function loadModelOptions() {
  try {
    await emotionStore.fetchModels()
    const models = emotionStore.availableModels
    if (Array.isArray(models) && models.length) {
      modelOptions.value = models.map((m) => {
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
    // 保留静态兜底
  }
}

// 监听摄像头对话框打开
watch(() => showCameraDialog.value, (newVal) => {
  if (newVal) {
    nextTick(() => startCamera())
  }
})
</script>

<style scoped>
.image-analysis-view {
  width: 100%;
  max-width: 1400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.upload-card,
.result-card,
.history-card {
  margin-bottom: 1.5rem;
  border-radius: 12px;
}

/* 模型选择 */
.model-selector {
  margin-bottom: 1.5rem;
}

.model-group {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.face-detect-switch {
  margin-bottom: 1.5rem;
}

/* 上传区域 */
.upload-area {
  margin-bottom: 1.5rem;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 2rem;
  border-radius: 8px;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 4rem;
  color: var(--el-color-primary);
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.upload-hint {
  color: var(--color-mahogany);
  font-size: 0.875rem;
}

.preview-container {
  width: 100%;
  max-height: 400px;
  overflow: hidden;
  border-radius: 8px;
}

.preview-container img {
  width: 100%;
  height: auto;
  display: block;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.action-buttons .el-button {
  flex: 1;
}

.camera-section {
  text-align: center;
}

.camera-btn {
  width: 100%;
}

/* 识别结果 */
.result-content {
  min-height: 400px;
}

.image-compare {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.image-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.image-title {
  font-weight: 600;
}

.image-box img {
  width: 100%;
  max-height: 260px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid var(--color-sand);
  background: var(--color-parchment);
}

.image-note {
  font-size: 0.875rem;
  color: var(--color-mahogany);
  text-align: center;
}

.main-emotion {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--color-accent)20 0%, var(--color-accent)20 100%);
  border-radius: 12px;
}

.emotion-icon {
  font-size: 6rem;
  line-height: 1;
}

.emotion-info {
  flex: 1;
}

.emotion-info h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--color-ink);
}

.emotion-en {
  color: var(--color-mahogany);
  font-size: 1rem;
  margin-bottom: 1rem;
  text-transform: capitalize;
}

.confidence-text {
  margin-top: 0.5rem;
  color: var(--color-mahogany);
  font-weight: bold;
}

.health-btn {
  width: 100%;
  margin-top: 1rem;
  font-size: 1.1rem;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #67c23a 0%, #5daf34 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
  transition: all 0.3s;
}

.health-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(103, 194, 58, 0.4);
}

/* 概率列表 */
.probability-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.probability-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.prob-label {
  width: 120px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.prob-emoji {
  font-size: 1.5rem;
}

.probability-item .el-progress {
  flex: 1;
}

/* 元信息 */
.meta-info {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* 历史记录 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  transition: all 0.3s;
}

.history-item:hover {
  background: #e8eaed;
  transform: translateX(4px);
}

.history-emoji {
  font-size: 1.5rem;
}

.history-emotion {
  flex: 1;
  font-weight: 500;
}

.history-confidence {
  color: #67c23a;
  font-weight: bold;
}

.history-time {
  color: var(--color-mahogany);
  font-size: 0.875rem;
}

/* 摄像头 */
.camera-container {
  text-align: center;
}

.camera-video {
  width: 100%;
  max-width: 500px;
  border-radius: 8px;
  background: #000;
}

/* 响应式 */
@media (max-width: 768px) {
  .main-emotion {
    flex-direction: column;
    text-align: center;
  }

  .emotion-info h2 {
    font-size: 1.5rem;
  }

  .prob-label {
    width: 100px;
    font-size: 0.85rem;
  }
  
  .image-compare {
    flex-direction: column;
  }
}
</style>
