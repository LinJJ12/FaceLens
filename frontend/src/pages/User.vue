<template>
  <div class="user-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>个人中心</h1>
      <p>管理您的个人信息和偏好设置</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：用户信息卡片 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8">
        <el-card class="profile-card" shadow="hover">
          <div class="profile-header">
            <el-avatar :size="100" :src="displayAvatar" @click="viewAvatar" style="cursor: pointer;">
              <el-icon :size="50"><user-filled /></el-icon>
            </el-avatar>
            <el-upload
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :on-change="handleAvatarChange"
              accept="image/*"
              :auto-upload="false"
            >
              <el-button class="avatar-upload" size="small" circle>
                <el-icon><camera /></el-icon>
              </el-button>
            </el-upload>
          </div>
          
          <div class="profile-info">
            <h3>{{ userInfo.name }}</h3>
            <p class="user-email">{{ userInfo.email }}</p>
            <el-tag type="success">{{ userInfo.role }}</el-tag>
          </div>

          <el-divider />

          <div class="profile-stats">
            <div class="stat-item">
              <div class="stat-value">{{ totalRecognitions }}</div>
              <div class="stat-label">总识别次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ activeDays }}</div>
              <div class="stat-label">活跃天数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ memberDays }}</div>
              <div class="stat-label">会员天数</div>
            </div>
          </div>

          <el-divider />

          <div class="profile-actions">
            <el-button type="primary" @click="editProfileDialog = true" block>
              编辑资料
            </el-button>
            <el-button @click="changePasswordDialog = true" block>
              修改密码
            </el-button>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="quick-actions-card" shadow="hover">
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-upload
              class="upload-full-width"
              :show-file-list="false"
              :before-upload="beforeImportData"
              :on-change="handleImportData"
              accept=".json"
              :auto-upload="false"
            >
              <el-button class="action-btn">
                <el-icon><upload /></el-icon>
                <span>导入数据备份</span>
              </el-button>
            </el-upload>
            <el-button @click="exportAllData" class="action-btn">
              <el-icon><download /></el-icon>
              <span>导出所有数据</span>
            </el-button>
            <el-button @click="clearHistory" class="action-btn">
              <el-icon><delete /></el-icon>
              <span>清空历史记录</span>
            </el-button>
            <el-button @click="syncFromServer" class="action-btn" :loading="syncing">
              <el-icon><upload-filled /></el-icon>
              <span>从服务器同步</span>
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：设置 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="16">
        <!-- 成就系统 -->
        <el-card class="achievements-card" shadow="hover">
          <template #header>
            <div class="card-header-with-actions">
              <span>成就徽章</span>
              <el-tag type="success">{{ unlockedCount }}/{{ totalAchievements }}</el-tag>
            </div>
          </template>
          <div class="achievements-grid">
            <div
              v-for="achievement in achievements"
              :key="achievement.id"
              :class="['achievement-item', { unlocked: achievement.unlocked, locked: !achievement.unlocked }]"
              @click="showAchievementDetail(achievement)"
            >
              <div class="achievement-icon">{{ achievement.icon }}</div>
              <div class="achievement-info">
                <div class="achievement-name">{{ achievement.name }}</div>
                <div class="achievement-desc">{{ achievement.desc }}</div>
                <el-progress
                  v-if="!achievement.unlocked"
                  :percentage="getAchievementProgress(achievement)"
                  :stroke-width="6"
                  :show-text="false"
                />
                <div v-else class="achievement-unlocked">
                  已解锁 • {{ formatDate(achievement.unlockedAt) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 使用统计 -->
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <span>使用统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-box-icon" style="background: var(--el-color-primary-light-9)">
                  📅
                </div>
                <div class="stat-box-content">
                  <div class="stat-box-value">{{ consecutiveDays }}</div>
                  <div class="stat-box-label">连续使用天数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-box-icon" style="background: var(--el-color-primary-light-9)">

                </div>
                <div class="stat-box-content">
                  <div class="stat-box-value">{{ todayCount }}</div>
                  <div class="stat-box-label">今日识别次数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-box-icon" style="background: var(--el-color-primary-light-9)">
                  🎯
                </div>
                <div class="stat-box-content">
                  <div class="stat-box-value">{{ userLevel }}</div>
                  <div class="stat-box-label">当前等级</div>
                </div>
              </div>
            </el-col>
          </el-row>
          <el-divider />
          <div class="level-progress">
            <div class="level-info">
              <span>等级进度</span>
              <span>{{ experiencePoints }}/{{ nextLevelExp }} EXP</span>
            </div>
            <el-progress
              :percentage="levelProgress"
              :stroke-width="12"
              :color="getLevelColor()"
            >
              <template #default="{ percentage }">
                <span style="font-weight: bold">{{ percentage }}%</span>
              </template>
            </el-progress>
          </div>
        </el-card>

        <!-- 目标设定 -->
        <el-card class="goals-card" shadow="hover">
          <template #header>
            <div class="card-header-with-actions">
              <span>我的目标</span>
              <el-button size="small" @click="addGoalDialog = true">
                <el-icon><plus /></el-icon>
                添加目标
              </el-button>
            </div>
          </template>
          <div class="goals-list">
            <div v-for="goal in goals" :key="goal.id" class="goal-item">
              <div class="goal-header">
                <el-checkbox v-model="goal.completed" @change="toggleGoal(goal)">
                  {{ goal.title }}
                </el-checkbox>
                <el-button
                  size="small"
                  text
                  type="danger"
                  @click="deleteGoal(goal.id)"
                >
                  <el-icon><close /></el-icon>
                </el-button>
              </div>
              <div class="goal-progress">
                <el-progress
                  :percentage="getGoalProgress(goal)"
                  :status="goal.completed ? 'success' : ''"
                />
                <span class="goal-target">{{ goal.current }}/{{ goal.target }}</span>
              </div>
              <div class="goal-deadline">
                截止日期: {{ formatDate(goal.deadline) }}
              </div>
            </div>
            <el-empty v-if="goals.length === 0" description="还没有设定目标，快来添加吧！" :image-size="80" />
          </div>
        </el-card>

        <!-- 显示设置 -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <span>显示设置</span>
          </template>
          <el-form label-width="150px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="settings.theme" size="large">
                <el-radio-button label="light">浅色</el-radio-button>
                <el-radio-button label="dark">深色</el-radio-button>
                <el-radio-button label="auto">跟随系统</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="动画效果">
              <el-switch v-model="settings.animations" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 模型偏好 -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <span>模型偏好</span>
          </template>
          <el-form label-width="150px">
            <el-form-item label="默认模型">
              <el-select v-model="settings.defaultModel">
                <el-option v-for="opt in modelOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动人脸检测">
              <el-switch v-model="settings.autoFaceDetect" />
              <span class="form-item-tip">上传图片时自动进行人脸检测</span>
            </el-form-item>
            <el-form-item label="显示性能统计">
              <el-switch v-model="settings.showPerformance" />
            </el-form-item>
            <el-form-item label="显示质量评估">
              <el-switch v-model="settings.showQuality" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 保存按钮 -->
        <div class="save-actions">
          <el-button type="primary" size="large" @click="saveSettings">
            <el-icon><check /></el-icon>
            保存设置
          </el-button>
          <el-button size="large" @click="resetSettings">
            <el-icon><refresh /></el-icon>
            恢复默认
          </el-button>
        </div>
      </el-col>
    </el-row>

    <!-- 编辑资料对话框 -->
    <el-dialog v-model="editProfileDialog" title="编辑资料" width="500px">
      <el-form :model="userInfo" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.name" disabled />
          <div class="form-item-tip">用户名注册后不可修改</div>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userInfo.email" type="email" />
        </el-form-item>
        <el-form-item label="个性签名">
          <el-input v-model="userInfo.bio" type="textarea" :rows="3" placeholder="仅保存在本机" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProfileDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="changePasswordDialog" title="修改密码" width="500px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 添加目标对话框 -->
    <el-dialog v-model="addGoalDialog" title="添加目标" width="500px">
      <el-form :model="newGoal" label-width="100px">
        <el-form-item label="目标标题">
          <el-input v-model="newGoal.title" placeholder="例如：每周识别5次情绪" />
        </el-form-item>
        <el-form-item label="目标类型">
          <el-select v-model="newGoal.type" style="width: 100%">
            <el-option label="识别次数" value="count" />
            <el-option label="连续天数" value="days" />
            <el-option label="积极情绪占比" value="positive" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标数值">
          <el-input-number v-model="newGoal.target" :min="1" :max="365" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="newGoal.deadline"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            :disabledDate="(time) => time.getTime() < Date.now()"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addGoalDialog = false">取消</el-button>
        <el-button type="primary" @click="addGoal">添加</el-button>
      </template>
    </el-dialog>

    <!-- 头像裁剪对话框 -->
    <el-dialog v-model="avatarCropDialog" title="裁剪头像" width="600px">
      <div class="avatar-crop-container">
        <div class="crop-preview">
          <div class="avatar-crop-frame">
            <img 
              v-if="avatarPreview" 
              :src="avatarPreview" 
              ref="cropImage"
              @mousedown="startDrag"
              :style="{
                transform: `scale(${cropZoom}) translate(${cropPosition.x}px, ${cropPosition.y}px)`,
                cursor: isDragging ? 'grabbing' : 'grab',
                transition: isDragging ? 'none' : 'transform 0.1s ease'
              }"
              style="display: block;"
            />
          </div>
          <!-- 裁剪框指示 -->
          <div class="crop-mask">
            <div class="crop-indicator"></div>
          </div>
        </div>
        <div class="crop-controls">
          <el-slider v-model="cropZoom" :min="0.1" :max="3" :step="0.05" style="margin: 1rem 0">
            <template #label>
              缩放: {{ cropZoom.toFixed(2) }}x
            </template>
          </el-slider>
          <div class="crop-instructions">
            <el-icon><info-filled /></el-icon>
            拖动图片调整位置，使用滑块调整缩放比例
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="avatarCropDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAvatar">确认</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看头像大图对话框 -->
    <el-dialog v-model="viewAvatarDialog" title="查看头像" width="400px">
      <div class="avatar-view-container">
        <img :src="largeAvatarUrl" style="max-width: 100%; max-height: 400px; display: block; margin: 0 auto;" />
      </div>
      <template #footer>
        <el-button @click="viewAvatarDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 成就详情对话框 -->
    <el-dialog v-model="achievementDetailDialog" title="成就详情" width="500px">
      <div v-if="selectedAchievement" class="achievement-detail">
        <div class="achievement-detail-icon">{{ selectedAchievement.icon }}</div>
        <h3>{{ selectedAchievement.name }}</h3>
        <p class="achievement-detail-desc">{{ selectedAchievement.desc }}</p>
        <el-divider />
        <div class="achievement-detail-info">
          <div class="info-item">
            <span class="label">奖励经验:</span>
            <span class="value">{{ selectedAchievement.exp }} EXP</span>
          </div>
          <div class="info-item">
            <span class="label">解锁条件:</span>
            <span class="value">{{ selectedAchievement.condition }}</span>
          </div>
          <div v-if="!selectedAchievement.unlocked" class="info-item">
            <span class="label">完成进度:</span>
            <el-progress :percentage="getAchievementProgress(selectedAchievement)" />
          </div>
          <div v-else class="info-item">
            <span class="label">解锁时间:</span>
            <span class="value">{{ formatDateTime(selectedAchievement.unlockedAt) }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useEmotionStore } from '../stores/emotion'
import { useVideoStore } from '../stores/video'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { resolveAssetUrl } from '../utils/assets'
import api from '../api/client'
import {
  UserFilled,
  Camera,
  Download,
  Delete,
  Folder,
  Check,
  Refresh,
  Plus,
  Close,
  Upload,
  UploadFilled,
  InfoFilled
} from '@element-plus/icons-vue'

const emotionStore = useEmotionStore()
const videoStore = useVideoStore()
const userStore = useUserStore()

// 用于防止初始化时触发 watch 保存
const isInitialized = ref(false)

// 用户信息：以登录账户（userStore）为准，附加字段仅保存在本机
// 注意：本地资料存于独立的 userProfile 键，避免覆盖登录态的 userInfo
const loadUserInfo = () => {
  const saved = localStorage.getItem('userProfile')
  const server = userStore.userInfo || {}
  let local = {}
  if (saved) {
    try {
      local = JSON.parse(saved) || {}
    } catch (e) {
      console.warn('解析本地用户信息失败', e)
    }
  }
  return {
    name: server.username || local.name || '用户',
    email: server.email || local.email || '',
    bio: local.bio || '',
    avatar: server.avatar || local.avatar || '',
    role: server.role === 'admin' ? '管理员' : '普通用户',
    joinDate: server.created_at || local.joinDate || new Date().toISOString()
  }
}

// 用户信息
const userInfo = ref(loadUserInfo())

// 头像展示地址（兼容服务端相对路径与本地 base64）
const displayAvatar = computed(() => resolveAssetUrl(userInfo.value.avatar))

// 计算总识别次数（优先使用服务端统计）
const totalRecognitions = computed(() => {
  if (emotionStore.serverHistoriesTotal > 0) {
    return emotionStore.serverHistoriesTotal
  }
  return emotionStore.predictions.length + videoStore.videoHistory.length
})

// 计算活跃天数（含服务端记录）
const activeDays = computed(() => {
  const dates = new Set()
  const push = (ts) => {
    if (!ts) return
    const d = new Date(ts)
    if (!Number.isNaN(d.getTime())) dates.add(d.toDateString())
  }
  ;(emotionStore.serverHistories || []).forEach(r => push(r.created_at))
  emotionStore.predictions.forEach(pred => push(pred.timestamp))
  videoStore.videoHistory.forEach(video => push(video.timestamp))

  return dates.size
})

// 计算会员天数
const memberDays = computed(() => {
  const now = new Date()
  const join = new Date(userInfo.value.joinDate)
  const diff = now - join
  return Math.floor(diff / (1000 * 60 * 60 * 24))
})

// 从 localStorage 加载设置，如果没有则使用默认值
const loadSettings = () => {
  const saved = localStorage.getItem('userSettings')
  if (saved) {
    try {
      return JSON.parse(saved)
    } catch (e) {
      console.warn('解析设置失败，使用默认值')
    }
  }
  return {
    // 显示设置
    theme: 'light',
    animations: true,

    // 模型偏好
    defaultModel: 'cnn',
    autoFaceDetect: true,
    showPerformance: true,
    showQuality: true
  }
}

// 设置
const settings = ref(loadSettings())

// 模型选项：准确率从后端实时获取，失败时使用静态兜底
const modelOptions = ref([
  { label: 'CNN (83.77%)', value: 'cnn' },
  { label: 'VGG16 (80%)', value: 'vgg' },
  { label: 'SE-Net-81 (81%)', value: 'se81' },
  { label: 'SE-Net-83 (83%)', value: 'se83' }
])

async function loadModelOptions() {
  try {
    await emotionStore.fetchModels()
    const apiModels = emotionStore.availableModels
    if (Array.isArray(apiModels) && apiModels.length) {
      modelOptions.value = apiModels.map((m) => {
        const acc = typeof m.accuracy === 'number' && m.accuracy <= 1
          ? (m.accuracy * 100).toFixed(2)
          : m.accuracy
        return { label: `${m.display_name || m.name} (${acc}%)`, value: m.name }
      })
    }
  } catch (error) {
    // 保留静态兜底
  }
}

// 对话框
const editProfileDialog = ref(false)
const changePasswordDialog = ref(false)
const addGoalDialog = ref(false)
const achievementDetailDialog = ref(false)
const avatarCropDialog = ref(false)
const selectedAchievement = ref(null)

// 头像相关
const avatarPreview = ref('')
const cropZoom = ref(1)
const avatarFile = ref(null)
const cropPosition = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const viewAvatarDialog = ref(false)
const largeAvatarUrl = ref('')

// 密码表单
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 从 localStorage 加载成就，如果没有则使用默认值
const loadAchievements = () => {
  const saved = localStorage.getItem('achievements')
  if (saved) {
    try {
      return JSON.parse(saved)
    } catch (e) {
      console.warn('解析成就失败，使用默认值')
    }
  }
  return [
    {
      id: 1,
      name: '初次尝试',
      desc: '完成第一次情绪识别',
      icon: '🎯',
      exp: 10,
      condition: '完成1次识别',
      requirement: { type: 'count', value: 1 },
      unlocked: false,
      unlockedAt: null
    },
  {
    id: 2,
    name: '情绪探索者',
    desc: '累计识别10次情绪',
    icon: '🔍',
    exp: 50,
    condition: '完成10次识别',
    requirement: { type: 'count', value: 10 },
    unlocked: false,
    unlockedAt: null
  },
  {
    id: 3,
    name: '坚持不懈',
    desc: '连续使用7天',
    icon: '💪',
    exp: 100,
    condition: '连续使用7天',
    requirement: { type: 'consecutive', value: 7 },
    unlocked: false,
    unlockedAt: null
  },
  {
    id: 4,
    name: '情绪大师',
    desc: '累计识别50次情绪',
    icon: '🏆',
    exp: 200,
    condition: '完成50次识别',
    requirement: { type: 'count', value: 50 },
    unlocked: false,
    unlockedAt: null
  },
  {
    id: 5,
    name: '快乐使者',
    desc: '识别到10次高兴情绪',
    icon: '😊',
    exp: 80,
    condition: '识别10次高兴情绪',
    requirement: { type: 'emotion', emotion: 'happy', value: 10 },
    unlocked: false,
    unlockedAt: null
  },
  {
    id: 6,
    name: '数据分析师',
    desc: '导出分析报告5次',
    icon: '📊',
    exp: 150,
    condition: '导出5次报告',
    requirement: { type: 'export', value: 5 },
    unlocked: false,
    unlockedAt: null
  },
  {
    id: 7,
    name: '长期用户',
    desc: '使用系统30天',
    icon: '⭐',
    exp: 300,
    condition: '使用30天',
    requirement: { type: 'days', value: 30 },
    unlocked: false,
    unlockedAt: null
  },
  {
    id: 8,
    name: '情绪专家',
    desc: '累计识别100次情绪',
    icon: '👑',
    exp: 500,
    condition: '完成100次识别',
    requirement: { type: 'count', value: 100 },
    unlocked: false,
    unlockedAt: null
  }
  ]
}

// 成就系统
const achievements = ref(loadAchievements())

// 计算已解锁成就数量
const unlockedCount = computed(() => {
  return achievements.value.filter(a => a.unlocked).length
})

const totalAchievements = computed(() => achievements.value.length)

// 从 localStorage 加载经验值和导出次数
const loadExperiencePoints = () => {
  const saved = localStorage.getItem('experiencePoints')
  return saved ? parseInt(saved) || 0 : 0
}

const loadExportCount = () => {
  const saved = localStorage.getItem('exportCount')
  return saved ? parseInt(saved) || 0 : 0
}

// 经验值和等级系统
const experiencePoints = ref(loadExperiencePoints())
const exportCount = ref(loadExportCount()) // 导出次数

const userLevel = computed(() => {
  return Math.floor(experiencePoints.value / 100) + 1
})

const nextLevelExp = computed(() => {
  return userLevel.value * 100
})

const levelProgress = computed(() => {
  const currentLevelExp = experiencePoints.value % 100
  return Math.round((currentLevelExp / 100) * 100)
})

// 连续使用天数：从识别记录的真实时间戳计算（按自然日去重后取最大连续段）
const consecutiveDays = computed(() => {
  const days = new Set()
  const push = (ts) => {
    if (!ts) return
    const d = new Date(ts)
    if (!Number.isNaN(d.getTime())) days.add(d.toDateString())
  }
  ;(emotionStore.serverHistories || []).forEach(r => push(r.created_at))
  emotionStore.predictions.forEach(p => push(p.timestamp))
  videoStore.videoHistory.forEach(v => push(v.timestamp))

  if (days.size === 0) return 0

  const sorted = [...days]
    .map(str => new Date(str))
    .sort((a, b) => a - b)
  let best = 1
  let current = 1
  for (let i = 1; i < sorted.length; i++) {
    const diff = (sorted[i] - sorted[i - 1]) / (1000 * 60 * 60 * 24)
    current = Math.abs(diff - 1) < 1e-6 ? current + 1 : 1
    if (current > best) best = current
  }
  return best
})

// 今日识别次数（含服务端记录）
const todayCount = computed(() => {
  const today = new Date().toDateString()
  const count = (ts) => ts && new Date(ts).toDateString() === today ? 1 : 0
  let n = 0
  ;(emotionStore.serverHistories || []).forEach(r => { n += count(r.created_at) })
  emotionStore.predictions.forEach(pred => { n += count(pred.timestamp) })
  videoStore.videoHistory.forEach(v => { n += count(v.timestamp) })
  return n
})

// 从 localStorage 加载目标
const loadGoals = () => {
  const saved = localStorage.getItem('goals')
  if (saved) {
    try {
      return JSON.parse(saved)
    } catch (e) {
      console.warn('解析目标失败，使用默认值')
    }
  }
  return []
}

// 目标系统
const goals = ref(loadGoals())

const newGoal = ref({
  title: '',
  type: 'count',
  target: 10,
  current: 0,
  deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
  completed: false
})

// 保存设置 - 优化版本，避免UI阻塞
function saveSettings() {
  try {
    // 异步保存设置，避免阻塞UI
    setTimeout(() => {
      localStorage.setItem('userSettings', JSON.stringify(settings.value))
    }, 0)
    
    // 应用各种设置
    // 注意：applyTheme已经有防抖机制，所以这里直接调用没问题
    applyTheme(settings.value.theme)
    applyAnimations(settings.value.animations)
    applyLanguage("zh-CN")
    
    // 使用setTimeout确保消息在UI更新后显示
    setTimeout(() => {
      ElMessage.success('设置已保存')
    }, 0)
  } catch (error) {
    console.error('保存设置时出错:', error)
    ElMessage.error('保存设置失败，请重试')
  }
}

// 保存主题变化监听器的引用，避免重复添加
let themeChangeListener = null

// 应用主题设置 - 优化版本，避免频繁DOM操作
function applyTheme(theme) {
  try {
    // 使用防抖技术，避免短时间内多次调用
    if (window._themeTimeout) {
      clearTimeout(window._themeTimeout)
    }
    
    window._themeTimeout = setTimeout(() => {
      // 移除之前可能存在的监听器，防止内存泄漏
      if (themeChangeListener) {
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', themeChangeListener)
        themeChangeListener = null
      }
      
      // 仅当实际需要改变主题时才执行DOM操作
      const currentTheme = settings.value.theme
      let shouldBeDark = false
      
      if (currentTheme === 'auto') {
        shouldBeDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        
        // 创建并添加新的监听器
        themeChangeListener = (e) => {
          // 只有在当前主题仍然是auto时才响应系统变化
          if (settings.value.theme === 'auto') {
            document.documentElement.classList.toggle('dark', e.matches)
          }
        }
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeChangeListener)
      } else if (currentTheme === 'dark') {
        shouldBeDark = true
      }
      
      // 批量执行DOM操作
      if (shouldBeDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      
      // 异步保存设置，避免阻塞UI
      setTimeout(() => {
        localStorage.setItem('theme', currentTheme)
      }, 0)
    }, 100) // 100ms的防抖延迟
  } catch (error) {
    console.error('应用主题时出错:', error)
  }
}

// 应用动画设置
function applyAnimations(enable) {
  if (enable) {
    document.documentElement.classList.remove('no-animations')
    // 添加动画类
    document.body.classList.add('animate-fade')
    // 为所有卡片添加动画
    document.querySelectorAll('.el-card').forEach(card => {
      card.classList.add('card-hover-animation')
    })
  } else {
    document.documentElement.classList.add('no-animations')
    document.body.classList.remove('animate-fade')
    document.querySelectorAll('.el-card').forEach(card => {
      card.classList.remove('card-hover-animation')
    })
  }
  localStorage.setItem('animations', enable.toString())
}

// 应用语言设置（当前版本界面语言为简体中文，仅同步文档语言标记）
function applyLanguage(lang) {
  document.documentElement.lang = lang || 'zh-CN'
  localStorage.setItem('language', lang || 'zh-CN')
}

// 恢复默认设置
function resetSettings() {
  ElMessageBox.confirm('确定要恢复默认设置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    settings.value = {
      theme: 'light',
      animations: true,
      defaultModel: 'cnn',
      autoFaceDetect: true,
      showPerformance: true,
      showQuality: true
    }
    saveSettings()
  }).catch(() => {})
}

// 保存资料：邮箱同步到服务端，其余字段仅保存在本机
const savingProfile = ref(false)
async function saveProfile() {
  if (!userInfo.value.email) {
    ElMessage.warning('请填写邮箱')
    return
  }
  savingProfile.value = true
  try {
    const result = await userStore.updateUserInfo({ email: userInfo.value.email })
    if (result.success) {
      // 服务端可能返回规范化后的用户信息
      const serverUser = result.data?.user
      if (serverUser?.email) userInfo.value.email = serverUser.email
      // 资料存独立键，避免覆盖登录态 userInfo（用户名/角色）
      localStorage.setItem('userProfile', JSON.stringify(userInfo.value))
      editProfileDialog.value = false
      ElMessage.success('资料已更新')
    }
  } catch (error) {
    console.error('保存资料失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    savingProfile.value = false
  }
}

// 修改密码（调用后端 /auth/change-password）
async function changePassword() {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    ElMessage.warning('请填写完整')
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.error('密码长度至少6位')
    return
  }

  try {
    const result = await userStore.changePassword({
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword
    })
    if (result.success) {
      changePasswordDialog.value = false
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  }
}

// 成就系统相关函数
function getAchievementProgress(achievement) {
  if (achievement.unlocked) return 100
  
  const req = achievement.requirement
  let current = 0
  
  switch (req.type) {
    case 'count':
      current = emotionStore.predictions.length
      break
    case 'consecutive':
      current = consecutiveDays.value
      break
    case 'emotion':
      current = emotionStore.predictions.filter(p => p.emotion === req.emotion).length
      break
    case 'export':
      current = exportCount.value
      break
    case 'days':
      current = activeDays.value
      break
  }
  
  return Math.min(100, Math.round((current / req.value) * 100))
}

function showAchievementDetail(achievement) {
  selectedAchievement.value = achievement
  achievementDetailDialog.value = true
}

function checkAndUnlockAchievements() {
  achievements.value.forEach(achievement => {
    if (!achievement.unlocked) {
      const progress = getAchievementProgress(achievement)
      if (progress >= 100) {
        achievement.unlocked = true
        achievement.unlockedAt = new Date()
        experiencePoints.value += achievement.exp
        ElMessage.success({
          message: `🎉 解锁成就：${achievement.name}！获得 ${achievement.exp} EXP`,
          duration: 3000
        })
      }
    }
  })
  saveAchievements()
}

function saveAchievements() {
  localStorage.setItem('achievements', JSON.stringify(achievements.value))
  localStorage.setItem('experiencePoints', experiencePoints.value.toString())
  localStorage.setItem('exportCount', exportCount.value.toString())
}

function getLevelColor() {
  const colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c', 'var(--color-mahogany)']
  return colors[(userLevel.value - 1) % colors.length]
}

// 目标相关函数
function addGoal() {
  if (!newGoal.value.title) {
    ElMessage.warning('请输入目标标题')
    return
  }
  
  const goal = {
    id: Date.now(),
    ...newGoal.value,
    current: getCurrentGoalValue(newGoal.value.type),
    createdAt: new Date()
  }
  
  goals.value.push(goal)
  saveGoals()
  addGoalDialog.value = false
  ElMessage.success('目标添加成功')
  
  // 重置表单
  newGoal.value = {
    title: '',
    type: 'count',
    target: 10,
    current: 0,
    deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    completed: false
  }
}

function getCurrentGoalValue(type) {
  switch (type) {
    case 'count':
      return emotionStore.predictions.length
    case 'days':
      return consecutiveDays.value
    case 'positive':
      const positiveCount = emotionStore.predictions.filter(
        p => p.emotion === 'happy' || p.emotion === 'normal'
      ).length
      return Math.round((positiveCount / emotionStore.predictions.length) * 100) || 0
    default:
      return 0
  }
}

function getGoalProgress(goal) {
  const current = getCurrentGoalValue(goal.type)
  return Math.min(100, Math.round((current / goal.target) * 100))
}

function toggleGoal(goal) {
  if (goal.completed) {
    ElMessage.success('🎉 目标完成！')
    experiencePoints.value += 50
    saveAchievements()
  }
  saveGoals()
}

function deleteGoal(id) {
  goals.value = goals.value.filter(g => g.id !== id)
  saveGoals()
  ElMessage.success('目标已删除')
}

function saveGoals() {
  localStorage.setItem('goals', JSON.stringify(goals.value))
}

// 日期格式化
function formatDate(date) {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function formatDateTime(date) {
  if (!date) return '-'
  const d = new Date(date)
  return `${formatDate(d)} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

// 头像上传相关函数
function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB！')
    return false
  }
  return true
}

function handleAvatarChange(file) {
  avatarFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
    // 重置剪裁参数
    cropZoom.value = 1
    cropPosition.value = { x: 0, y: 0 }
    avatarCropDialog.value = true
    
    // 延迟执行以确保图片已加载
    setTimeout(() => {
      const imageElement = document.querySelector('.avatar-crop-frame img')
      if (imageElement && imageElement.complete) {
        const container = imageElement.parentElement
        const containerWidth = container.clientWidth // 400px
        const containerHeight = container.clientHeight // 400px
        const imageWidth = imageElement.naturalWidth
        const imageHeight = imageElement.naturalHeight
        
        console.log('图片尺寸:', imageWidth, 'x', imageHeight)
        console.log('容器尺寸:', containerWidth, 'x', containerHeight)
        
        // 计算初始缩放，确保图片能完整显示在容器中
        const scaleX = containerWidth / imageWidth
        const scaleY = containerHeight / imageHeight
        // 使用较小的缩放比例，确保图片完整显示
        const initialScale = Math.max(0.1, Math.min(scaleX, scaleY))
        
        cropZoom.value = initialScale
        console.log('初始缩放:', initialScale)
      }
    }, 200)
  }
  reader.readAsDataURL(file.raw)
}

// 处理图片拖拽移动
function handleImageDrag(event) {
  if (!isDragging.value) return
  
  const dx = event.clientX - dragStart.value.x
  const dy = event.clientY - dragStart.value.y
  
  cropPosition.value.x += dx / cropZoom.value
  cropPosition.value.y += dy / cropZoom.value
  
  dragStart.value = { x: event.clientX, y: event.clientY }
}

function startDrag(event) {
  isDragging.value = true
  dragStart.value = { x: event.clientX, y: event.clientY }
  document.addEventListener('mousemove', handleImageDrag)
  document.addEventListener('mouseup', stopDrag)
}

function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', handleImageDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 实现真正的头像剪裁功能
async function confirmAvatar() {
  // 使用document.querySelector直接获取图片元素，避免ref引用问题
  const imageElement = document.querySelector('.avatar-crop-frame img')
  
  if (!avatarPreview.value || !imageElement) {
    ElMessage.warning('请先上传图片')
    return
  }
  
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  
  // 设置画布大小为头像尺寸 (200x200)
  canvas.width = 200
  canvas.height = 200
  
  try {
    // 获取原始图片尺寸
    const imageWidth = imageElement.naturalWidth
    const imageHeight = imageElement.naturalHeight
    
    // 获取裁剪框容器尺寸
    const container = imageElement.parentElement
    const containerWidth = container.clientWidth
    const containerHeight = container.clientHeight
    
    // 计算图片在容器中的缩放比例和位置
    const scale = cropZoom.value
    
    // 计算要从原图中截取的区域
    // 确保截取区域始终在图片范围内
    const sourceX = Math.max(0, Math.min(imageWidth - canvas.width/scale, 
                     (containerWidth/2 - cropPosition.value.x)/scale - canvas.width/(2*scale)))
    const sourceY = Math.max(0, Math.min(imageHeight - canvas.height/scale, 
                     (containerHeight/2 - cropPosition.value.y)/scale - canvas.height/(2*scale)))
    const sourceWidth = canvas.width/scale
    const sourceHeight = canvas.height/scale
    
    // 绘制剪裁后的图像
    context.drawImage(
      imageElement,
      sourceX, sourceY,
      sourceWidth, sourceHeight,
      0, 0,
      canvas.width, canvas.height
    )
    
    // 获取剪裁后的图像数据（压缩为 200x200 JPEG，控制上传体积）
    const croppedImage = canvas.toDataURL('image/jpeg', 0.85)

    // 上传到服务端（/auth/avatar），成功后更新本地展示
    try {
      const response = await api.post('/auth/avatar', { avatar: croppedImage })
      userInfo.value.avatar = response.data.avatar_url || croppedImage
      // 同步到全局用户状态（顶栏头像立即更新）
      if (userStore.userInfo) {
        userStore.userInfo.avatar = response.data.avatar
      }
      avatarCropDialog.value = false
      ElMessage.success('头像更新成功')

      // 增加经验值
      experiencePoints.value += 10
      saveAchievements()
    } catch (uploadError) {
      console.error('头像上传失败:', uploadError)
      // 上传失败时降级为仅本地保存
      userInfo.value.avatar = croppedImage
      avatarCropDialog.value = false
      ElMessage.warning('头像已保存到本机（服务端上传失败）')
    }
  } catch (error) {
    console.error('头像剪裁失败:', error)
    ElMessage.error('头像剪裁失败，请重试')
  }
}

// 查看头像大图
function viewAvatar() {
  if (userInfo.value.avatar) {
    largeAvatarUrl.value = displayAvatar.value
    viewAvatarDialog.value = true
  }
}

// 数据导入相关函数
function beforeImportData(file) {
  const isJSON = file.type === 'application/json' || file.name.endsWith('.json')
  if (!isJSON) {
    ElMessage.error('只能上传 JSON 文件！')
    return false
  }
  return true
}

function handleImportData(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)

      ElMessageBox.confirm(
        '导入数据将合并到当前数据中（历史记录、设置、成就等），是否继续？',
        '确认导入',
        {
          confirmButtonText: '确定导入',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          // 导入图片识别历史：写入 IndexedDB（与 store 持久化路径一致）
          if (Array.isArray(data.predictions) && data.predictions.length > 0) {
            const existing = emotionStore.predictions.map(p => p.id)
            const incoming = data.predictions.filter(p => !existing.includes(p.id))
            emotionStore.predictions = [...incoming, ...emotionStore.predictions]
            await emotionStore.saveToStorage()
          }

          // 导入视频历史：写入 IndexedDB
          if (Array.isArray(data.videoHistory) && data.videoHistory.length > 0) {
            const existingVideoIds = new Set(videoStore.videoHistory.map(v => v.video_id))
            const incomingVideos = data.videoHistory.filter(v => !existingVideoIds.has(v.video_id))
            videoStore.videoHistory = [...incomingVideos, ...videoStore.videoHistory]
            await videoStore.saveHistory()
          }

          // 导入设置
          if (data.settings) {
            settings.value = { ...settings.value, ...data.settings }
            localStorage.setItem('userSettings', JSON.stringify(settings.value))
            applyTheme(settings.value.theme)
            applyAnimations(settings.value.animations)
          }

          // 导入成就 / 经验值 / 目标
          if (Array.isArray(data.achievements) && data.achievements.length > 0) {
            const unlockedIds = new Set(achievements.value.filter(a => a.unlocked).map(a => a.id))
            data.achievements.forEach(a => {
              if (a.unlocked && !unlockedIds.has(a.id)) {
                const target = achievements.value.find(x => x.id === a.id)
                if (target) {
                  target.unlocked = true
                  target.unlockedAt = a.unlockedAt
                }
              }
            })
            saveAchievements()
          }
          if (typeof data.experiencePoints === 'number' && data.experiencePoints > experiencePoints.value) {
            experiencePoints.value = data.experiencePoints
          }
          if (Array.isArray(data.goals)) {
            const existingGoalIds = new Set(goals.value.map(g => g.id))
            goals.value = [...goals.value, ...data.goals.filter(g => !existingGoalIds.has(g.id))]
            saveGoals()
          }

          ElMessage.success('数据导入成功！')
        } catch (importError) {
          console.error('导入数据处理失败:', importError)
          ElMessage.error('导入失败：' + importError.message)
        }
      }).catch(() => {
        ElMessage.info('已取消导入')
      })
    } catch (error) {
      console.error('数据解析失败:', error)
      ElMessage.error('数据格式错误，导入失败')
    }
  }
  reader.readAsText(file.raw)
}

// 从服务器同步识别历史到本地缓存
const syncing = ref(false)
async function syncFromServer() {
  syncing.value = true
  try {
    const records = await emotionStore.fetchServerHistories(100, 5)
    await emotionStore.loadFromStorage()
    await videoStore.loadFromStorage()
    ElMessage.success(`同步完成：服务端共 ${records.length} 条识别记录`)
  } catch (error) {
    console.error('同步失败:', error)
    ElMessage.error('同步失败，请检查后端服务是否可用')
  } finally {
    syncing.value = false
  }
}

// 导出所有数据
function exportAllData() {
  exportCount.value++
  checkAndUnlockAchievements() // 检查导出相关成就
  
  const data = {
    userInfo: userInfo.value,
    settings: settings.value,
    predictions: emotionStore.predictions,
    videoHistory: videoStore.videoHistory,
    achievements: achievements.value,
    goals: goals.value,
    experiencePoints: experiencePoints.value,
    exportCount: exportCount.value,
    gratitudes: JSON.parse(localStorage.getItem('gratitudes') || '[]'),
    journals: JSON.parse(localStorage.getItem('journals') || '[]'),
    exportDate: new Date().toISOString(),
    version: '2.0.0'
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `情绪识别数据备份_${new Date().toLocaleDateString()}.json`
  link.click()
  
  ElMessage.success('数据导出成功')
}

// 清空历史记录（本地 IndexedDB；服务端记录请到"历史记录"页删除）
function clearHistory() {
  ElMessageBox.confirm(
    '确定要清空本机的所有历史记录吗？此操作不可恢复！（服务端记录不受影响，可在历史记录页单独删除）',
    '清空本地历史',
    {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'error'
    }
  ).then(async () => {
    try {
      await emotionStore.clearAllPredictions()
      await videoStore.clearHistory()
      await videoStore.clearCurrentAnalysis()
      ElMessage.success('本地历史记录已清空')
    } catch (error) {
      console.error('清空历史失败:', error)
      ElMessage.error('清空失败：' + error.message)
    }
  }).catch(() => {})
}

// 监听识别数据变化，自动检查成就
watch(() => emotionStore.predictions.length, () => {
  checkAndUnlockAchievements()
}, { immediate: false })

// 监听视频历史变化，自动检查成就
watch(() => videoStore.videoHistory.length, () => {
  checkAndUnlockAchievements()
}, { immediate: false })

// 监听主题设置变化，确保主题状态一致
watch(() => settings.value.theme, (newTheme) => {
  // 当主题设置变化时，立即应用新主题
  applyTheme(newTheme)
})

// 创建节流保存函数，避免频繁写入 localStorage
let userInfoSaveTimer = null
let settingsSaveTimer = null

// 使用 flush: 'post' 确保在 DOM 更新后才保存，避免初始化时的不必要保存
// 监听设置变化，自动保存（节流500ms）
watch(settings, (newSettings) => {
  if (!isInitialized.value) return
  if (settingsSaveTimer) clearTimeout(settingsSaveTimer)
  settingsSaveTimer = setTimeout(() => {
    console.log('💾 自动保存设置')
    localStorage.setItem('userSettings', JSON.stringify(newSettings))
  }, 500)
}, { deep: true })

// 监听用户信息变化，自动保存（节流500ms，独立键避免覆盖登录态）
watch(userInfo, (newUserInfo) => {
  if (!isInitialized.value) return
  if (userInfoSaveTimer) clearTimeout(userInfoSaveTimer)
  userInfoSaveTimer = setTimeout(() => {
    localStorage.setItem('userProfile', JSON.stringify(newUserInfo))
  }, 500)
}, { deep: true })

let goalsSaveTimer = null
let achievementsSaveTimer = null

// 监听目标变化，自动保存（节流500ms）
watch(goals, (newGoals) => {
  if (!isInitialized.value) return
  if (goalsSaveTimer) clearTimeout(goalsSaveTimer)
  goalsSaveTimer = setTimeout(() => {
    console.log('💾 自动保存目标')
    localStorage.setItem('goals', JSON.stringify(newGoals))
  }, 500)
}, { deep: true })

// 监听成就变化，自动保存（节流500ms）
watch(achievements, (newAchievements) => {
  if (!isInitialized.value) return
  if (achievementsSaveTimer) clearTimeout(achievementsSaveTimer)
  achievementsSaveTimer = setTimeout(() => {
    console.log('💾 自动保存成就')
    localStorage.setItem('achievements', JSON.stringify(newAchievements))
  }, 500)
}, { deep: true })

// 监听经验值变化，自动保存（立即）
watch(experiencePoints, (newExp) => {
  if (!isInitialized.value) return
  console.log('💾 自动保存经验值:', newExp)
  localStorage.setItem('experiencePoints', newExp.toString())
})

// 监听导出次数变化，自动保存（立即）
watch(exportCount, (newCount) => {
  if (!isInitialized.value) return
  console.log('💾 自动保存导出次数:', newCount)
  localStorage.setItem('exportCount', newCount.toString())
})

onMounted(() => {
  loadModelOptions()
  try {
    // 应用当前设置（不再打印冗余日志）
    setTimeout(() => {
      applyTheme(settings.value.theme)
      applyAnimations(settings.value.animations)
      applyLanguage('zh-CN')

      // 异步检查成就，避免阻塞UI
      setTimeout(checkAndUnlockAchievements, 100)

      // 标记初始化完成，开始监听数据变化
      setTimeout(() => {
        isInitialized.value = true
      }, 200)
    }, 50)

    // 拉取服务端历史，让统计卡片展示真实数据
    emotionStore.fetchServerHistories(100, 3).catch(() => {})
  } catch (error) {
    console.error('初始化时出错:', error)
  }
})

// 在组件卸载前保存所有待保存的数据
onBeforeUnmount(() => {
  console.log('🔄 组件卸载前保存所有数据...')
  
  // 清除所有定时器并立即保存
  if (userInfoSaveTimer) {
    clearTimeout(userInfoSaveTimer)
    localStorage.setItem('userProfile', JSON.stringify(userInfo.value))
  }
  
  if (settingsSaveTimer) {
    clearTimeout(settingsSaveTimer)
    localStorage.setItem('userSettings', JSON.stringify(settings.value))
    console.log('💾 卸载时保存设置')
  }
  
  if (goalsSaveTimer) {
    clearTimeout(goalsSaveTimer)
    localStorage.setItem('goals', JSON.stringify(goals.value))
    console.log('💾 卸载时保存目标')
  }
  
  if (achievementsSaveTimer) {
    clearTimeout(achievementsSaveTimer)
    localStorage.setItem('achievements', JSON.stringify(achievements.value))
    console.log('💾 卸载时保存成就')
  }
  
  console.log('✅ 所有数据已保存')
})
</script>

<style scoped>
.user-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: var(--color-surface);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--color-ink);
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--color-mahogany);
  font-size: 1.1rem;
}

.profile-card {
  margin-bottom: 1.5rem;
}

.profile-header {
  text-align: center;
  position: relative;
  padding: 1rem 0;
}

.avatar-upload {
  position: absolute;
  bottom: 1rem;
  right: calc(50% - 50px);
  transform: translateX(50%);
}

.profile-info {
  text-align: center;
  margin: 1.5rem 0;
}

.profile-info h3 {
  font-size: 1.5rem;
  color: var(--color-ink);
  margin-bottom: 0.5rem;
}

.user-email {
  color: var(--color-mahogany);
  margin-bottom: 0.75rem;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding: 1rem 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--color-accent);
  margin-bottom: 0.25rem;
}

.stat-label {
  color: var(--color-mahogany);
  font-size: 0.875rem;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.quick-actions-card {
  margin-bottom: 1.5rem;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.upload-full-width {
  width: 100%;
  display: block;
  margin: 0;
  padding: 0;
}

.upload-full-width :deep(.el-upload) {
  width: 100%;
  display: block;
  margin: 0;
  padding: 0;
}

/* 快速操作按钮样式 */
.action-btn {
  justify-content: flex-start !important;
  width: 100% !important;
  padding: 10px 16px !important;
  height: 40px !important;
  text-align: left;
  margin: 0 !important;
  box-sizing: border-box !important;
}

/* 按钮内部容器 */
.action-btn :deep(.el-button__content) {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  width: 100%;
}

/* 按钮图标 */
.action-btn :deep(.el-icon) {
  font-size: 16px;
  margin: 0 !important;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 按钮文字 */
.action-btn :deep(span:not(.el-icon)) {
  flex: 1;
  line-height: 1.5;
  text-align: left;
}

.settings-card {
  margin-bottom: 1.5rem;
}

.form-item-tip {
  margin-left: 1rem;
  color: var(--color-mahogany);
  font-size: 0.875rem;
}

.save-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding: 2rem 0;
}

/* 成就系统样式 */
.achievements-card {
  margin-bottom: 2rem;
}

.card-header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.achievement-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid var(--color-sand);
  cursor: pointer;
  transition: all 0.3s;
}

.achievement-item.unlocked {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.achievement-item.locked {
  opacity: 0.6;
  background: var(--el-color-primary-light-9);
}

.achievement-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.achievement-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.achievement-info {
  flex: 1;
}

.achievement-name {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
  color: var(--color-ink);
}

.achievement-desc {
  font-size: 0.9rem;
  color: var(--color-mahogany);
  margin-bottom: 0.5rem;
}

.achievement-unlocked {
  font-size: 0.85rem;
  color: #67c23a;
  font-weight: 500;
}

/* 使用统计样式 */
.stats-card {
  margin-bottom: 2rem;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

.stat-box-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.stat-box-content {
  flex: 1;
}

.stat-box-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-ink);
}

.stat-box-label {
  font-size: 0.9rem;
  color: var(--color-mahogany);
  margin-top: 0.25rem;
}

.level-progress {
  margin-top: 1rem;
}

.level-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-mahogany);
}

/* 目标系统样式 */
.goals-card {
  margin-bottom: 2rem;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.goal-item {
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  border: 1px solid var(--color-sand);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.goal-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.goal-progress .el-progress {
  flex: 1;
}

.goal-target {
  font-size: 0.9rem;
  color: var(--color-mahogany);
  white-space: nowrap;
}

.goal-deadline {
  font-size: 0.85rem;
  color: var(--color-mahogany);
}

/* 成就详情对话框样式 */
.achievement-detail {
  text-align: center;
  padding: 1rem 0;
}

.achievement-detail-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.achievement-detail h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-ink);
}

.achievement-detail-desc {
  color: var(--color-mahogany);
  margin-bottom: 1.5rem;
}

.achievement-detail-info {
  text-align: left;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-sand);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-weight: 500;
  color: var(--color-mahogany);
}

.info-item .value {
  color: var(--color-ink);
}

/* 头像裁剪样式 */
.avatar-crop-container {
  padding: 1rem 0;
}

.crop-preview {
  width: 100%;
  height: 500px; /* 增加高度以容纳更大的图片 */
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  margin-bottom: 1rem;
  position: relative;
}

.avatar-crop-frame {
  width: 400px; /* 增加裁剪框大小 */
  height: 400px;
  overflow: hidden;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-crop-frame img {
  max-width: none; /* 允许图片超出容器 */
  max-height: none;
  display: block;
}

.crop-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
}

.crop-indicator {
  width: 300px; /* 增大裁剪指示框 */
  height: 300px;
  border: 2px dashed #fff;
  background: transparent;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
  border-radius: 4px;
}

.crop-controls {
  padding: 0 1rem;
}

.crop-instructions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-mahogany);
  font-size: 0.9rem;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: var(--el-color-primary-light-9);
  border-radius: 6px;
  border-left: 4px solid var(--el-color-primary);
}

.avatar-view-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 0;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .profile-stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .save-actions {
    flex-direction: column;
  }
  
  .achievements-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-box {
    flex-direction: column;
    text-align: center;
  }
}

/* 动画效果样式 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.animate-fade {
  animation: fadeIn 0.3s ease-in-out;
}

.card-hover-animation {
  transition: all 0.3s ease;
}

.card-hover-animation:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

/* 深色模式样式 */
.dark {
  background-color: #1a1a1a !important;
  color: #e0e0e0 !important;
}

.dark .el-card {
  background-color: #2c2c2c !important;
  border-color: #404040 !important;
  color: #e0e0e0 !important;
}

.dark .el-card__header {
  background-color: #333333 !important;
  border-bottom: 1px solid #404040 !important;
}

.dark .el-input__wrapper {
  background-color: #333333 !important;
  border-color: #404040 !important;
}

.dark .el-input__inner {
  color: #e0e0e0 !important;
}

.dark .el-switch__core {
  background-color: #555555 !important;
}

.dark .el-switch__core.is-checked {
  background-color: var(--color-accent) !important;
}

.dark .el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background-color: var(--color-accent) !important;
  border-color: var(--color-accent) !important;
}

.dark .el-select {
  color: #e0e0e0 !important;
}

.dark .el-dropdown-menu {
  background-color: #2c2c2c !important;
  border-color: #404040 !important;
}

.dark .el-dropdown-menu__item {
  color: #e0e0e0 !important;
}

.dark .el-dropdown-menu__item:hover {
  background-color: #333333 !important;
}

.dark .el-dialog {
  background-color: #2c2c2c !important;
  border-color: #404040 !important;
}

.dark .el-dialog__header {
  background-color: #333333 !important;
  border-bottom: 1px solid #404040 !important;
}

.dark .el-dialog__title {
  color: #e0e0e0 !important;
}

.dark .profile-info h3 {
  color: #e0e0e0 !important;
}

.dark .stat-value {
  color: #8c9eff !important;
}

.dark .achievement-name {
  color: #e0e0e0 !important;
}

.dark .achievement-detail h3 {
  color: #e0e0e0 !important;
}

.dark .info-item .value {
  color: #e0e0e0 !important;
}

.dark .crop-preview {
  background: #2c2c2c !important;
}

.dark .crop-instructions {
  background: #2c3e50 !important;
  color: #e0e0e0 !important;
  border-left-color: var(--color-accent) !important;
}

/* 无动画模式 */
.no-animations {
  --el-transition-duration: 0ms !important;
}

.no-animations * {
  transition: none !important;
  animation: none !important;
}
</style>
