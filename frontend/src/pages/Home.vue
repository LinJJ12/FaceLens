<template>
  <div class="home-container">
    <!-- 欢迎横幅 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">智能情绪识别系统</span>
        </h1>
        <p class="hero-subtitle">基于深度学习的人脸情绪分析平台</p>
        <p class="hero-description">利用先进的卷积神经网络技术，准确识别7种基本情绪表情</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="goToImageAnalysis">
            <el-icon><camera /></el-icon>
            开始图片识别
          </el-button>
          <el-button type="success" size="large" @click="goToVideoAnalysis">
            <el-icon><video-camera /></el-icon>
            视频情绪分析
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <div class="floating-card">
          <div class="emotion-showcase">
            <!-- 上面三个 -->
            <div class="emotion-showcase-row">
              <div v-for="(emotion, index) in emotions.slice(0, 3)" :key="index" class="emotion-item" :style="{ animationDelay: `${index * 0.1}s` }">
                <span class="emotion-emoji">{{ emotion.emoji }}</span>
                <span class="emotion-name">{{ emotion.name }}</span>
              </div>
            </div>
            <!-- 下面四个 -->
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
      <el-row :gutter="30">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="feature in features" :key="feature.title" class="feature-col">
          <el-card class="feature-card" shadow="hover" @click="handleFeatureClick(feature.route)">
            <div class="feature-icon" :style="{ background: feature.color }">
              <el-icon :size="34"><component :is="feature.icon" /></el-icon>
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
          <el-card class="model-card" shadow="hover">
            <div class="model-badge" v-if="model.recommended">推荐</div>
            <div class="model-name">{{ model.name }}</div>
            <div class="model-accuracy">
              <el-progress 
                type="circle" 
                :percentage="model.accuracy" 
                :width="80"
                :color="model.color"
              />
            </div>
            <div class="model-features">
              <el-tag v-for="tag in model.tags" :key="tag" size="small" class="model-tag">
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
      <el-card class="quick-start-card">
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
          <el-card class="recent-card" shadow="hover" @click="viewPrediction(pred)">
            <div class="recent-image">
              <img :src="pred.preprocessed_image || pred.image" alt="识别图片" />
              <div class="recent-overlay">
                <span class="recent-emotion">{{ pred.emotion_cn }}</span>
              </div>
            </div>
            <div class="recent-info">
              <div class="recent-confidence">
                <el-tag :type="getConfidenceType(pred.confidence)">
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
    route: '/image-analysis',
    color: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)'
  },
  {
    icon: 'VideoCamera',
    title: '视频分析',
    description: '逐帧分析视频情绪变化',
    route: '/video',
    color: 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)'
  },
  {
    icon: 'FirstAidKit',
    title: '心理健康',
    description: '个性化心理健康建议',
    route: '/health',
    color: 'linear-gradient(135deg, #14B8A6 0%, #2DD4BF 100%)'
  },
  {
    icon: 'DataAnalysis',
    title: '数据分析',
    description: '可视化情绪统计图表',
    route: '/data-analysis',
    color: 'linear-gradient(135deg, #0EA5E9 0%, #38BDF8 100%)'
  },
  {
    icon: 'Clock',
    title: '历史记录',
    description: '查看所有识别历史',
    route: '/history',
    color: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)'
  },
  {
    icon: 'User',
    title: '个人中心',
    description: '管理个人信息和设置',
    route: '/user',
    color: 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)'
  },
  {
    icon: 'Setting',
    title: '系统管理',
    description: '用户和权限管理',
    route: '/admin',
    color: 'linear-gradient(135deg, #14B8A6 0%, #2DD4BF 100%)'
  },
  {
    icon: 'InfoFilled',
    title: '关于系统',
    description: '了解系统详细信息',
    route: '/about',
    color: 'linear-gradient(135deg, #0EA5E9 0%, #38BDF8 100%)'
  }
]

// AI模型介绍
const models = [
  {
    name: 'CNN',
    accuracy: 83.77,
    color: '#6366F1',
    recommended: true,
    tags: ['快速', '准确'],
    description: '经典卷积神经网络，平衡速度与精度'
  },
  {
    name: 'VGG16',
    accuracy: 80,
    color: '#f093fb',
    recommended: false,
    tags: ['稳定', '可靠'],
    description: '深度网络结构，特征提取能力强'
  },
  {
    name: 'SE-Net 81',
    accuracy: 81,
    color: '#4facfe',
    recommended: false,
    tags: ['注意力', '高效'],
    description: '通道注意力机制，提升关键特征'
  },
  {
    name: 'SE-Net 83',
    accuracy: 83,
    color: '#43e97b',
    recommended: true,
    tags: ['最优', '精确'],
    description: '优化版SE网络，最佳识别效果'
  }
]

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

// 页面加载
onMounted(() => {
  // 初始化逻辑
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
  min-height: 500px;
  margin-bottom: 60px;
  gap: 60px;
}

.hero-content {
  flex: 1.2;
  max-width: 650px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
  color: #1A2456;
}

.gradient-text {
  background: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 24px;
  color: rgba(26, 36, 86, 0.8);
  margin-bottom: 10px;
  font-weight: 500;
}

.hero-description {
  font-size: 16px;
  color: rgba(26, 36, 86, 0.7);
  margin-bottom: 30px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.hero-image {
  flex: 0.9;
  display: flex;
  justify-content: center;
  align-items: center;
}

.floating-card {
  background: rgba(226, 232, 240, 0.3);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
  animation: float 3s ease-in-out infinite;
  max-width: 500px;
  border: 1px solid #E2E8F0;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.emotion-showcase {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.emotion-showcase-row {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.emotion-item:nth-child(1),
.emotion-item:nth-child(2),
.emotion-item:nth-child(3) {
  /* 第一行：3个 */
}

.emotion-item:nth-child(n+4) {
  /* 第二行：4个 */
}

.emotion-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out backwards;
  min-width: 90px;
  border: 1px solid #E2E8F0;
}

.emotion-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
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
  font-size: 42px;
}

.emotion-name {
  font-size: 15px;
  color: #606266;
  font-weight: 500;
}

/* 章节标题 */
.section-title {
  text-align: center;
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 40px;
  color: #1A2456;
  position: relative;
  padding-bottom: 14px;
}

.section-title::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 44px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, #6366F1, #8B5CF6);
}

/* 功能特性 */
.features-section {
  margin-top: 80px; /* 增加顶部间距，让"核心功能"标题向下移动 */
  margin-bottom: 60px;
}

.feature-col {
  margin-bottom: 30px; /* 为每个列添加底部间距 */
}

.feature-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  height: 100%;
  margin-bottom: 40px; /* 增加卡片下方间距，让模块之间分开更多 */
}

.feature-card:hover {
  transform: translateY(-8px);
  border-color: rgba(79, 70, 229, 0.45);
  box-shadow: 0 20px 25px -5px rgba(26, 36, 86, 0.15), 0 10px 10px -5px rgba(26, 36, 86, 0.08);
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  font-size: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  transition: transform 0.3s;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1) rotate(5deg);
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #1A2456;
}

.feature-desc {
  font-size: 14px;
  color: rgba(26, 36, 86, 0.7);
  line-height: 1.5;
}

/* AI模型介绍 */
.models-section {
  margin-bottom: 60px;
}

.model-card {
  text-align: center;
  position: relative;
  height: 100%;
  transition: all 0.3s;
}

.model-card:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.model-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #4F46E5;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
}

.model-name {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #1A2456;
}

.model-accuracy {
  margin-bottom: 20px;
}

.model-features {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.model-tag {
  margin: 0;
}

.model-desc {
  font-size: 14px;
  color: rgba(26, 36, 86, 0.7);
  line-height: 1.5;
}

/* 快速开始 */
.quick-start-section {
  margin-bottom: 60px;
}

.quick-start-card {
  background: rgba(226, 232, 240, 0.2);
  border: 2px solid #E2E8F0;
}

.quick-start-actions {
  text-align: center;
  margin-top: 40px;
}

/* 最近识别 */
.recent-section {
  margin-bottom: 40px;
}

.recent-card {
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
}

.recent-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.recent-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 10px;
}

.recent-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.recent-card:hover .recent-image img {
  transform: scale(1.1);
}

.recent-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  padding: 10px;
  color: white;
}

.recent-emotion {
  font-size: 16px;
  font-weight: 600;
}

.recent-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-time {
  font-size: 12px;
  color: rgba(26, 36, 86, 0.6);
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
  
  .hero-actions {
    justify-content: center;
  }
  
  .emotion-showcase {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 18px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .emotion-showcase {
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  
  .emotion-item {
    padding: 12px;
  }
  
  .emotion-emoji {
    font-size: 28px;
  }
  
  .stats-section {
    padding: 20px;
  }
  
  .stat-value {
    font-size: 28px;
  }
}
</style>
