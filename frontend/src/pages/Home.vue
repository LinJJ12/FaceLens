<template>
  <div class="home-container">
    <!-- 欢迎横幅 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-eyebrow">FaceLens · 基于 RAF-DB</div>
        <h1 class="hero-title">看见情绪，<br />理解每一种表达</h1>
        <p class="hero-description">
          基于深度学习的人脸情绪分析平台，利用卷积神经网络与注意力机制，
          准确识别开心、悲伤、惊讶、愤怒、恐惧、厌恶、平静 7 种基本情绪。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="goToImageAnalysis">
            <el-icon><camera /></el-icon>
            开始图片识别
          </el-button>
          <el-button size="large" @click="goToVideoAnalysis">
            <el-icon><video-camera /></el-icon>
            视频情绪分析
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <div class="floating-card">
          <div class="emotion-showcase">
            <div class="emotion-showcase-row">
              <div v-for="(emotion, index) in emotions.slice(0, 3)" :key="index" class="emotion-item" :style="{ animationDelay: `${index * 0.1}s` }">
                <span class="emotion-emoji">{{ emotion.emoji }}</span>
                <span class="emotion-name">{{ emotion.name }}</span>
              </div>
            </div>
            <div class="emotion-showcase-row">
              <div v-for="(emotion, index) in emotions.slice(3)" :key="index + 3" class="emotion-item" :style="{ animationDelay: `${(index + 3) * 0.1}s` }">
                <span class="emotion-emoji">{{ emotion.emoji }}</span>
                <span class="emotion-name">{{ emotion.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能特性 -->
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="feature in features" :key="feature.title" class="feature-col">
          <el-card class="feature-card" shadow="never" @click="handleFeatureClick(feature.route)">
            <div class="feature-icon">
              <el-icon :size="26"><component :is="feature.icon" /></el-icon>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- AI模型介绍 -->
    <div class="models-section">
      <h2 class="section-title">AI 模型</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="model in models" :key="model.name">
          <el-card class="model-card" shadow="never">
            <div class="model-badge" v-if="model.recommended">推荐</div>
            <div class="model-badge model-badge-muted" v-else-if="model.available === false">离线</div>
            <div class="model-name">{{ model.name }}</div>
            <div class="model-accuracy">
              <el-progress
                type="circle"
                :percentage="model.accuracy"
                :width="80"
                color="var(--color-accent)"
              />
            </div>
            <div class="model-features">
              <el-tag v-for="tag in model.tags" :key="tag" size="small" class="model-tag" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
            <p class="model-desc">{{ model.description }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快速开始指南 -->
    <div class="quick-start-section">
      <el-card class="quick-start-card" shadow="never">
        <h2 class="section-title">快速开始</h2>
        <el-steps :active="0" align-center>
          <el-step title="上传图片" description="支持JPG/PNG格式" icon="Upload" />
          <el-step title="选择模型" description="4种AI模型可选" icon="Setting" />
          <el-step title="开始识别" description="快速分析情绪" icon="View" />
          <el-step title="查看结果" description="详细情绪报告" icon="Document" />
        </el-steps>
        <div class="quick-start-actions">
          <el-button type="primary" size="large" @click="goToImageAnalysis">
            立即体验
            <el-icon><arrow-right /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 最近识别历史 -->
    <div class="recent-section" v-if="emotionStore.predictions.length > 0">
      <h2 class="section-title">最近识别</h2>
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="8" :lg="6"
                v-for="(pred, index) in recentPredictions"
                :key="index">
          <el-card class="recent-card" shadow="never" @click="viewPrediction(pred)">
            <div class="recent-image">
              <img :src="pred.preprocessed_image || pred.image" alt="识别图片" />
              <div class="recent-overlay">
                <span class="recent-emotion">{{ pred.emotion_cn }}</span>
              </div>
            </div>
            <div class="recent-info">
              <div class="recent-confidence">
                <el-tag :type="getConfidenceType(pred.confidence)" effect="plain">
                  {{ (pred.confidence * 100).toFixed(1) }}%
                </el-tag>
              </div>
              <div class="recent-time">{{ formatTime(pred.timestamp) }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEmotionStore } from '../stores/emotion'
import { Camera, VideoCamera, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const emotionStore = useEmotionStore()

// 情绪展示
const emotions = [
  { emoji: '😊', name: '开心' },
  { emoji: '😢', name: '悲伤' },
  { emoji: '😱', name: '惊讶' },
  { emoji: '😠', name: '愤怒' },
  { emoji: '😰', name: '恐惧' },
  { emoji: '🤢', name: '厌恶' },
  { emoji: '😐', name: '平静' }
]

// 功能特性
const features = [
  {
    icon: 'Camera',
    title: '图片识别',
    description: '上传图片快速识别情绪',
    route: '/image-analysis'
  },
  {
    icon: 'VideoCamera',
    title: '视频分析',
    description: '逐帧分析视频情绪变化',
    route: '/video'
  },
  {
    icon: 'FirstAidKit',
    title: '心理健康',
    description: '个性化心理健康建议',
    route: '/health'
  },
  {
    icon: 'DataAnalysis',
    title: '数据分析',
    description: '可视化情绪统计图表',
    route: '/data-analysis'
  },
  {
    icon: 'Clock',
    title: '历史记录',
    description: '查看所有识别历史',
    route: '/history'
  },
  {
    icon: 'User',
    title: '个人中心',
    description: '管理个人信息和设置',
    route: '/user'
  },
  {
    icon: 'Setting',
    title: '系统管理',
    description: '用户和权限管理',
    route: '/admin'
  },
  {
    icon: 'InfoFilled',
    title: '关于系统',
    description: '了解系统详细信息',
    route: '/about'
  }
]

// 模型展示的静态元数据（accuracy/available 以后端 /api/models 为准）
const defaultModels = [
  {
    key: 'cnn',
    name: 'CNN',
    accuracy: 83.77,
    recommended: true,
    tags: ['快速', '准确'],
    description: '经典卷积神经网络，平衡速度与精度'
  },
  {
    key: 'vgg',
    name: 'VGG16',
    accuracy: 80,
    recommended: false,
    tags: ['稳定', '可靠'],
    description: '深度网络结构，特征提取能力强'
  },
  {
    key: 'se81',
    name: 'SE-Net 81',
    accuracy: 81,
    recommended: false,
    tags: ['注意力', '高效'],
    description: '通道注意力机制，提升关键特征'
  },
  {
    key: 'se83',
    name: 'SE-Net 83',
    accuracy: 83,
    recommended: true,
    tags: ['最优', '精确'],
    description: '优化版SE网络，最佳识别效果'
  }
]

const models = ref(defaultModels)

// 最近识别记录
const recentPredictions = computed(() => {
  return emotionStore.predictions.slice(0, 4)
})

// 功能点击处理
const handleFeatureClick = (route) => {
  if (route) {
    router.push(route)
  }
}

const goToImageAnalysis = () => router.push('/image-analysis')
const goToVideoAnalysis = () => router.push('/video')

// 查看预测详情
const viewPrediction = (pred) => {
  emotionStore.currentPrediction = pred
  router.push('/image-analysis')
  ElMessage.info('已加载识别记录')
}

// 置信度类型
const getConfidenceType = (confidence) => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'info'
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

// 页面加载：模型准确率从后端实时获取
onMounted(async () => {
  try {
    await emotionStore.fetchModels()
    const apiModels = emotionStore.availableModels
    if (Array.isArray(apiModels) && apiModels.length) {
      models.value = defaultModels.map((m) => {
        const found = apiModels.find(
          (x) => String(x.name || '').toLowerCase() === m.key
        )
        if (!found) return m
        return {
          ...m,
          accuracy: typeof found.accuracy === 'number' && found.accuracy <= 1
            ? Number((found.accuracy * 100).toFixed(2))
            : Number(found.accuracy ?? m.accuracy),
          available: found.available !== false,
          description: found.description || m.description
        }
      })
    }
  } catch (error) {
    // 后端不可用时保留静态兜底数据
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

/* 英雄区域 */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 440px;
  margin-bottom: 56px;
  gap: 60px;
}

.hero-content {
  flex: 1.2;
  max-width: 620px;
}

.hero-eyebrow {
  display: inline-block;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.02em;
  color: var(--color-mahogany);
  border: 1px solid var(--color-sand);
  border-radius: 999px;
  padding: 0.375rem 0.875rem;
  margin-bottom: 20px;
  background: var(--color-surface);
}

.hero-title {
  font-size: 46px;
  font-weight: 700;
  margin-bottom: 18px;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: var(--color-ink);
}

.hero-description {
  font-size: 16px;
  color: var(--color-mahogany);
  margin-bottom: 30px;
  line-height: 1.7;
  max-width: 520px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-image {
  flex: 0.9;
  display: flex;
  justify-content: center;
  align-items: center;
}

.floating-card {
  background: var(--color-surface);
  border-radius: 20px;
  padding: 30px;
  box-shadow: var(--shadow-md);
  animation: float 4s ease-in-out infinite;
  max-width: 480px;
  border: 1px solid var(--color-sand);
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
}

.emotion-showcase {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.emotion-showcase-row {
  display: flex;
  gap: 14px;
  justify-content: center;
}

.emotion-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 22px;
  background: var(--color-parchment);
  border-radius: 14px;
  transition: all 0.25s ease;
  animation: fadeInUp 0.6s ease-out backwards;
  min-width: 88px;
  border: 1px solid var(--color-sand);
}

.emotion-item:hover {
  transform: translateY(-4px);
  border-color: var(--color-mahogany);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.emotion-emoji {
  font-size: 40px;
}

.emotion-name {
  font-size: 14px;
  color: var(--color-mahogany);
  font-weight: 500;
}

/* 章节标题 */
.section-title {
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 36px;
  color: var(--color-ink);
}

/* 功能特性 */
.features-section {
  margin-top: 24px;
  margin-bottom: 56px;
}

.feature-col {
  margin-bottom: 20px;
}

.feature-card {
  text-align: left;
  cursor: pointer;
  transition: all 0.25s;
  height: 100%;
}

.feature-card:hover {
  border-color: var(--color-mahogany);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: var(--color-ink);
  background: var(--el-color-primary-light-9);
  border: 1px solid var(--color-sand);
  transition: transform 0.25s;
}

.feature-card:hover .feature-icon {
  transform: scale(1.06);
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-ink);
  text-align: center;
}

.feature-desc {
  font-size: 13px;
  color: var(--color-mahogany);
  line-height: 1.5;
  text-align: center;
}

/* AI模型介绍 */
.models-section {
  margin-bottom: 56px;
}

.model-card {
  text-align: center;
  position: relative;
  height: 100%;
  transition: all 0.25s;
}

.model-card:hover {
  border-color: var(--color-mahogany);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.model-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: var(--color-accent);
  color: #fafafa;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.model-badge-muted {
  background: var(--color-parchment);
  color: var(--color-mahogany);
  border: 1px solid var(--color-sand);
}

.model-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 18px;
  color: var(--color-ink);
}

.model-accuracy {
  margin-bottom: 18px;
}

.model-features {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.model-tag {
  margin: 0;
}

.model-desc {
  font-size: 13px;
  color: var(--color-mahogany);
  line-height: 1.5;
}

/* 快速开始 */
.quick-start-section {
  margin-bottom: 56px;
}

.quick-start-card {
  background: var(--color-surface);
}

.quick-start-actions {
  text-align: center;
  margin-top: 32px;
}

/* 最近识别 */
.recent-section {
  margin-bottom: 40px;
}

.recent-card {
  cursor: pointer;
  transition: all 0.25s;
  overflow: hidden;
}

.recent-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.recent-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 10px;
  background: var(--el-color-primary-light-9);
}

.recent-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.recent-card:hover .recent-image img {
  transform: scale(1.06);
}

.recent-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.65), transparent);
  padding: 10px;
  color: white;
}

.recent-emotion {
  font-size: 15px;
  font-weight: 600;
}

.recent-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-time {
  font-size: 12px;
  color: var(--color-mahogany);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
  }

  .hero-content {
    max-width: 100%;
  }

  .hero-description {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .section-title {
    font-size: 22px;
  }

  .emotion-item {
    padding: 12px;
  }

  .emotion-emoji {
    font-size: 28px;
  }
}
</style>
