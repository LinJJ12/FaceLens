<template>
  <div class="landing">
    <!-- 顶部导航 -->
    <header class="landing-nav">
      <div class="nav-inner">
        <div class="brand">
          <svg class="brand-mark" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6" />
            <circle cx="12" cy="12" r="3.4" stroke="currentColor" stroke-width="1.6" />
            <circle cx="12" cy="12" r="0.8" fill="currentColor" />
          </svg>
          <span class="wordmark">FaceLens</span>
          <span class="brand-tag">人脸情绪识别</span>
        </div>

        <nav class="nav-links">
          <a href="#/" @click.prevent="scrollTo('features')">功能</a>
          <a href="#/" @click.prevent="scrollTo('models')">模型</a>
          <a href="#/" @click.prevent="scrollTo('privacy')">隐私</a>
          <a
            class="github-link"
            href="https://github.com/LinJJ12/FaceLens"
            target="_blank"
            rel="noopener noreferrer"
          >
            <el-icon><Link /></el-icon>
            GitHub
          </a>
        </nav>

        <div class="nav-actions">
          <button class="theme-toggle" :title="isDark ? '切换到浅色' : '切换到深色'" @click="toggleTheme">
            <el-icon><Moon v-if="!isDark" /><Sunny v-else /></el-icon>
          </button>
          <router-link v-if="isLoggedIn" to="/home" class="btn btn-primary">进入工作台</router-link>
          <template v-else>
            <router-link to="/login" class="btn btn-ghost">登录</router-link>
            <router-link to="/login?mode=register" class="btn btn-primary">立即开始</router-link>
          </template>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner">
        <span class="hero-badge">基于 RAF-DB · 端到端情绪识别</span>
        <h1 class="hero-title">
          看见情绪的<br />
          <span class="hero-title-accent">每一种样子</span>
        </h1>
        <p class="hero-sub">
          FaceLens 从模型训练到 Web 应用覆盖完整链路：MTCNN 人脸检测对齐、四套可切换模型、
          视频/图片情绪分析、数据分析与心理健康辅助——全部运行在你自己的设备上。
        </p>
        <div class="hero-ctas">
          <router-link v-if="isLoggedIn" to="/home" class="btn btn-primary btn-lg">进入工作台</router-link>
          <router-link v-else to="/login" class="btn btn-primary btn-lg">免费开始使用</router-link>
          <a href="#/" class="btn btn-ghost btn-lg" @click.prevent="scrollTo('features')">了解功能</a>
        </div>

        <ul class="hero-stats">
          <li><strong>83.77%</strong><span>测试集最高准确率</span></li>
          <li><strong>4 套</strong><span>可在线切换模型</span></li>
          <li><strong>7 类</strong><span>情绪细粒度识别</span></li>
          <li><strong>100%</strong><span>数据本地存储</span></li>
        </ul>
      </div>

      <!-- 界面预览 -->
      <div class="preview-frame">
        <div class="preview-bar">
          <i></i><i></i><i></i>
          <span>FaceLens — 工作台</span>
        </div>
        <img :src="previewImage" alt="FaceLens 界面预览" loading="lazy" />
      </div>
    </section>

    <!-- 功能 -->
    <section id="features" class="section">
      <h2 class="section-title">完整的功能闭环</h2>
      <p class="section-sub">从一次快照到一份心理健康报告，FaceLens 覆盖情绪识别的每一步。</p>

      <div class="feature-grid">
        <div v-for="f in features" :key="f.title" class="feature-card">
          <div class="feature-icon"><el-icon :size="22"><component :is="f.icon" /></el-icon></div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 模型 -->
    <section id="models" class="section">
      <h2 class="section-title">四套模型，随时切换</h2>
      <p class="section-sub">同一界面在线切换，准确率与推理表现一目了然。</p>

      <div class="model-grid">
        <div v-for="m in models" :key="m.name" class="model-card">
          <div class="model-head">
            <span class="model-name">{{ m.name }}</span>
            <span class="model-acc">{{ m.acc }}</span>
          </div>
          <div class="model-bar"><i :style="{ width: m.bar }"></i></div>
          <p class="model-desc">{{ m.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 隐私 -->
    <section id="privacy" class="section">
      <div class="privacy-card">
        <div class="privacy-icon"><el-icon :size="26"><Lock /></el-icon></div>
        <div>
          <h3>数据不出你的设备</h3>
          <p>
            上传的图片、视频与分析记录仅保存在本地数据库与文件目录；JWT 本地签发校验，
            不依赖任何第三方云服务。系统输出仅供参考，不构成任何医学或心理诊断建议。
          </p>
        </div>
      </div>
    </section>

    <!-- 底部 CTA -->
    <section class="cta-band">
      <h2>准备好认识你的情绪了吗？</h2>
      <div class="hero-ctas">
        <router-link v-if="isLoggedIn" to="/home" class="btn btn-primary btn-lg">进入工作台</router-link>
        <router-link v-else to="/login" class="btn btn-primary btn-lg">免费开始使用</router-link>
      </div>
    </section>

    <footer class="landing-footer">
      <span>© 2025–2026 FaceLens · 基于 RAF-DB 的人脸情绪识别系统</span>
      <span>CC BY-NC 4.0 · 仅供学习研究，禁止商用</span>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  Picture,
  VideoCamera,
  Cpu,
  DataAnalysis,
  Sunny,
  Lock,
  Link,
  Moon,
  User as UserIcon,
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import previewImage from '../assets/landing-preview.jpg'

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

// App.vue 在其 onMounted 中才应用 html.dark，子组件 setup 阶段读取会早于该时机，
// 因此主题状态在挂载后初始化
const isDark = ref(false)

onMounted(() => {
  isDark.value = document.documentElement.classList.contains('dark')
})

// hash 路由下原生锚点会与 vue-router 冲突，改为程序化滚动。
// 使用即时定位：部分内嵌 WebView 会取消平滑滚动动画导致定位失效
function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ block: 'start' })
}

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  // 与 App.vue / Layout / User 的主题存储保持一致
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const features = [
  {
    icon: Picture,
    title: '图片识别',
    desc: '单图预测，MTCNN 人脸检测、对齐与质量评估（清晰度 / 亮度 / 对比度），支持摄像头拍照。',
  },
  {
    icon: VideoCamera,
    title: '视频分析',
    desc: '视频抽帧逐帧分析，输出情绪时间轴、转换记录与情绪流，支持一键导出 PDF 报告。',
  },
  {
    icon: Cpu,
    title: '多模型切换',
    desc: 'CNN / VGG16 / SE-Net 四套权重在线切换，准确率实时从后端读取。',
  },
  {
    icon: DataAnalysis,
    title: '数据分析',
    desc: '情绪分布、趋势、置信度、时段与日历热力图等 8 类图表，洞察你的情绪轨迹。',
  },
  {
    icon: Sunny,
    title: '心理健康辅助',
    desc: '基于情绪记录的心理状态参考、情绪日记、感恩记录与放松训练。',
  },
  {
    icon: UserIcon,
    title: '账户与管理',
    desc: 'JWT 认证、令牌自动刷新、头像资料管理，管理后台统一管理用户与数据。',
  },
]

const models = [
  { name: 'CNN', acc: '83.77%', bar: '84%', desc: '经典卷积网络，速度与精度均衡' },
  { name: 'SE-Net 83', acc: '83%', bar: '83%', desc: '优化版 SE 注意力网络' },
  { name: 'SE-Net 81', acc: '81%', bar: '81%', desc: '通道注意力机制模型' },
  { name: 'VGG16', acc: '80%', bar: '80%', desc: '深层迁移学习，特征提取能力强' },
]
</script>

<style scoped>
.landing {
  min-height: 100vh;
  background: var(--color-parchment);
  color: var(--color-ink);
}

/* ---------- 导航 ---------- */
.landing-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--color-parchment) 82%, transparent);
  border-bottom: 1px solid var(--color-sand);
}

.nav-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-mark {
  width: 22px;
  height: 22px;
  color: var(--color-ink);
}

.wordmark {
  font-weight: 700;
  letter-spacing: -0.02em;
  font-size: 1.05rem;
  color: var(--color-ink);
}

.brand-tag {
  font-size: 0.72rem;
  color: var(--color-mahogany);
  border: 1px solid var(--color-sand);
  border-radius: 999px;
  padding: 2px 8px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-left: auto;
}

.nav-links a {
  color: var(--color-mahogany);
  font-size: 0.9rem;
  text-decoration: none;
}

.nav-links a:hover {
  color: var(--color-ink);
}

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.theme-toggle {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--color-sand);
  background: var(--color-surface);
  color: var(--color-ink);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: background var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--el-fill-color-light);
}

/* ---------- 按钮 ---------- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-base);
  border: 1px solid transparent;
}

.btn-primary {
  background: var(--color-accent);
  color: var(--color-parchment);
}

.btn-primary:hover {
  background: var(--color-accent-hover);
}

.btn-ghost {
  border-color: var(--color-sand);
  color: var(--color-ink);
  background: var(--color-surface);
}

.btn-ghost:hover {
  background: var(--el-fill-color-light);
}

.btn-lg {
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 12px;
}

/* ---------- Hero ---------- */
.hero {
  max-width: 1120px;
  margin: 0 auto;
  padding: 5.5rem 1.5rem 3rem;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  font-size: 0.8rem;
  color: var(--color-mahogany);
  border: 1px solid var(--color-sand);
  background: var(--color-surface);
  border-radius: 999px;
  padding: 6px 14px;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: clamp(2.4rem, 6vw, 4rem);
  line-height: 1.12;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 1.25rem;
}

.hero-title-accent {
  color: var(--color-accent);
}

.hero-sub {
  max-width: 620px;
  margin: 0 auto 2rem;
  color: var(--color-mahogany);
  font-size: 1.05rem;
  line-height: 1.75;
}

.hero-ctas {
  display: flex;
  justify-content: center;
  gap: 0.8rem;
  flex-wrap: wrap;
  margin-bottom: 2.5rem;
}

.hero-stats {
  list-style: none;
  display: flex;
  justify-content: center;
  gap: clamp(1.5rem, 5vw, 3.5rem);
  padding: 0;
  margin: 0 0 3rem;
  flex-wrap: wrap;
}

.hero-stats li {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hero-stats strong {
  font-size: 1.6rem;
  letter-spacing: -0.02em;
}

.hero-stats span {
  font-size: 0.8rem;
  color: var(--color-mahogany);
}

/* ---------- 预览图 ---------- */
.preview-frame {
  max-width: 880px;
  margin: 0 auto;
  border: 1px solid var(--color-sand);
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
}

.preview-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-sand);
  background: var(--el-fill-color-light);
}

.preview-bar i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-sand);
}

.preview-bar span {
  margin-left: 10px;
  font-size: 0.75rem;
  color: var(--color-mahogany);
}

.preview-frame img {
  display: block;
  width: 100%;
}

/* ---------- 区块 ---------- */
.section {
  max-width: 1120px;
  margin: 0 auto;
  padding: 4.5rem 1.5rem 0;
}

.section-title {
  text-align: center;
  font-size: 1.9rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem;
}

.section-sub {
  text-align: center;
  color: var(--color-mahogany);
  margin: 0 0 2.5rem;
}

/* ---------- 功能卡片 ---------- */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.feature-card {
  background: var(--color-surface);
  border: 1px solid var(--color-sand);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  transition: box-shadow var(--transition-base), transform var(--transition-base);
}

.feature-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.feature-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--el-fill-color-light);
  color: var(--color-ink);
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin: 0 0 0.4rem;
  font-size: 1.02rem;
}

.feature-card p {
  margin: 0;
  color: var(--color-mahogany);
  font-size: 0.9rem;
  line-height: 1.7;
}

/* ---------- 模型卡片 ---------- */
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.model-card {
  background: var(--color-surface);
  border: 1px solid var(--color-sand);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.25rem 1.4rem;
}

.model-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.75rem;
}

.model-name {
  font-weight: 600;
}

.model-acc {
  font-weight: 700;
  letter-spacing: -0.02em;
}

.model-bar {
  height: 6px;
  border-radius: 999px;
  background: var(--el-fill-color-light);
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.model-bar i {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: var(--color-accent);
}

.model-desc {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-mahogany);
}

/* ---------- 隐私 ---------- */
.privacy-card {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
  background: var(--color-surface);
  border: 1px solid var(--color-sand);
  border-radius: var(--radius-xl);
  padding: 2rem;
}

.privacy-icon {
  flex: none;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: var(--el-fill-color-light);
  color: var(--color-ink);
}

.privacy-card h3 {
  margin: 0 0 0.5rem;
}

.privacy-card p {
  margin: 0;
  color: var(--color-mahogany);
  line-height: 1.8;
  font-size: 0.92rem;
}

/* ---------- CTA / 页脚 ---------- */
.cta-band {
  text-align: center;
  padding: 5rem 1.5rem;
}

.cta-band h2 {
  font-size: 1.8rem;
  letter-spacing: -0.02em;
  margin: 0 0 1.5rem;
}

.landing-footer {
  border-top: 1px solid var(--color-sand);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  max-width: 1120px;
  margin: 0 auto;
  font-size: 0.8rem;
  color: var(--color-mahogany);
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .hero {
    padding-top: 3.5rem;
  }

  .privacy-card {
    flex-direction: column;
  }
}
</style>
