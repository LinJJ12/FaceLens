<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEmotionStore } from './stores/emotion'
import { useUserStore } from './stores/user'

const emotionStore = useEmotionStore()
const userStore = useUserStore()

onMounted(() => {
  // 初始化用户状态
  userStore.initializeUser()
  
  // 初始化主题设置
  const userSettings = JSON.parse(localStorage.getItem('userSettings') || '{}')
  const savedTheme = localStorage.getItem('theme')
  
  if (userSettings && userSettings.theme) {
    if (userSettings.theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (userSettings.theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      document.documentElement.classList.toggle('dark', prefersDark)
    }
  } else if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
  }
  
  // 检查后端服务健康状态
  emotionStore.checkHealth()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
    'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: var(--color-parchment);
  min-height: 100vh;
  color: var(--color-ink);
}

#app {
  min-height: 100vh;
  background: var(--color-parchment);
}

/* 调整 Element Plus 消息提示位置，避免遮挡导航栏和按钮 */
:deep(.el-message) {
  top: 100px !important;
  z-index: 9999 !important;
}

/* 确保消息提示在所有元素之上，但位置下移 */
.el-message {
  top: 100px !important;
}

/* 全局深色模式样式（令牌自动翻转，无需单独设置背景） */

/* Element Plus 暗色微调：统一为 zinc 暗色面板 */
.dark .el-card {
  background-color: var(--color-surface);
  border-color: var(--color-sand);
  color: var(--color-ink);
}

.dark .el-card__header {
  border-bottom: 1px solid var(--color-sand);
  color: var(--color-ink);
}

.dark .el-dialog,
.dark .el-message-box,
.dark .el-notification {
  background-color: #1c1c1f;
  border-color: var(--color-sand);
}

.dark .el-dialog__title,
.dark .el-message-box__title {
  color: var(--color-ink);
}

.dark .el-button--primary {
  --el-button-text-color: #fafafa;
  --el-button-hover-text-color: #fafafa;
}

.dark .el-table {
  --el-table-bg-color: var(--color-surface);
  --el-table-tr-bg-color: var(--color-surface);
  --el-table-header-bg-color: #1d1d21;
  --el-table-row-hover-bg-color: #232327;
  --el-table-border-color: var(--color-sand);
  --el-table-text-color: var(--color-ink);
  --el-table-header-text-color: var(--color-mahogany);
}

.dark .el-tag {
  --el-tag-bg-color: #232327;
  --el-tag-border-color: var(--color-sand);
  --el-tag-text-color: var(--color-ink);
}

.dark .el-descriptions {
  --el-descriptions-item-bordered-label-background: #1d1d21;
}

/* 全局卡片样式 */
.el-card {
  border-radius: 0.625rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  border: 1px solid var(--color-sand);
}

.el-card:hover {
  box-shadow: var(--shadow-md);
}

/* 主题切换动画 - 只应用于主要UI元素，避免性能问题 */
body, #app, .el-card, .el-input__wrapper, .el-select__wrapper, .el-dropdown-menu, .el-dialog, .el-button, .el-table {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
</style>
