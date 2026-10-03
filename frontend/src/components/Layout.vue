<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="brand">
          <el-button class="sidebar-toggle" text @click="toggleSidebar">
            <el-icon :size="20"><operation /></el-icon>
          </el-button>
          <router-link to="/home" class="wordmark">FaceLens</router-link>
          <span class="brand-tag">人脸情绪识别</span>
        </div>

        <nav class="nav-menu">
          <router-link to="/home" class="nav-item" exact-active-class="router-link-active">
            <el-icon><home-filled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/data-analysis" class="nav-item" exact-active-class="router-link-active">
            <el-icon><data-analysis /></el-icon>
            <span>数据分析</span>
          </router-link>
          <router-link to="/health" class="nav-item" exact-active-class="router-link-active">
            <el-icon><medal /></el-icon>
            <span>心理健康</span>
          </router-link>
          <router-link to="/history" class="nav-item" exact-active-class="router-link-active">
            <el-icon><clock /></el-icon>
            <span>历史记录</span>
          </router-link>
          <router-link v-if="userStore.isAdmin" to="/admin" class="nav-item admin-nav" exact-active-class="router-link-active">
            <el-icon><setting /></el-icon>
            <span>管理</span>
          </router-link>
        </nav>

        <div class="header-actions">
          <el-switch
            v-model="isDark"
            inline-prompt
            active-icon="Moon"
            inactive-icon="Sunny"
            @change="toggleTheme"
          />

          <!-- 最近识别通知 -->
          <el-popover placement="bottom-end" :width="320" trigger="click" popper-class="bell-popper">
            <template #reference>
              <el-badge :value="emotionStore.predictions.length" :max="99" class="notification-badge">
                <el-button circle>
                  <el-icon><bell /></el-icon>
                </el-button>
              </el-badge>
            </template>
            <div class="bell-panel">
              <div class="bell-panel-header">
                <span>最近识别</span>
                <el-link type="primary" :underline="false" @click="goHistory">查看全部</el-link>
              </div>
              <template v-if="recentPredictions.length">
                <div v-for="item in recentPredictions" :key="item.id" class="bell-item">
                  <span class="bell-item-emoji">{{ emotionEmoji(item.emotion) }}</span>
                  <div class="bell-item-body">
                    <div class="bell-item-title">{{ item.emotion_cn || item.emotion }} · 置信度 {{ formatPercent(item.confidence) }}</div>
                    <div class="bell-item-time">{{ formatTime(item.timestamp) }}</div>
                  </div>
                </div>
              </template>
              <el-empty v-else description="暂无识别记录" :image-size="60" />
            </div>
          </el-popover>

          <!-- 用户信息下拉菜单 -->
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar :size="32" :src="avatarUrl">
                <el-icon><user /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
              <el-icon><arrow-down /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><user /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="help">
                  <el-icon><question-filled /></el-icon>
                  帮助中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><switch-button /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- 侧边栏 -->
    <aside :class="['sidebar', { 'sidebar-collapsed': !sidebarExpanded }]">
      <div class="sidebar-header">
        <span v-if="sidebarExpanded">智能分析</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/image-analysis" class="sidebar-item" exact-active-class="router-link-active" title="图片识别">
          <el-icon><camera /></el-icon>
          <span v-if="sidebarExpanded">图片识别</span>
        </router-link>
        <router-link to="/video" class="sidebar-item" exact-active-class="router-link-active" title="视频分析">
          <el-icon><video-camera /></el-icon>
          <span v-if="sidebarExpanded">视频分析</span>
        </router-link>
        <el-divider v-if="sidebarExpanded" />
        <router-link to="/user" class="sidebar-item" exact-active-class="router-link-active" title="个人中心">
          <el-icon><user /></el-icon>
          <span v-if="sidebarExpanded">个人中心</span>
        </router-link>
        <router-link to="/about" class="sidebar-item" exact-active-class="router-link-active" title="关于系统">
          <el-icon><info-filled /></el-icon>
          <span v-if="sidebarExpanded">关于系统</span>
        </router-link>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main :class="['main-content', { 'sidebar-collapsed': !sidebarExpanded }]">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>

    <!-- 底部 -->
    <footer :class="['footer', { 'sidebar-collapsed': !sidebarExpanded }]">
      <div class="footer-content">
        <div class="footer-section">
          <h4>FaceLens</h4>
          <p>基于 RAF-DB 数据集与深度学习的人脸情绪识别系统</p>
          <p>支持 7 种基本情绪的分类识别</p>
        </div>
        <div class="footer-section">
          <h4>快速链接</h4>
          <router-link to="/about">关于系统</router-link>
          <router-link to="/help">帮助中心</router-link>
          <a href="#" @click.prevent="showPrivacy">隐私政策</a>
        </div>
        <div class="footer-section">
          <h4>开源仓库</h4>
          <a href="https://github.com/LinJJ12/FaceLens" target="_blank" rel="noopener">GitHub 项目主页</a>
          <a href="https://github.com/LinJJ12/FaceLens/issues" target="_blank" rel="noopener">提交 Issue</a>
        </div>
        <div class="footer-section">
          <h4>技术栈</h4>
          <p>Vue 3 + Element Plus</p>
          <p>Flask + TensorFlow</p>
          <p>CNN + VGG16 + SE-Net</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>FaceLens · 仅供学习与研究使用，不构成医学或心理诊断建议</p>
      </div>
    </footer>

    <!-- 隐私政策对话框 -->
    <el-dialog v-model="privacyVisible" title="隐私政策" width="640px">
      <div class="privacy-content">
        <p><strong>最后更新：2026 年 10 月</strong></p>
        <p>我们非常重视您的隐私。使用 FaceLens（以下简称"本系统"）即表示您同意以下政策：</p>
        <h5>1. 数据收集</h5>
        <p>本系统仅收集为提供识别服务所必需的数据：您主动上传的图片/视频、由其产生的识别结果（情绪类别、置信度）以及账户基本信息（用户名、邮箱、头像）。</p>
        <h5>2. 数据用途</h5>
        <p>上传的人脸图像仅用于情绪识别推理与生成分析报告，识别结果用于向您展示历史记录、统计图表与心理健康建议。</p>
        <h5>3. 数据存储与删除</h5>
        <p>数据存储在您自建或自托管的数据库中，本系统不会将数据共享给任何第三方。您可以随时在"历史记录"或"个人中心"删除自己的识别记录，或联系管理员删除账户。</p>
        <h5>4. 敏感信息提示</h5>
        <p>人脸图像属于敏感个人信息，请仅在获得被拍摄者同意的前提下上传。请勿上传包含身份证、门牌号等其他敏感信息的图片。</p>
        <h5>5. 免责声明</h5>
        <p>本系统输出仅供学习与研究参考，不构成任何医学或心理诊断建议。如有需要，请咨询专业人士。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="privacyVisible = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEmotionStore } from '../stores/emotion'
import { useUserStore } from '../stores/user'
import { resolveAssetUrl } from '../utils/assets'
import { ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  DataAnalysis,
  Medal,
  Clock,
  User,
  InfoFilled,
  Bell,
  ArrowDown,
  Setting,
  QuestionFilled,
  SwitchButton,
  VideoCamera,
  Camera,
  Operation
} from '@element-plus/icons-vue'

const router = useRouter()
const emotionStore = useEmotionStore()
const userStore = useUserStore()
const isDark = ref(false)
const sidebarExpanded = ref(true)
const privacyVisible = ref(false)

const EMOJI_MAP = {
  happy: '😊', sad: '😢', angry: '😠', fear: '😨',
  surprised: '😲', disgust: '🤢', normal: '😐'
}

const recentPredictions = computed(() => (emotionStore.predictions || []).slice(0, 5))
const avatarUrl = computed(() => resolveAssetUrl(userStore.userInfo?.avatar))

const emotionEmoji = (emotion) => EMOJI_MAP[emotion] || '🙂'
const formatPercent = (value) => `${Math.round((Number(value) || 0) * 100)}%`
const formatTime = (ts) => {
  if (!ts) return ''
  const d = new Date(ts)
  if (Number.isNaN(d.getTime())) return String(ts)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const goHistory = () => router.push('/history')

const toggleSidebar = () => {
  sidebarExpanded.value = !sidebarExpanded.value
  localStorage.setItem('sidebarExpanded', sidebarExpanded.value)
}

// 初始化侧边栏状态
onMounted(() => {
  const savedSidebarState = localStorage.getItem('sidebarExpanded')
  if (savedSidebarState !== null) {
    sidebarExpanded.value = savedSidebarState === 'true'
  }
})

const toggleTheme = (value) => {
  const target = value ? 'dark' : 'light'
  document.documentElement.classList.toggle('dark', value)
  localStorage.setItem('theme', target)
  const userSettings = JSON.parse(localStorage.getItem('userSettings') || '{}')
  userSettings.theme = target
  localStorage.setItem('userSettings', JSON.stringify(userSettings))
}

const showPrivacy = () => {
  privacyVisible.value = true
}

// 处理用户下拉菜单命令
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/user')
      break
    case 'help':
      router.push('/help')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 处理登出
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '确认退出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await userStore.logout()
    router.push('/login')
  } catch (error) {
    // 用户取消登出
  }
}

// 保存Layout中的主题变化监听器引用
let layoutThemeListener = null

onMounted(() => {
  // 检查本地存储的主题设置
  const savedTheme = localStorage.getItem('theme')
  const userSettings = JSON.parse(localStorage.getItem('userSettings') || '{}')

  // 优先使用userSettings中的主题设置
  if (userSettings && userSettings.theme) {
    if (userSettings.theme === 'dark') {
      isDark.value = true
      document.documentElement.classList.add('dark')
    } else if (userSettings.theme === 'auto') {
      // 跟随系统主题
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      isDark.value = prefersDark
      document.documentElement.classList.toggle('dark', prefersDark)

      if (layoutThemeListener) {
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', layoutThemeListener)
      }

      layoutThemeListener = (e) => {
        const currentSettings = JSON.parse(localStorage.getItem('userSettings') || '{}')
        if (currentSettings && currentSettings.theme === 'auto') {
          isDark.value = e.matches
          document.documentElement.classList.toggle('dark', e.matches)
        }
      }
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', layoutThemeListener)
    }
  } else if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})

// 组件卸载时清理监听器
onUnmounted(() => {
  if (layoutThemeListener) {
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', layoutThemeListener)
    layoutThemeListener = null
  }
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-parchment);
}

/* 顶部导航 */
.header {
  background: color-mix(in srgb, var(--color-parchment) 88%, transparent);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid var(--color-sand);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.sidebar-toggle {
  color: var(--color-ink);
  padding: 0.5rem;
}

.wordmark {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--color-ink);
  text-decoration: none;
  line-height: 1;
}

.brand-tag {
  font-size: 0.75rem;
  color: var(--color-mahogany);
  border: 1px solid var(--color-sand);
  border-radius: 999px;
  padding: 0.125rem 0.625rem;
  line-height: 1.4;
  white-space: nowrap;
}

.nav-menu {
  display: flex;
  gap: 0.25rem;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--color-mahogany);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.nav-item:hover {
  background: var(--el-color-primary-light-9);
  color: var(--color-ink);
}

.nav-item.router-link-active {
  background: var(--color-accent);
  color: #fafafa;
}

.admin-nav {
  color: var(--color-ink);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.notification-badge {
  cursor: pointer;
}

/* 最近识别面板 */
.bell-panel {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.bell-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  font-size: 0.9rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-sand);
  margin-bottom: 0.25rem;
}

.bell-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.25rem;
  border-radius: 8px;
}

.bell-item:hover {
  background: var(--el-color-primary-light-9);
}

.bell-item-emoji {
  font-size: 1.25rem;
}

.bell-item-title {
  font-size: 0.85rem;
  color: var(--color-ink);
}

.bell-item-time {
  font-size: 0.75rem;
  color: var(--color-mahogany);
}

/* 用户下拉菜单样式 */
.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  border-radius: 8px;
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--el-color-primary-light-9);
}

.username {
  font-weight: 500;
  color: var(--color-ink);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  left: 0;
  top: 64px;
  bottom: 0;
  width: 232px;
  background: var(--color-parchment);
  transition: all var(--transition-base);
  z-index: 999;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-sand);
}

.sidebar.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 1.25rem 1rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-mahogany);
  text-align: left;
}

.sidebar-nav {
  flex: 1;
  padding: 0 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--color-mahogany);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.sidebar-collapsed .sidebar-item {
  justify-content: center;
  padding: 0.625rem;
}

.sidebar-collapsed .sidebar-item span {
  display: none;
}

.sidebar-item:hover {
  background: var(--el-color-primary-light-9);
  color: var(--color-ink);
}

.sidebar-item.router-link-active {
  background: var(--color-accent);
  color: #fafafa;
}

.sidebar-item .el-icon {
  font-size: 1.125rem;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 2rem 0 3rem;
  margin-left: 232px;
  transition: margin-left var(--transition-base);
  min-height: calc(100vh - 64px);
}

.main-content.sidebar-collapsed {
  margin-left: 64px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* 底部 */
.footer {
  background: var(--color-parchment);
  margin-left: 232px;
  transition: margin-left var(--transition-base);
  margin-top: 3rem;
  padding: 2.5rem 0 1.25rem;
  border-top: 1px solid var(--color-sand);
}

.footer.sidebar-collapsed {
  margin-left: 64px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.footer-section h4 {
  color: var(--color-ink);
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.footer-section p,
.footer-section a {
  color: var(--color-mahogany);
  margin: 0.375rem 0;
  font-size: 0.85rem;
  text-decoration: none;
  display: block;
  transition: color var(--transition-fast);
}

.footer-section a:hover {
  color: var(--color-ink);
}

.footer-bottom {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-sand);
  color: var(--color-mahogany);
  font-size: 0.8rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* 隐私政策 */
.privacy-content {
  max-height: 55vh;
  overflow-y: auto;
  padding-right: 0.5rem;
  line-height: 1.7;
  font-size: 0.9rem;
  color: var(--color-ink);
}

.privacy-content h5 {
  margin: 1rem 0 0.25rem;
  font-size: 0.925rem;
}

.privacy-content p {
  margin: 0.25rem 0;
  color: var(--color-mahogany);
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar {
    width: 64px;
  }

  .sidebar-header span {
    display: none;
  }

  .sidebar-item {
    justify-content: center;
    padding: 0.625rem;
  }

  .sidebar-item span {
    display: none;
  }

  .main-content {
    margin-left: 64px;
  }

  .footer {
    margin-left: 64px;
  }

  .brand-tag {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .header-content {
    padding: 0 1rem;
  }

  .content-wrapper {
    padding: 0 1rem;
  }

  .sidebar {
    width: 0;
    overflow: hidden;
  }

  .main-content {
    margin-left: 0;
  }

  .footer {
    margin-left: 0;
  }

  .footer-content {
    grid-template-columns: 1fr;
    padding: 0 1rem;
  }

  .username {
    display: none;
  }
}
</style>
