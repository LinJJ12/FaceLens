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
  background: #F6F7FB;
  min-height: 100vh;
  color: #1A2456;
}

#app {
  min-height: 100vh;
  background: #F6F7FB;
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

/* 全局深色模式样式 */
.dark body {
  background: #1A2456;
  color: #F6F7FB;
}

.dark #app {
  background: #1A2456;
}

/* Element Plus 全局深色模式样式 */
.dark .el-card {
  background-color: #243566;
  border-color: #334155;
  color: #F6F7FB;
}

.dark .el-card__header {
  background-color: #333333;
  border-bottom: 1px solid #404040;
  color: #e0e0e0;
}

.dark .el-card__body {
  color: #e0e0e0;
}

.dark .el-input__wrapper {
  background-color: #333333;
  border-color: #404040;
}

.dark .el-input__inner {
  color: #e0e0e0;
}

.dark .el-input__placeholder {
  color: #909399;
}

.dark .el-switch__core {
  background-color: #555555;
}

.dark .el-switch__core.is-checked {
  background-color: #6366F1;
}

.dark .el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background-color: #6366F1;
  border-color: #6366F1;
}

.dark .el-select {
  color: #e0e0e0;
}

.dark .el-select__wrapper {
  background-color: #333333;
  border-color: #404040;
}

.dark .el-select__placeholder {
  color: #909399;
}

.dark .el-select__popper {
  background-color: #2c2c2c;
  border-color: #404040;
  color: #e0e0e0;
}

.dark .el-select__option {
  color: #e0e0e0;
}

.dark .el-select__option:hover {
  background-color: #333333;
}

.dark .el-select__option.is-selected {
  background-color: #6366F1;
  color: white;
}

.dark .el-dropdown-menu {
  background-color: #2c2c2c;
  border-color: #404040;
}

.dark .el-dropdown-menu__item {
  color: #e0e0e0;
}

.dark .el-dropdown-menu__item:hover {
  background-color: #333333;
}

.dark .el-dialog {
  background-color: #2c2c2c;
  border-color: #404040;
}

.dark .el-dialog__header {
  background-color: #333333;
  border-bottom: 1px solid #404040;
}

.dark .el-dialog__title {
  color: #e0e0e0;
}

.dark .el-button {
  transition: all 0.3s ease;
}

.dark .el-button--primary {
  background-color: #6366F1;
  border-color: #6366F1;
}

.dark .el-button--primary:hover {
  background-color: #818CF8;
  border-color: #818CF8;
}

/* 全局卡片样式 */
.el-card {
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
  border: 1px solid #E2E8F0;
}

.el-card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

/* 全局按钮样式：语义色交由 Element Plus 主题变量与默认色处理 */

.dark .el-form-item__label {
  color: #e0e0e0;
}

.dark .el-divider {
  background-color: #404040;
}

.dark .el-divider__text {
  color: #e0e0e0;
  background-color: #1a1a1a;
}

.dark .el-progress__text {
  color: #e0e0e0;
}

.dark .el-progress-bar__outer {
  background-color: #404040;
}

.dark .el-alert {
  background-color: #2c2c2c;
  border-color: #404040;
}

.dark .el-alert--warning {
  background-color: #2c2c2c;
  border-color: #e6a23c;
  color: #f56c6c;
}

.dark .el-table {
  background-color: #2c2c2c;
}

.dark .el-table thead {
  background-color: #333333;
}

.dark .el-table th {
  color: #e0e0e0;
  border-bottom: 1px solid #404040;
}

.dark .el-table td {
  color: #e0e0e0;
  border-bottom: 1px solid #404040;
}

.dark .el-table__empty-block {
  color: #909399;
}

.dark .el-pagination button {
  color: #e0e0e0;
  background-color: #2c2c2c;
  border-color: #404040;
}

.dark .el-pagination__sizes .el-input .el-input__wrapper {
  background-color: #2c2c2c;
  border-color: #404040;
}

.dark .el-pagination__sizes .el-input__inner {
  color: #e0e0e0;
}

.dark .el-pagination__total {
  color: #e0e0e0;
}

.dark .el-tag {
  background-color: #333333;
  border-color: #404040;
  color: #e0e0e0;
}

/* 主题切换动画 - 只应用于主要UI元素，避免性能问题 */
body, #app, .el-card, .el-input__wrapper, .el-select__wrapper, .el-dropdown-menu, .el-dialog, .el-button, .el-table {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
</style>
