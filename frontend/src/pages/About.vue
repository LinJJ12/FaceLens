<template>
  <div class="about-view">
    <el-card class="about-card">
      <template #header>
        <h2>ℹ️ 关于系统</h2>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="系统名称">
          人脸情绪识别系统
        </el-descriptions-item>
        <el-descriptions-item label="数据集">
          RAF-DB (Real-world Affective Faces Database)
        </el-descriptions-item>
        <el-descriptions-item label="情绪类别">
          7类: 生气、厌恶、害怕、高兴、平静、悲伤、惊讶
        </el-descriptions-item>
        <el-descriptions-item label="模型架构">
          <el-tag type="primary">CNN (83.77%)</el-tag>
          <el-tag type="success" style="margin-left: 8px;">VGG16 (80%)</el-tag>
          <el-tag type="warning" style="margin-left: 8px;">SE-Net (81%)</el-tag>
          <el-tag type="danger" style="margin-left: 8px;">SE-Net (83%)</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>模型性能</h3>
      <el-table :data="modelPerformance" style="width: 100%; margin-top: 1rem;">
        <el-table-column prop="model" label="模型" width="120" />
        <el-table-column prop="accuracy" label="准确率" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.accuracy" :color="'#67c23a'" />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
      </el-table>

      <el-divider />

      <h3>技术栈</h3>
      <div class="tech-stack">
        <el-tag size="large">Python 3.8</el-tag>
        <el-tag size="large" type="success">TensorFlow/Keras</el-tag>
        <el-tag size="large" type="info">Flask</el-tag>
        <el-tag size="large" type="warning">Vue 3</el-tag>
        <el-tag size="large" type="danger">Element Plus</el-tag>
      </div>

      <el-divider />

      <h3>使用说明</h3>
      <ol class="instructions">
        <li>选择要使用的识别模型(CNN/VGG16/SE-Net)</li>
        <li>可选择是否启用人脸检测功能</li>
        <li>上传图片或使用摄像头拍照</li>
        <li>点击"开始识别"按钮</li>
        <li>查看识别结果和详细概率分布</li>
      </ol>

      <el-divider />

      <div class="footer-info">
        <p>© 2025 人脸情绪识别系统</p>
        <p>基于 RAF-DB 数据集训练</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
const modelPerformance = [
  {
    model: 'CNN',
    accuracy: 83.77,
    description: 'CNN基础模型，轻量高效'
  },
  {
    model: 'VGG16',
    accuracy: 80.00,
    description: 'VGG16迁移学习模型'
  },
  {
    model: 'SE-Net (81%)',
    accuracy: 81.00,
    description: 'SE注意力机制模型，关注关键特征'
  },
  {
    model: 'SE-Net (83%)',
    accuracy: 83.00,
    description: 'SE注意力机制模型(最佳版本)'
  }
]
</script>

<style scoped>
.about-view {
  width: 100%;
  max-width: 900px;
}

.about-card {
  border-radius: 12px;
}

.about-card h2,
.about-card h3 {
  color: #303133;
  margin-bottom: 1rem;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.instructions {
  line-height: 2;
  color: #606266;
  padding-left: 1.5rem;
}

.footer-info {
  text-align: center;
  color: #909399;
  margin-top: 2rem;
}

.footer-info p {
  margin: 0.5rem 0;
}
</style>
