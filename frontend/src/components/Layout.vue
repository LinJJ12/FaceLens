<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <el-button
            class="sidebar-toggle"
            text
            @click="toggleSidebar"
          >
            <el-icon :size="20"><operation /></el-icon>
          </el-button>
          <img class="logo-icon" src="@/assets/brand/logo.png" alt="情绪识别系统" />
          <span class="logo-text">情绪识别系统</span>
        </div>
        
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" exact-active-class="router-link-active">
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
          <el-badge :value="emotionStore.predictions.length" class="notification-badge">
            <el-button circle>
              <el-icon><bell /></el-icon>
            </el-button>
          </el-badge>
          
          <!-- 用户信息下拉菜单 -->
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.userInfo?.avatar">
                <el-icon><user /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
              <el-icon><arrow-down /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><user /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><setting /></el-icon>
                  账户设置
                </el-dropdown-item>
                <el-dropdown-item command="help" divided>
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
          <h4>关于系统</h4>
          <p>基于 RAF-DB 数据集与深度学习的人脸情绪识别系统</p>
          <p>支持 7 种基本情绪的分类识别</p>
        </div>
        <div class="footer-section">
          <h4>快速链接</h4>
          <router-link to="/about">关于系统</router-link>
          <router-link to="/user">个人中心</router-link>
          <a href="#" @click.prevent="showPrivacy">隐私政策</a>
        </div>
        <div class="footer-section">
          <h4>开源仓库</h4>
          <a href="https://github.com/LinJJ12/RAF-DB-Based-Facial-Emotion-Recognition-System" target="_blank" rel="noopener">GitHub 项目主页</a>
          <a href="https://github.com/LinJJ12/RAF-DB-Based-Facial-Emotion-Recognition-System/issues" target="_blank" rel="noopener">提交 Issue</a>
        </div>
        <div class="footer-section">
          <h4>技术栈</h4>
          <p>Vue 3 + Element Plus</p>
          <p>Flask + TensorFlow</p>
          <p>CNN + VGG16 + SE-Net</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>人脸情绪识别系统 · 仅供学习与研究使用，不构成医学或心理诊断建议</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEmotionStore } from '../stores/emotion'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
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
  Tools,
  VideoCamera,
  Camera,
  Operation
} from '@element-plus/icons-vue'

const router = useRouter()
const emotionStore = useEmotionStore()
const userStore = useUserStore()
const isDark = ref(false)
const sidebarExpanded = ref(true)

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
  if (value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
    // 更新User.vue中的settings
    const userSettings = JSON.parse(localStorage.getItem('userSettings') || '{}')
    if (userSettings) {
      userSettings.theme = 'dark'
      localStorage.setItem('userSettings', JSON.stringify(userSettings))
    }
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
    // 更新User.vue中的settings
    const userSettings = JSON.parse(localStorage.getItem('userSettings') || '{}')
    if (userSettings) {
      userSettings.theme = 'light'
      localStorage.setItem('userSettings', JSON.stringify(userSettings))
    }
  }
}

const showPrivacy = () => {
  ElMessage.info('隐私政策页面开发中...')
}

// 处理用户下拉菜单命令
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/user')
      break
    case 'settings':
      router.push('/user')
      break
    case 'help':
      ElMessage.info('帮助中心页面开发中...')
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
      
      // 移除之前可能存在的监听器
      if (layoutThemeListener) {
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', layoutThemeListener)
      }
      
      // 创建并添加新的监听器
      layoutThemeListener = (e) => {
        // 重新获取最新的userSettings，确保使用最新的主题设置
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
  background: #F6F7FB;
  background-attachment: fixed;
}

/* 顶部导航 */
.header {
  background: rgba(246, 247, 251, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(26, 36, 86, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid #E2E8F0;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1A2456;
  font-family: inherit;
}

.sidebar-toggle {
  color: #1A2456;
  font-size: 1.2rem;
  padding: 0.5rem;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  object-fit: cover;
  display: block;
  flex-shrink: 0;
}

.nav-menu {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  text-decoration: none;
  color: #1A2456;
  font-weight: 500;
  transition: all 0.3s;
  position: relative;
}

.nav-item:hover {
  background: rgba(26, 36, 86, 0.1);
  color: #4F46E5;
}

.nav-item.router-link-active {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: white;
  box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.35), 0 8px 10px -6px rgba(79, 70, 229, 0.2);
}

.admin-nav {
  background: #4F46E5;
  color: white;
  border: 1px solid #4F46E5;
}

.admin-nav:hover {
  background: rgba(79, 70, 229, 0.9);
  color: white;
}

.admin-nav.router-link-active {
  background: #4338CA;
  color: white;
  box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.3);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-badge {
  cursor: pointer;
}

/* 用户下拉菜单样式 */
.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(102, 126, 234, 0.1);
}

.username {
  font-weight: 500;
  color: #1A2456;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  left: 0;
  top: 70px;
  bottom: 0;
  width: 240px;
  background: rgba(246, 247, 251, 0.98);
  backdrop-filter: blur(10px);
  box-shadow: 2px 0 12px rgba(26, 36, 86, 0.08);
  transition: all 0.3s ease;
  z-index: 999;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #E2E8F0;
}

.sidebar.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 1.5rem 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1A2456;
  border-bottom: 1px solid #E2E8F0;
  text-align: center;
  font-family: inherit;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: #1A2456;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.sidebar-collapsed .sidebar-item {
  justify-content: center;
  padding: 0.875rem;
}

.sidebar-collapsed .sidebar-item span {
  display: none;
}

.sidebar-item:hover {
  background: rgba(26, 36, 86, 0.1);
  color: #4F46E5;
  transform: translateY(-2px);
}

.sidebar-item.router-link-active {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: white;
  box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.28);
}

.sidebar-item .el-icon {
  font-size: 1.25rem;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 2rem 0 4rem 0;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  min-height: calc(100vh - 70px);
}

.main-content.sidebar-collapsed {
  margin-left: 64px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem 2rem;
}

/* 底部 */
.footer {
  background: rgba(246, 247, 251, 0.98);
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  backdrop-filter: blur(10px);
  margin-top: 4rem;
  padding: 3rem 0 1rem;
  border-top: 1px solid #E2E8F0;
}

.footer.sidebar-collapsed {
  margin-left: 64px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h4 {
  color: #1A2456;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-family: inherit;
}

.footer-section p,
.footer-section a {
  color: rgba(26, 36, 86, 0.7);
  margin: 0.5rem 0;
  text-decoration: none;
  display: block;
  transition: color 0.3s;
}

.footer-section a:hover {
  color: #4F46E5;
}

.footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid #E2E8F0;
  color: rgba(26, 36, 86, 0.6);
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
    padding: 0.875rem;
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
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  
  .header-content {
    padding: 0 1rem;
  }
  
  .content-wrapper {
    padding: 0 1rem 2rem 1rem;
  }
  
  .sidebar {
    width: 0;
    overflow: hidden;
  }
  
  .sidebar.sidebar-expanded-mobile {
    width: 240px;
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
}
</style>
