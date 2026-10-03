<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-pattern"></div>
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-orb orb-3"></div>
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <!-- 主登录卡片 -->
    <div class="login-card">
      <!-- 头部 -->
      <div class="login-header">
        <div class="logo">
          <h1 class="wordmark">FaceLens</h1>
        </div>
        <p class="subtitle">欢迎回来，请登录您的账户</p>
      </div>

      <!-- 登录表单 -->
      <div class="login-form" v-if="!isRegisterMode">
        <el-form 
          :model="loginForm" 
          :rules="loginRules" 
          ref="loginFormRef"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名或邮箱"
              size="large"
              prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <el-link type="primary" @click="forgotPassword">忘记密码？</el-link>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="loginLoading"
              @click="handleLogin"
              class="login-btn"
            >
              {{ loginLoading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 注册链接 -->
        <div class="register-link">
          <span>还没有账户？</span>
          <el-link type="primary" @click="switchToRegister">立即注册</el-link>
        </div>
      </div>

      <!-- 注册表单 -->
      <div class="register-form" v-if="isRegisterMode">
        <el-form 
          :model="registerForm" 
          :rules="registerRules" 
          ref="registerFormRef"
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              size="large"
              prefix-icon="Message"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              size="large"
              prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-form-item prop="agreeTerms">
            <el-checkbox v-model="registerForm.agreeTerms">
              我已阅读并同意
              <el-link type="primary" @click="showTerms">《用户协议》</el-link>
              和
              <el-link type="primary" @click="showPrivacy">《隐私政策》</el-link>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="registerLoading"
              @click="handleRegister"
              class="register-btn"
            >
              {{ registerLoading ? '注册中...' : '注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 登录链接 -->
        <div class="login-link">
          <span>已有账户？</span>
          <el-link type="primary" @click="switchToLogin">立即登录</el-link>
        </div>
      </div>

      <!-- 忘记密码表单 -->
      <div class="forgot-form" v-if="isForgotMode">
        <h3>重置密码</h3>
        <p class="forgot-desc">请输入您的邮箱地址，我们将发送重置密码的链接给您</p>
        
        <el-form 
          :model="forgotForm" 
          :rules="forgotRules" 
          ref="forgotFormRef"
          @submit.prevent="handleForgotPassword"
        >
          <el-form-item prop="email">
            <el-input
              v-model="forgotForm.email"
              placeholder="请输入邮箱"
              size="large"
              prefix-icon="Message"
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="forgotLoading"
              @click="handleForgotPassword"
              class="forgot-btn"
            >
              {{ forgotLoading ? '发送中...' : '发送重置链接' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="back-to-login">
          <el-link type="primary" @click="switchToLogin">返回登录</el-link>
        </div>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="login-footer">
      <p>&copy; 2026 FaceLens. All rights reserved.</p>
      <div class="footer-links">
        <el-link type="info" @click="showTerms">用户协议</el-link>
        <el-link type="info" @click="showPrivacy">隐私政策</el-link>
        <el-link type="info" @click="showHelp">帮助中心</el-link>
      </div>
    </div>

    <!-- 用户协议对话框 -->
    <el-dialog v-model="termsDialog" title="用户协议" width="70%" max-height="80vh">
      <div class="terms-content">
        <h3>1. 服务条款</h3>
        <p>欢迎使用 FaceLens。本系统基于深度学习技术，提供人脸情绪识别服务。</p>
        
        <h3>2. 用户责任</h3>
        <p>用户应确保上传的图片符合相关法律法规，不得上传违法违规内容。</p>
        
        <h3>3. 隐私保护</h3>
        <p>我们承诺保护用户隐私，上传的图片仅用于情绪识别分析，不会用于其他用途。</p>
        
        <h3>4. 服务限制</h3>
        <p>本服务仅供学习和研究使用，不得用于商业用途。</p>
        
        <h3>5. 免责声明</h3>
        <p>本系统提供的识别结果仅供参考，不构成任何医学或心理诊断建议。</p>
      </div>
    </el-dialog>

    <!-- 隐私政策对话框 -->
    <el-dialog v-model="privacyDialog" title="隐私政策" width="70%" max-height="80vh">
      <div class="privacy-content">
        <h3>1. 信息收集</h3>
        <p>我们仅收集用户上传的图片用于情绪识别分析，不收集其他个人信息。</p>
        
        <h3>2. 信息使用</h3>
        <p>收集的图片仅用于提供情绪识别服务，不会用于其他目的。</p>
        
        <h3>3. 信息存储</h3>
        <p>用户数据采用加密存储，确保数据安全。</p>
        
        <h3>4. 信息共享</h3>
        <p>我们不会与第三方分享用户的个人信息。</p>
        
        <h3>5. 用户权利</h3>
        <p>用户有权要求删除个人数据，或查看我们收集的数据。</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单模式
const isRegisterMode = ref(false)
const isForgotMode = ref(false)

// 表单引用
const loginFormRef = ref()
const registerFormRef = ref()
const forgotFormRef = ref()

// 加载状态
const loginLoading = ref(false)
const registerLoading = ref(false)
const forgotLoading = ref(false)

// 其他状态
const rememberMe = ref(false)

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// 忘记密码表单
const forgotForm = reactive({
  email: ''
})

// 对话框状态
const termsDialog = ref(false)
const privacyDialog = ref(false)

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, message: '密码必须包含大小写字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  agreeTerms: [
    { required: true, message: '请同意用户协议和隐私政策', trigger: 'change' }
  ]
}

const forgotRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 切换表单模式
const switchToRegister = () => {
  isRegisterMode.value = true
  isForgotMode.value = false
  resetForms()
}

const switchToLogin = () => {
  isRegisterMode.value = false
  isForgotMode.value = false
  resetForms()
}

const forgotPassword = () => {
  isForgotMode.value = true
  isRegisterMode.value = false
  resetForms()
}

// 重置表单
const resetForms = () => {
  loginFormRef.value?.resetFields()
  registerFormRef.value?.resetFields()
  forgotFormRef.value?.resetFields()
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loginLoading.value = true
    
    // 使用用户store进行登录
    const result = await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
      remember: rememberMe.value
    })
    
    if (result.success) {
      // 记住我：保存用户名便于下次登录
      if (rememberMe.value) {
        localStorage.setItem('rememberedUsername', loginForm.username)
      } else {
        localStorage.removeItem('rememberedUsername')
      }
      // 跳转到首页或重定向页面
      const redirect = router.currentRoute.value.query.redirect || '/'
      router.push(redirect)
    }
    
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loginLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    registerLoading.value = true
    
    // 使用用户store进行注册
    const result = await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password
    })
    
    if (result.success) {
      switchToLogin()
    }
    
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    registerLoading.value = false
  }
}

// 处理忘记密码
const handleForgotPassword = async () => {
  if (!forgotFormRef.value) return
  
  try {
    await forgotFormRef.value.validate()
    forgotLoading.value = true
    
    // 使用用户store发送重置密码邮件
    const result = await userStore.forgotPassword(forgotForm.email)
    
    if (result.success) {
      switchToLogin()
    }
    
  } catch (error) {
    console.error('发送重置邮件失败:', error)
  } finally {
    forgotLoading.value = false
  }
}

// 显示用户协议
const showTerms = () => {
  termsDialog.value = true
}

// 显示隐私政策
const showPrivacy = () => {
  privacyDialog.value = true
}

// 显示帮助中心
const showHelp = () => {
  router.push('/help')
}

// 组件挂载时的处理
onMounted(() => {
  // 检查是否已登录
  if (userStore.isLoggedIn) {
    router.push('/')
  }

  // "记住我"：回填上次登录的用户名
  const remembered = localStorage.getItem('rememberedUsername')
  if (remembered) {
    loginForm.username = remembered
    rememberMe.value = true
  }

  // 检查路由参数（hash 模式下参数位于 route.query），决定初始模式
  const mode = router.currentRoute.value.query.mode
  if (mode === 'register') {
    switchToRegister()
  } else if (mode === 'forgot') {
    forgotPassword()
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-parchment) 0%, var(--el-color-primary-light-9) 50%, var(--color-parchment) 100%);
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* 背景图案：细网格 + 品牌色渐变晕染 */
.bg-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(24, 24, 27, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(24, 24, 27, 0.035) 1px, transparent 1px),
    radial-gradient(circle at 18% 22%, rgba(24, 24, 27, 0.10) 0%, transparent 45%),
    radial-gradient(circle at 82% 76%, rgba(24, 24, 27, 0.10) 0%, transparent 45%);
  background-size: 44px 44px, 44px 44px, 100% 100%, 100% 100%;
}

/* 品牌色光斑 */
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.5;
  will-change: transform;
}

.orb-1 {
  width: 420px;
  height: 420px;
  background: var(--color-sand);
  top: -140px;
  left: -110px;
  animation: orbDrift 16s ease-in-out infinite;
}

.orb-2 {
  width: 360px;
  height: 360px;
  background: var(--color-sand);
  bottom: -140px;
  right: -100px;
  animation: orbDrift 19s ease-in-out infinite reverse;
}

.orb-3 {
  width: 240px;
  height: 240px;
  background: var(--el-color-primary-light-9);
  top: 42%;
  right: 14%;
  opacity: 0.4;
  animation: orbDrift 22s ease-in-out infinite;
}

@keyframes orbDrift {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(24px, -18px);
  }
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(24, 24, 27, 0.05);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 89px;
  height: 89px;
  top: 23.6%;
  left: 8%;
  animation-delay: 0s;
}

.shape-2 {
  width: 55px;
  height: 55px;
  top: 61.8%;
  left: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 89px;
  height: 89px;
  top: 23.6%;
  right: 8%;
  animation-delay: 1s;
}

.shape-4 {
  width: 55px;
  height: 55px;
  top: 61.8%;
  right: 15%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 登录卡片 */
.login-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
  border: 1px solid var(--color-sand);
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 头部 */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.wordmark {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0;
  color: var(--color-ink);
}

.subtitle {
  color: var(--color-mahogany);
  font-size: 1rem;
  margin: 0;
}

/* 表单样式 */
.login-form,
.register-form,
.forgot-form {
  width: 100%;
}

.login-form .el-form-item,
.register-form .el-form-item,
.forgot-form .el-form-item {
  margin-bottom: 1.5rem;
}

.login-form .el-input,
.register-form .el-input,
.forgot-form .el-input {
  height: 50px;
}

.login-form .el-input__wrapper,
.register-form .el-input__wrapper,
.forgot-form .el-input__wrapper {
  border-radius: 12px;
  box-shadow: none;
  border: 1px solid var(--color-sand);
  transition: all 0.3s ease;
}

.login-form .el-input__wrapper:hover,
.register-form .el-input__wrapper:hover,
.forgot-form .el-input__wrapper:hover {
  border-color: var(--color-ink);
  box-shadow: 0 4px 12px rgba(24, 24, 27, 0.12);
}

.login-form .el-input__wrapper.is-focus,
.register-form .el-input__wrapper.is-focus,
.forgot-form .el-input__wrapper.is-focus {
  border-color: var(--color-ink);
  box-shadow: 0 0 0 2px rgba(24, 24, 27, 0.16);
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* 按钮样式 */
.login-btn,
.register-btn,
.forgot-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  background: var(--el-color-primary, var(--color-accent));
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover,
.register-btn:hover,
.forgot-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 24, 27, 0.22);
}

/* 链接样式 */
.register-link,
.login-link {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--color-mahogany);
}

.register-link span,
.login-link span {
  margin-right: 0.5rem;
}

/* 忘记密码样式 */
.forgot-form h3 {
  text-align: center;
  color: var(--color-ink);
  margin-bottom: 0.5rem;
}

.forgot-desc {
  text-align: center;
  color: var(--color-mahogany);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.back-to-login {
  text-align: center;
  margin-top: 1.5rem;
}

/* 底部信息 */
.login-footer {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  color: var(--color-mahogany);
  z-index: 1;
}

.login-footer p {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

/* 对话框内容 */
.terms-content,
.privacy-content {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 1rem;
}

.terms-content h3,
.privacy-content h3 {
  color: var(--color-ink);
  margin: 1.5rem 0 0.75rem 0;
  font-size: 1.1rem;
}

.terms-content p,
.privacy-content p {
  color: var(--color-mahogany);
  line-height: 1.6;
  margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 1rem;
  }
  
  .login-card {
    padding: 2rem;
    margin: 1rem;
  }
  
  .wordmark {
    font-size: 1.5rem;
  }

  .footer-links {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* 深色模式支持 */
.dark .login-card {
  background: rgba(44, 44, 44, 0.95);
  color: #e0e0e0;
}

.dark .wordmark {
  color: #e0e0e0;
}

.dark .subtitle {
  color: #b0b0b0;
}

.dark .el-input__wrapper {
  background-color: #333;
  border-color: #404040;
  color: #e0e0e0;
}

.dark .el-input__inner {
  color: #e0e0e0;
}

.dark .el-input__placeholder {
  color: var(--color-mahogany);
}

.dark .register-link,
.dark .login-link,
.dark .back-to-login {
  color: #b0b0b0;
}

.dark .login-footer {
  color: rgba(226, 232, 240, 0.55);
}

.dark .bg-pattern {
  background-image:
    linear-gradient(rgba(129, 140, 248, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(129, 140, 248, 0.05) 1px, transparent 1px),
    radial-gradient(circle at 18% 22%, rgba(24, 24, 27, 0.16) 0%, transparent 45%),
    radial-gradient(circle at 82% 76%, rgba(24, 24, 27, 0.16) 0%, transparent 45%);
  background-size: 44px 44px, 44px 44px, 100% 100%, 100% 100%;
}

.dark .terms-content h3,
.dark .privacy-content h3 {
  color: #e0e0e0;
}

.dark .terms-content p,
.dark .privacy-content p {
  color: #b0b0b0;
}

/* 动画效果 */
.login-card {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 表单验证样式 */
:deep(.el-form-item__error) {
  color: #f56c6c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

:deep(.el-form-item.is-error .el-input__wrapper) {
  border-color: #f56c6c;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2);
}

/* 加载状态样式 */
:deep(.el-button.is-loading) {
  pointer-events: none;
}

/* 复选框样式 */
:deep(.el-checkbox__label) {
  color: var(--color-mahogany);
  font-size: 0.9rem;
}

.dark :deep(.el-checkbox__label) {
  color: #b0b0b0;
}

/* 分割线样式 */
:deep(.el-divider__text) {
  background: rgba(255, 255, 255, 0.95);
  color: var(--color-mahogany);
  font-size: 0.9rem;
}

.dark :deep(.el-divider__text) {
  background: rgba(44, 44, 44, 0.95);
  color: var(--color-mahogany);
}
</style>
