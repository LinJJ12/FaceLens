<template>
  <div class="about-view">
    <el-card class="about-card" shadow="never">
      <template #header>
        <h2>关于 FaceLens</h2>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="系统名称">
          FaceLens — 基于 RAF-DB 的人脸情绪识别系统
        </el-descriptions-item>
        <el-descriptions-item label="数据集">
          RAF-DB (Real-world Affective Faces Database)
        </el-descriptions-item>
        <el-descriptions-item label="情绪类别">
          7类: 生气、厌恶、害怕、高兴、平静、悲伤、惊讶
        </el-descriptions-item>
        <el-descriptions-item label="模型架构">
          <el-tag v-for="m in modelPerformance" :key="m.model" style="margin: 0 8px 8px 0;" effect="plain">
            {{ m.model }} ({{ m.accuracy }}%)
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>模型性能</h3>
      <el-table :data="modelPerformance" style="width: 100%; margin-top: 1rem;">
        <el-table-column prop="model" label="模型" width="140" />
        <el-table-column prop="accuracy" label="准确率" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.accuracy" color="var(--color-accent)" />
          </template>
        </el-table-column>
        <el-table-column prop="availableLabel" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.available === false ? 'info' : 'success'" size="small" effect="plain">
              {{ row.available === false ? '离线' : '可用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
      </el-table>

      <el-divider />

      <h3>技术栈</h3>
      <div class="tech-stack">
        <el-tag size="large" effect="plain">Python 3.8+</el-tag>
        <el-tag size="large" effect="plain">TensorFlow / Keras</el-tag>
        <el-tag size="large" effect="plain">Flask</el-tag>
        <el-tag size="large" effect="plain">Vue 3</el-tag>
        <el-tag size="large" effect="plain">Element Plus</el-tag>
        <el-tag size="large" effect="plain">ECharts</el-tag>
      </div>

      <el-divider />

      <h3>使用说明</h3>
      <ol class="instructions">
        <li>选择要使用的识别模型（CNN / VGG16 / SE-Net）</li>
        <li>可选择是否启用人脸检测与对齐功能</li>
        <li>上传图片、使用摄像头拍照或上传视频</li>
        <li>点击"开始识别"按钮</li>
        <li>查看识别结果、概率分布与质量评估</li>
      </ol>

      <el-divider />

      <h3>常见问题</h3>
      <el-collapse class="faq">
        <el-collapse-item title="识别结果不准确怎么办？">
          <p>请确保人脸清晰、正对镜头且光照均匀。系统会给出图片质量评估（清晰度/亮度/对比度），可据此调整拍摄条件；也可尝试切换其他模型对比结果。</p>
        </el-collapse-item>
        <el-collapse-item title="支持哪些图片和视频格式？">
          <p>图片支持 JPG / PNG / WEBP / BMP（最大 16MB）；视频支持 MP4 / AVI / MOV / MKV / FLV / WMV（最大 200MB）。</p>
        </el-collapse-item>
        <el-collapse-item title="历史记录存在哪里？">
          <p>识别记录保存在您自托管的服务端数据库中，可在"历史记录"页查看与删除；浏览器本地同时保留一份离线副本用于快速展示。</p>
        </el-collapse-item>
        <el-collapse-item title="忘记密码怎么办？">
          <p>在登录页点击"忘记密码"，通过注册邮箱接收重置链接（需要后端配置邮件服务）。</p>
        </el-collapse-item>
      </el-collapse>

      <el-divider />

      <div class="footer-info">
        <p>© 2026 FaceLens · 基于 RAF-DB 数据集训练</p>
        <p>仅供学习与研究使用，不构成医学或心理诊断建议</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEmotionStore } from '../stores/emotion'

const emotionStore = useEmotionStore()

// 静态兜底；挂载后用后端 /api/models 的真实数据覆盖
const defaultModels = [
  { model: 'CNN', key: 'cnn', accuracy: 83.77, description: 'CNN基础模型，轻量高效' },
  { model: 'VGG16', key: 'vgg', accuracy: 80.0, description: 'VGG16迁移学习模型' },
  { model: 'SE-Net (81)', key: 'se81', accuracy: 81.0, description: 'SE注意力机制模型，关注关键特征' },
  { model: 'SE-Net (83)', key: 'se83', accuracy: 83.0, description: 'SE注意力机制模型（最佳版本）' }
]

const modelPerformance = ref(defaultModels)

onMounted(async () => {
  try {
    await emotionStore.fetchModels()
    const apiModels = emotionStore.availableModels
    if (Array.isArray(apiModels) && apiModels.length) {
      modelPerformance.value = defaultModels.map((m) => {
        const found = apiModels.find((x) => String(x.name || '').toLowerCase() === m.key)
        if (!found) return { ...m, availableLabel: '可用' }
        const acc = typeof found.accuracy === 'number' && found.accuracy <= 1
          ? Number((found.accuracy * 100).toFixed(2))
          : Number(found.accuracy ?? m.accuracy)
        return {
          ...m,
          model: found.display_name || m.model,
          accuracy: acc,
          available: found.available !== false,
          description: found.description || m.description
        }
      })
    }
  } catch (error) {
    // 后端不可用时保留静态兜底
  }
})
</script>

<style scoped>
.about-view {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.about-card {
  border-radius: 12px;
}

.about-card h2,
.about-card h3 {
  color: var(--color-ink);
  margin-bottom: 1rem;
  letter-spacing: -0.01em;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.instructions {
  line-height: 2;
  color: var(--color-mahogany);
  padding-left: 1.5rem;
}

.faq {
  margin-top: 1rem;
}

.faq p {
  color: var(--color-mahogany);
  line-height: 1.7;
  margin: 0;
}

.footer-info {
  text-align: center;
  color: var(--color-mahogany);
  margin-top: 2rem;
  font-size: 0.875rem;
}

.footer-info p {
  margin: 0.5rem 0;
}
</style>
