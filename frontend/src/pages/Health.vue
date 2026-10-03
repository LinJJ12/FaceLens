<template>
  <div class="health-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>心理健康中心</h1>
      <p>基于您的情绪状态，提供个性化的心理健康建议和放松技巧</p>
    </div>

    <!-- 空状态提示 -->
    <el-card class="empty-state-card" shadow="hover" v-if="!latestEmotion">
      <el-empty description="还没有情绪记录">
        <template #image>
          <div style="font-size: 80px;">😊</div>
        </template>
        <p style="color: var(--color-mahogany); margin-bottom: 1rem;">
          请先在首页上传照片进行情绪识别，系统会为您提供个性化的心理健康建议
        </p>
        <el-button type="primary" @click="$router.push('/')">
          前往首页识别
        </el-button>
      </el-empty>
      <el-divider />
      <div style="margin-top: 2rem;">
        <h3 style="text-align: center; margin-bottom: 1rem;">浏览所有情绪建议</h3>
        <el-row :gutter="16">
          <el-col :xs="12" :sm="8" :md="6" v-for="emotion in allEmotions" :key="emotion.key">
            <el-button 
              style="width: 100%; margin-bottom: 10px;"
              @click="selectEmotion(emotion.key)"
            >
              {{ emotion.emoji }} {{ emotion.name }}
            </el-button>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 当前情绪状态卡片 -->
    <el-card class="emotion-status-card" shadow="hover" v-else>
      <template #header>
        <div class="card-header">
          <span>当前情绪状态</span>
          <el-tag :type="getEmotionTagType(latestEmotion.emotion)">
            {{ latestEmotion.emotion_cn }}
          </el-tag>
          <el-tag v-if="latestEmotion.manual" size="small" type="info" effect="plain" style="margin-left: 8px;">
            手动选择
          </el-tag>
        </div>
      </template>
      <div class="emotion-status-content">
        <div class="emotion-display">
          <div class="emotion-emoji">{{ getEmotionEmoji(latestEmotion.emotion) }}</div>
          <div class="emotion-details">
            <h3>{{ latestEmotion.emotion_cn }}</h3>
            <el-progress
              :percentage="Math.round(latestEmotion.confidence * 100)"
              :color="getProgressColor(latestEmotion.confidence)"
            />
            <p class="emotion-time">检测时间: {{ formatTime(latestEmotion.timestamp) }}</p>
          </div>
        </div>
        <el-button type="primary" @click="getNewAdvice">
          获取新建议
        </el-button>
      </div>
    </el-card>

    <!-- 个性化建议 -->
    <el-row :gutter="20" class="advice-section">
      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <el-card class="advice-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#67c23a"><info-filled /></el-icon>
              <span>即时建议</span>
            </div>
          </template>
          <div class="advice-content">
            <h4>{{ currentAdvice.title }}</h4>
            <p>{{ currentAdvice.description }}</p>
            <el-divider />
            <h5>立即行动:</h5>
            <ul>
              <li v-for="(action, index) in currentAdvice.actions" :key="index">
                {{ action }}
              </li>
            </ul>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <el-card class="advice-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#409eff"><medal /></el-icon>
              <span>放松技巧</span>
            </div>
          </template>
          <div class="advice-content">
            <h4>{{ relaxationTechnique.title }}</h4>
            <p>{{ relaxationTechnique.description }}</p>
            <el-divider />
            <div class="technique-steps">
              <el-steps direction="vertical" :active="activeStep" finish-status="success">
                <el-step
                  v-for="(step, index) in relaxationTechnique.steps"
                  :key="index"
                  :title="step"
                />
              </el-steps>
              <el-button-group class="step-controls">
                <el-button size="small" @click="prevStep" :disabled="activeStep === 0">
                  上一步
                </el-button>
                <el-button size="small" type="primary" @click="nextStep">
                  {{ activeStep >= relaxationTechnique.steps.length ? '完成' : '下一步' }}
                </el-button>
              </el-button-group>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="12" :lg="8">
        <el-card class="advice-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#e6a23c"><reading /></el-icon>
              <span>推荐资源</span>
            </div>
          </template>
          <div class="advice-content">
            <div class="resource-list">
              <div
                v-for="(resource, index) in recommendedResources"
                :key="index"
                class="resource-item"
              >
                <div class="resource-icon">{{ resource.icon }}</div>
                <div class="resource-info">
                  <h5>{{ resource.title }}</h5>
                  <p>{{ resource.description }}</p>
                  <el-link :href="resource.link" target="_blank" type="primary">
                    了解更多 →
                  </el-link>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 情绪历史趋势分析 (基于视频和图片数据) -->
    <el-card class="emotion-trend-card" shadow="hover" v-if="allEmotionRecords.length > 3">
      <template #header>
        <div class="card-header">
          <el-icon color="var(--color-mahogany)"><trend-charts /></el-icon>
          <span>情绪历史趋势</span>
        </div>
      </template>
      <div class="trend-content">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <div class="trend-stat">
              <div class="trend-icon" style="background: linear-gradient(135deg, #67c23a 0%, #38f9d7 100%)">
                😊
              </div>
              <div class="trend-info">
                <div class="trend-label">积极情绪占比</div>
                <div class="trend-value">{{ emotionStats.positiveRate }}%</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="trend-stat">
              <div class="trend-icon" style="background: var(--el-color-primary-light-9)">
                😢
              </div>
              <div class="trend-info">
                <div class="trend-label">消极情绪占比</div>
                <div class="trend-value">{{ emotionStats.negativeRate }}%</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="trend-stat">
              <div class="trend-icon" style="background: linear-gradient(135deg, #409eff 0%, var(--color-accent) 100%)">
                📊
              </div>
              <div class="trend-info">
                <div class="trend-label">情绪稳定性</div>
                <div class="trend-value">{{ emotionStats.stability }}</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="trend-stat">
              <div class="trend-icon" style="background: linear-gradient(135deg, #e6a23c 0%, #ffd700 100%)">
                🎬
              </div>
              <div class="trend-info">
                <div class="trend-label">视频分析数</div>
                <div class="trend-value">{{ videoStore.videoHistory.length }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <el-alert
          :title="emotionStats.alertTitle"
          :type="emotionStats.alertType"
          :closable="false"
          style="margin-top: 20px;"
        >
          <div>
            <p>{{ emotionStats.alertDescription }}</p>
            <ul style="margin-top: 10px; padding-left: 20px;">
              <li v-for="(suggestion, index) in emotionStats.suggestions" :key="index">
                {{ suggestion }}
              </li>
            </ul>
          </div>
        </el-alert>
      </div>
    </el-card>

    <!-- 情绪科普教育 -->
    <el-card class="emotion-education-card" shadow="hover" v-if="latestEmotion && currentEmotionKnowledge">
      <template #header>
        <div class="card-header">
          <el-icon color="#409eff"><document /></el-icon>
          <span>{{ currentEmotionKnowledge.title }}</span>
        </div>
      </template>
      <div class="education-content">
        <div class="education-intro">
          <h4>{{ currentEmotionKnowledge.subtitle }}</h4>
          <p class="intro-text">{{ currentEmotionKnowledge.description }}</p>
        </div>
        
        <el-collapse v-model="activeEducationSections" accordion>
          <el-collapse-item 
            v-for="(section, index) in currentEmotionKnowledge.sections" 
            :key="index"
            :name="index"
          >
            <template #title>
              <strong>{{ section.title }}</strong>
            </template>
            <p class="section-content">{{ section.content }}</p>
          </el-collapse-item>
        </el-collapse>

        <div class="knowledge-tips" v-if="currentEmotionKnowledge.tips">
          <h5>重要提示</h5>
          <ul>
            <li v-for="(tip, index) in currentEmotionKnowledge.tips" :key="index">
              {{ tip }}
            </li>
          </ul>
        </div>

        <!-- 推荐书籍 -->
        <div class="recommended-books" v-if="recommendedBooks.length > 0">
          <h5>延伸阅读</h5>
          <div class="book-list">
            <div class="book-item" v-for="(book, index) in recommendedBooks" :key="index">
              <div class="book-info">
                <h6>{{ book.title }}</h6>
                <p class="book-author">作者: {{ book.author }}</p>
                <p class="book-desc">{{ book.description }}</p>
              </div>
              <el-link :href="book.link" target="_blank" type="primary">了解详情</el-link>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 更多建议浏览 -->
    <el-card class="more-advice-card" shadow="hover" v-if="latestEmotion">
      <template #header>
        <div class="card-header">
          <span>更多{{ latestEmotion.emotion_cn }}建议 ({{ allAdviceList.length }}条)</span>
          <el-button type="primary" size="small" @click="refreshAdviceList">
            <el-icon><refresh /></el-icon> 换一批
          </el-button>
        </div>
      </template>
      <div class="advice-list-container">
        <el-row :gutter="16">
          <el-col 
            :xs="24" 
            :sm="12" 
            :md="8" 
            :lg="6" 
            v-for="advice in displayedAdviceList" 
            :key="advice.id"
          >
            <div class="advice-item">
              <el-tag size="small" effect="plain" style="margin-bottom: 8px;">
                {{ advice.category }}
              </el-tag>
              <p>{{ advice.text }}</p>
            </div>
          </el-col>
        </el-row>
        <el-divider />
        <div style="text-align: center;">
          <el-button @click="showMoreAdvice = !showMoreAdvice">
            {{ showMoreAdvice ? '收起' : '查看全部建议' }}
            <el-icon>
              <arrow-down v-if="!showMoreAdvice" />
              <arrow-up v-else />
            </el-icon>
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 情绪管理工具箱 -->
    <el-card class="toolbox-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>情绪管理工具箱</span>
        </div>
      </template>
      <el-tabs v-model="activeTab" class="toolbox-tabs">
        <!-- 呼吸训练 -->
        <el-tab-pane label="深呼吸训练" name="breathing">
          <div class="breathing-exercise">
            <el-select v-model="selectedBreathingType" placeholder="选择呼吸法" style="margin-bottom: 1rem;">
              <el-option label="4-7-8呼吸法(快速放松)" value="478" />
              <el-option label="箱式呼吸(海豹突击队)" value="box" />
              <el-option label="共振呼吸(深度放松)" value="resonant" />
            </el-select>
            <div class="breathing-info" v-if="currentBreathingInfo">
              <p><strong>{{ currentBreathingInfo.name }}</strong></p>
              <p>{{ currentBreathingInfo.description }}</p>
              <p class="benefit-text">{{ currentBreathingInfo.benefit }}</p>
            </div>
            <div class="breathing-circle" :class="{ breathing: isBreathing }">
              <span class="breathing-text">{{ breathingText }}</span>
            </div>
            <div class="breathing-controls">
              <el-button type="primary" @click="startBreathing" v-if="!isBreathing">
                开始训练
              </el-button>
              <el-button @click="stopBreathing" v-else>
                停止
              </el-button>
              <p class="breathing-instruction">{{ breathingInstruction }}</p>
            </div>
          </div>
        </el-tab-pane>

        <!-- 冥想引导 -->
        <el-tab-pane label="冥想引导" name="meditation">
          <div class="meditation-guide">
            <el-select v-model="selectedMeditation" placeholder="选择冥想类型" style="width: 200px; margin-bottom: 20px;">
              <el-option
                v-for="med in meditations"
                :key="med.id"
                :label="med.title"
                :value="med.id"
              />
            </el-select>
            <div v-if="selectedMeditation" class="meditation-content">
              <h4>{{ getCurrentMeditation().title }}</h4>
              <p class="meditation-description">{{ getCurrentMeditation().description }}</p>
              <p class="meditation-duration">{{ getCurrentMeditation().duration }}</p>
              <el-divider />
              <div class="meditation-video-container">
                <video 
                  :src="getCurrentMeditation().video" 
                  controls 
                  class="meditation-video"
                  :poster="getCurrentMeditation().poster"
                  preload="metadata"
                >
                  您的浏览器不支持视频播放
                </video>
              </div>
              <div class="meditation-tips">
                <h5>冥想小贴士</h5>
                <ul>
                  <li>找一个安静、舒适的环境</li>
                  <li>调整坐姿或躺姿，保持身体放松</li>
                  <li>跟随视频指引，专注于当下</li>
                  <li>如果思绪飘散，温柔地将注意力带回</li>
                </ul>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 渐进式肌肉放松 -->
        <el-tab-pane label="肌肉放松" name="pmr">
          <div class="pmr-exercise">
            <p class="pmr-intro">渐进式肌肉放松(PMR)通过紧张-放松各肌肉群来减少焦虑和压力</p>
            <div class="pmr-sequence">
              <el-steps :active="pmrStep" direction="vertical" finish-status="success">
                <el-step 
                  v-for="(step, index) in pmrSequence" 
                  :key="index"
                  :title="step"
                  :description="index === pmrStep ? '正在进行...' : ''"
                />
              </el-steps>
            </div>
            <div class="pmr-controls">
              <el-button-group>
                <el-button @click="prevPmrStep" :disabled="pmrStep === 0">
                  上一步
                </el-button>
                <el-button type="primary" @click="nextPmrStep">
                  {{ pmrStep >= pmrSequence.length - 1 ? '完成' : '下一步' }}
                </el-button>
              </el-button-group>
              <el-button @click="resetPmr" style="margin-left: 1rem;">重新开始</el-button>
            </div>
            <p class="pmr-tip">每个动作紧张 5 秒、放松 10 秒，感受两者的差异</p>
          </div>
        </el-tab-pane>

        <!-- 接地技术 -->
        <el-tab-pane label="接地练习" name="grounding">
          <div class="grounding-exercise">
            <h4>5-4-3-2-1接地技术</h4>
            <p class="grounding-intro">通过五感将注意力带回当下,快速缓解焦虑</p>
            <div class="grounding-steps">
              <div class="grounding-step" v-for="step in groundingSteps" :key="step.number">
                <div class="step-header">
                  <span class="step-number">{{ step.number }}</span>
                  <h5>{{ step.title }}</h5>
                </div>
                <el-input
                  v-model="groundingInputs[step.number - 1]"
                  type="textarea"
                  :rows="2"
                  :placeholder="step.placeholder"
                />
              </div>
            </div>
            <el-button type="primary" @click="completeGrounding">
              完成练习
            </el-button>
            <p class="grounding-benefit">适用于焦虑发作、惊恐、解离等情况</p>
          </div>
        </el-tab-pane>

        <!-- 积极心理学练习 -->
        <el-tab-pane label="积极练习" name="positive">
          <div class="positive-exercise">
            <h4>今日感恩记录</h4>
            <p>写下三件让你感到感恩的事情：</p>
            <el-input
              v-for="i in 3"
              :key="i"
              v-model="gratitudeList[i-1]"
              :placeholder="`第 ${i} 件事`"
              style="margin-bottom: 1rem"
            />
            <div class="journal-actions">
              <el-button type="primary" @click="saveGratitude">
                保存记录
              </el-button>
              <el-button @click="viewGratitudeHistory">
                查看历史
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 情绪日记 -->
        <el-tab-pane label="情绪日记" name="journal">
          <div class="emotion-journal">
            <h4>记录此刻的感受</h4>
            <el-input
              v-model="journalContent"
              type="textarea"
              :rows="8"
              placeholder="写下你现在的心情、想法和感受..."
            />
            <div class="journal-actions">
              <el-button type="primary" @click="saveJournal">
                保存日记
              </el-button>
              <el-button @click="viewJournalHistory">
                查看历史
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 专业资源与帮助 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card class="emergency-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#f56c6c"><warning-filled /></el-icon>
              <span>紧急求助热线</span>
            </div>
          </template>
          <div class="emergency-content">
            <p>如果您正在经历严重的情绪困扰或危机，请立即寻求专业帮助：</p>
            <div class="emergency-contacts">
              <div 
                class="contact-item" 
                v-for="(contact, index) in mentalHealthResources.emergencyContacts" 
                :key="index"
              >
                <h5>{{ contact.name }}</h5>
                <p class="contact-phone"><strong>{{ contact.phone }}</strong></p>
                <p class="contact-desc">{{ contact.description }}</p>
                <el-tag size="small" type="info">{{ contact.coverage }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="resources-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#409eff"><reading /></el-icon>
              <span>在线资源</span>
            </div>
          </template>
          <div class="resources-content">
            <div 
              class="resource-link" 
              v-for="(resource, index) in mentalHealthResources.onlineResources" 
              :key="index"
            >
              <div class="resource-header">
                <h5>{{ resource.name }}</h5>
                <el-tag size="small">{{ resource.type }}</el-tag>
              </div>
              <p>{{ resource.description }}</p>
              <el-link :href="resource.link" target="_blank" type="primary">
                访问网站 →
              </el-link>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 在线课程推荐 -->
    <el-card class="courses-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon color="#67c23a"><video-camera /></el-icon>
          <span>推荐课程</span>
        </div>
      </template>
      <div class="courses-content">
        <el-row :gutter="16">
          <el-col 
            :xs="24" 
            :sm="12" 
            :md="8" 
            v-for="(course, index) in mentalHealthResources.courses" 
            :key="index"
          >
            <div class="course-card">
              <el-tag 
                :type="course.free ? 'success' : 'warning'" 
                size="small" 
                style="margin-bottom: 8px;"
              >
                {{ course.free ? '免费' : '付费' }}
              </el-tag>
              <h5>{{ course.title }}</h5>
              <p class="course-platform">平台: {{ course.platform }}</p>
              <p class="course-instructor">讲师: {{ course.instructor }}</p>
              <el-link :href="course.link" target="_blank" type="primary">
                查看课程 →
              </el-link>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
<!-- 日记历史记录对话框 -->
    <el-dialog
      v-model="showJournalHistory"
      title="📝 情绪日记历史记录"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="journalHistoryList.length > 0">
        <el-table :data="journalHistoryList" style="width: 100%">
          <el-table-column prop="date" label="记录时间" width="200">
            <template #default="{ row }">
              {{ formatJournalTime(row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="emotion" label="情绪" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.emotion" :type="getEmotionTagType(row.emotion)">
                {{ row.emotion ? getEmotionEmoji(row.emotion) + ' ' + allEmotions.find(e => e.key === row.emotion)?.name : '-' }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="内容摘要" min-width="300">
            <template #default="{ row }">
              {{ row.content.length > 50 ? row.content.substring(0, 50) + '...' : row.content }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewJournalDetail(row)">查看详情</el-button>
              <el-button size="small" type="danger" @click="deleteJournal(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="empty-journal">
        <el-empty description="暂无日记记录" />
        <p style="text-align: center; margin-top: 1rem; color: var(--color-mahogany);">
          开始记录你的第一则情绪日记吧！
        </p>
      </div>
      <template #footer>
        <el-button @click="closeJournalHistory">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 日记详情对话框 -->
    <el-dialog
      v-model="showJournalDetail"
      title="📝 日记详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedJournal" class="journal-detail">
        <div class="detail-item">
          <span class="label">记录时间：</span>
          <span class="value">{{ formatJournalTime(selectedJournal.date) }}</span>
        </div>
        <div class="detail-item" v-if="selectedJournal.emotion">
          <span class="label">当时情绪：</span>
          <el-tag :type="getEmotionTagType(selectedJournal.emotion)">
            {{ getEmotionEmoji(selectedJournal.emotion) }} {{ allEmotions.find(e => e.key === selectedJournal.emotion)?.name }}
          </el-tag>
        </div>
        <div class="detail-content">
          <h4>内容：</h4>
          <p>{{ selectedJournal.content }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeJournalDetail">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 感恩记录历史对话框 -->
    <el-dialog
      v-model="showGratitudeHistory"
      title="📝 感恩记录历史"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="gratitudeHistoryList.length > 0">
        <el-table :data="gratitudeHistoryList" style="width: 100%">
          <el-table-column prop="date" label="记录时间" width="200">
            <template #default="{ row }">
              {{ formatJournalTime(row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="items" label="感恩事项">
            <template #default="{ row }">
              <div v-for="(item, index) in row.items" :key="index" class="gratitude-item">
                {{ index + 1 }}. {{ item }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewGratitudeDetail(row)">查看详情</el-button>
              <el-button size="small" type="danger" @click="deleteGratitude(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="empty-journal">
        <el-empty description="暂无感恩记录" />
        <p style="text-align: center; margin-top: 1rem; color: var(--color-mahogany);">
          开始记录你的第一次感恩吧！
        </p>
      </div>
      <template #footer>
        <el-button @click="closeGratitudeHistory">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 感恩记录详情对话框 -->
    <el-dialog
      v-model="showGratitudeDetail"
      title="📝 感恩记录详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedGratitude" class="journal-detail">
        <div class="detail-item">
          <span class="label">记录时间：</span>
          <span class="value">{{ formatJournalTime(selectedGratitude.date) }}</span>
        </div>
        <div class="detail-content">
          <h4>感恩事项：</h4>
          <ul>
            <li v-for="(item, index) in selectedGratitude.items" :key="index">
              {{ index + 1 }}. {{ item }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeGratitudeDetail">关闭</el-button>
      </template>
    </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useEmotionStore } from '../stores/emotion'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, Medal, Reading, WarningFilled, Refresh, ArrowDown, ArrowUp, Document, VideoCamera } from '@element-plus/icons-vue'
import {
  emotionAdviceLibrary,
  getRandomAdvice,
  emotionKnowledgeBase,
  getEmotionKnowledge,
  mentalHealthResources
} from '../data/adviceLibrary'
import { useVideoStore } from '../stores/video'
import api from '../api/client'

const emotionStore = useEmotionStore()
const videoStore = useVideoStore()

// 合并图片识别和视频分析的所有情绪数据（服务端历史优先，本地补充）
const allEmotionRecords = computed(() => {
  const records = []

  // 服务端历史记录（含图片与视频帧）
  ;(emotionStore.serverHistories || []).forEach(rec => {
    records.push({
      emotion: rec.emotion,
      emotion_cn: rec.emotion_cn,
      confidence: rec.confidence,
      timestamp: rec.created_at,
      source: (rec.input_type || 'image') === 'video' ? 'video' : 'image',
      origin: 'server'
    })
  })

  // 本地图片预测：仅补充服务端没有的记录（分页外的服务端记录由本地副本兜底展示）
  const serverHistoryIds = new Set((emotionStore.serverHistories || []).map(r => r.id))
  ;(emotionStore.predictions || []).forEach(pred => {
    if (pred.history_id && serverHistoryIds.has(pred.history_id)) return
    records.push({ ...pred, source: 'image', origin: 'local' })
  })

  // 本地视频帧：服务端没有视频记录时兜底
  const serverHasVideo = (emotionStore.serverHistories || []).some(r => (r.input_type || 'image') === 'video')
  if (!serverHasVideo && videoStore.videoHistory && Array.isArray(videoStore.videoHistory)) {
    videoStore.videoHistory.forEach(video => {
      if (video.results && video.results.timeline && Array.isArray(video.results.timeline)) {
        video.results.timeline.forEach(frame => {
          records.push({
            emotion: frame.emotion,
            emotion_cn: frame.emotion_cn,
            confidence: frame.confidence,
            timestamp: video.timestamp, // frame.timestamp 是视频内秒数，不能当日期
            source: 'video',
            video_id: video.video_id,
            origin: 'local'
          })
        })
      }
    })
  }

  return records.sort((a, b) =>
    new Date(b.timestamp) - new Date(a.timestamp)
  )
})

// 所有情绪选项
const allEmotions = [
  { key: 'happy', name: '高兴', emoji: '😊' },
  { key: 'sad', name: '悲伤', emoji: '😢' },
  { key: 'anger', name: '生气', emoji: '😠' },
  { key: 'surprised', name: '惊讶', emoji: '😲' },
  { key: 'fear', name: '害怕', emoji: '😨' },
  { key: 'disgust', name: '厌恶', emoji: '🤢' },
  { key: 'normal', name: '平静', emoji: '😐' }
]

// 当前选中的情绪 (用于无数据时手动选择)
const selectedEmotion = ref(null)

// 获取最新的情绪记录或手动选择的情绪
const latestEmotion = computed(() => {
  if (selectedEmotion.value) {
    return {
      emotion: selectedEmotion.value,
      emotion_cn: allEmotions.find(e => e.key === selectedEmotion.value)?.name || '未知',
      confidence: 1.0,
      timestamp: new Date().toISOString(),
      manual: true
    }
  }
  return allEmotionRecords.value.length > 0
    ? allEmotionRecords.value[0]
    : null
})

// 选择情绪
function selectEmotion(emotionKey) {
  selectedEmotion.value = emotionKey
  ElMessage.success(`已切换到${allEmotions.find(e => e.key === emotionKey)?.name}情绪建议`)
}

// 扩展建议相关
const showMoreAdvice = ref(false)
const allAdviceList = computed(() => {
  if (!latestEmotion.value) return []
  return emotionAdviceLibrary[latestEmotion.value.emotion] || []
})

// 存储打乱后的建议列表
const shuffledAdviceList = ref([])

// 在情绪变化时初始化打乱列表
watch(() => latestEmotion.value?.emotion, () => {
  showMoreAdvice.value = false
  // 初始化打乱列表
  shuffledAdviceList.value = [...allAdviceList.value]
  shuffleArray(shuffledAdviceList.value)
}, { immediate: true })

const displayedAdviceList = computed(() => {
  if (showMoreAdvice.value) {
    return shuffledAdviceList.value
  }
  return shuffledAdviceList.value.slice(0, 8)
})

// 打乱数组的辅助函数
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

function refreshAdviceList() {
  // 真正打乱建议列表顺序
  shuffleArray(shuffledAdviceList.value)
  ElMessage.success('已刷新建议列表')
}

// ===== 情绪统计分析 =====
// 服务端健康评估（/health/assessment，由后端基于当日情绪记录生成）
const serverAssessment = ref(null)

const emotionStats = computed(() => {
  const local = computeLocalEmotionStats()
  const a = serverAssessment.value
  if (!a || (!a.alert_title && a.health_score == null)) return local

  return {
    positiveRate: a.positive_rate != null ? Number(a.positive_rate).toFixed(1) : local.positiveRate,
    negativeRate: a.negative_rate != null ? Number(a.negative_rate).toFixed(1) : local.negativeRate,
    stability: a.stability_level || local.stability,
    stabilityRate: local.stabilityRate,
    alertTitle: a.alert_title || local.alertTitle,
    alertType: a.alert_type === 'error' ? 'error' : (a.alert_type || local.alertType),
    alertDescription: a.alert_description || local.alertDescription,
    suggestions: (Array.isArray(a.suggestions) && a.suggestions.length) ? a.suggestions : local.suggestions,
    fromServer: true
  }
})

function computeLocalEmotionStats() {
  if (allEmotionRecords.value.length === 0) {
    return {
      positiveRate: 0,
      negativeRate: 0,
      stability: '暂无数据',
      alertTitle: '暂无数据',
      alertType: 'info',
      alertDescription: '开始记录情绪以获取详细分析',
      suggestions: []
    }
  }

  // 计算积极和消极情绪占比
  let positiveCount = 0
  let negativeCount = 0
  
  allEmotionRecords.value.forEach(record => {
    if (record.emotion === 'happy' || record.emotion === 'normal') {
      positiveCount++
    } else if (['anger', 'sad', 'fear', 'disgust'].includes(record.emotion)) {
      negativeCount++
    }
  })
  
  const total = allEmotionRecords.value.length
  const positiveRate = ((positiveCount / total) * 100).toFixed(1)
  const negativeRate = ((negativeCount / total) * 100).toFixed(1)
  
  // 计算情绪稳定性（基于最近10条记录的情绪变化）
  const recentRecords = allEmotionRecords.value.slice(0, Math.min(10, total))
  let emotionChanges = 0
  for (let i = 1; i < recentRecords.length; i++) {
    if (recentRecords[i].emotion !== recentRecords[i-1].emotion) {
      emotionChanges++
    }
  }
  
  const stabilityRate = Math.max(0, 100 - (emotionChanges / recentRecords.length * 100))
  let stability = stabilityRate >= 70 ? '稳定' : stabilityRate >= 40 ? '一般' : '波动较大'
  
  // 生成分析建议
  let alertTitle = ''
  let alertType = 'info'
  let alertDescription = ''
  let suggestions = []
  
  if (positiveCount / total >= 0.7) {
    alertTitle = '✨ 心理状态良好'
    alertType = 'success'
    alertDescription = `您最近 ${positiveRate}% 的时间保持积极情绪，心理健康状态优秀！`
    suggestions = [
      '继续保持当前的生活方式和心态',
      '可以尝试帮助身边情绪低落的朋友',
      '定期回顾让你开心的事物，建立感恩日记',
      '保持规律的运动和充足的睡眠'
    ]
  } else if (positiveCount / total >= 0.4) {
    alertTitle = '⚖️ 情绪状态平衡'
    alertType = 'warning'
    alertDescription = `您的积极情绪占 ${positiveRate}%，消极情绪占 ${negativeRate}%，整体处于平衡状态。`
    suggestions = [
      '尝试增加积极活动，如运动、社交、爱好',
      '学习情绪管理技巧，提升情绪调节能力',
      '每天记录3件让你感恩的事情',
      '遇到压力时及时寻求支持和帮助'
    ]
  } else {
    alertTitle = '⚠️ 需要关注情绪健康'
    alertType = 'error'
    alertDescription = `您最近 ${negativeRate}% 的时间处于消极情绪，建议重视心理健康。`
    suggestions = [
      '建议咨询专业心理咨询师获得支持',
      '每天安排30分钟放松时间，如冥想、散步',
      '与信任的朋友或家人分享感受',
      '尝试认知行为疗法（CBT）技巧调整思维模式',
      '保持规律作息，避免熬夜和过度劳累'
    ]
  }
  
  // 如果有视频数据，添加特殊建议
  if (videoStore.videoHistory.length > 0) {
    suggestions.push(`已分析 ${videoStore.videoHistory.length} 个视频，获得更全面的情绪评估`)
  }
  
  return {
    positiveRate,
    negativeRate,
    stability,
    stabilityRate: stabilityRate.toFixed(1),
    alertTitle,
    alertType,
    alertDescription,
    suggestions
  }
}

// 情绪到emoji的映射
const emotionEmojiMap = {
  anger: '😠',
  disgust: '🤢',
  fear: '😨',
  happy: '😊',
  normal: '😐',
  sad: '😢',
  surprised: '😲'
}

function getEmotionEmoji(emotion) {
  return emotionEmojiMap[emotion] || '😐'
}

function getEmotionTagType(emotion) {
  const typeMap = {
    happy: 'success',
    normal: 'info',
    sad: 'warning',
    anger: 'danger',
    fear: 'warning',
    disgust: 'danger',
    surprised: 'primary'
  }
  return typeMap[emotion] || 'info'
}

function getProgressColor(confidence) {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 建议内容
const adviceDatabase = {
  happy: {
    title: '保持积极心态',
    description: '您现在的情绪状态很好！继续保持这种积极的心态。',
    actions: [
      '分享你的快乐给身边的人',
      '做一些你喜欢的活动',
      '记录这个美好时刻',
      '帮助他人，传递正能量'
    ]
  },
  sad: {
      title: '温柔对待自己',
      description: '悲伤是正常的情绪。给自己一些时间和空间来感受和处理。',
      actions: [
      '找信任的朋友倾诉',
      '写下你的感受',
      '做一些轻松的运动',
      '听舒缓的音乐',
      '必要时寻求专业帮助'
    ]
  },
  anger: {
    title: '冷静下来',
    description: '愤怒时做出的决定往往不理智。先让自己冷静下来。',
    actions: [
      '深呼吸10次',
      '离开当前环境',
      '做运动发泄情绪',
      '等冷静后再处理问题',
      '尝试从对方角度思考'
    ]
  },
  fear: {
    title: '面对恐惧',
    description: '恐惧常常来自未知。了解和面对可以减轻恐惧。',
    actions: [
      '分析恐惧的具体原因',
      '制定应对计划',
      '寻求支持和帮助',
      '练习放松技巧',
      '循序渐进面对恐惧'
    ]
  },
  normal: {
    title: '保持平衡',
    description: '平静的状态很好，继续保持生活的平衡。',
    actions: [
      '规律作息',
      '适量运动',
      '培养兴趣爱好',
      '维护社交关系',
      '定期自我反思'
    ]
  },
  disgust: {
    title: '接纳情绪',
    description: '厌恶是一种保护性情绪。尝试理解它的来源。',
    actions: [
      '远离引起厌恶的源头',
      '调整环境',
      '练习接纳',
      '寻找积极的方面',
      '必要时设置边界'
    ]
  },
  surprised: {
    title: '应对变化',
    description: '惊讶说明遇到了意外。让自己时间适应新情况。',
    actions: [
      '了解情况',
      '评估影响',
      '保持开放心态',
      '寻求信息和支持',
      '制定应对策略'
    ]
  }
}

const currentAdvice = ref({
  title: '欢迎来到心理健康中心',
  description: '上传照片进行情绪识别后，系统会根据您的情绪状态提供个性化的建议。',
  actions: ['点击首页开始情绪识别', '定期关注自己的情绪状态', '学习情绪管理技巧']
})

// 放松技巧
const relaxationTechniques = {
  happy: {
    title: '能量保持法',
    description: '在积极情绪中保持平衡，避免过度兴奋',
    steps: [
      '深呼吸，感受当下',
      '用笔记录美好瞬间',
      '计划接下来的活动',
      '保持规律作息'
    ]
  },
  sad: {
    title: '温柔疗愈法',
    description: '通过温和的方式照顾自己',
    steps: [
      '找一个舒适的地方坐下',
      '闭上眼睛，深呼吸5次',
      '回忆一个温暖的回忆',
      '给自己一个拥抱',
      '做一件让自己开心的小事'
    ]
  },
  anger: {
    title: '情绪释放法',
    description: '安全地释放愤怒情绪',
    steps: [
      '找个安静的地方',
      '深呼吸，数到10',
      '做剧烈运动10分钟',
      '用文字表达情绪',
      '思考解决方案'
    ]
  },
  fear: {
    title: '安全着陆法',
    description: '帮助你回到当下，感到安全',
    steps: [
      '说出5件你看到的东西',
      '说出4件你能触摸的东西',
      '说出3件你听到的声音',
      '说出2件你闻到的气味',
      '说出1件你尝到的味道'
    ]
  },
  normal: {
    title: '正念冥想法',
    description: '保持内心的平静和觉察',
    steps: [
      '找一个安静的空间',
      '舒适地坐下或躺下',
      '闭上眼睛，关注呼吸',
      '观察身体的感受',
      '保持5-10分钟'
    ]
  },
  disgust: {
    title: '净化重置法',
    description: '清理负面感受，重新开始',
    steps: [
      '洗个热水澡或洗脸',
      '整理周围环境',
      '换一套干净的衣服',
      '闻一些舒缓的香味',
      '做一些喜欢的活动'
    ]
  },
  surprised: {
    title: '适应调节法',
    description: '帮助快速适应新情况',
    steps: [
      '暂停，深呼吸',
      '收集更多信息',
      '评估情况',
      '调整心态',
      '制定下一步计划'
    ]
  }
}

const relaxationTechnique = ref(relaxationTechniques.normal)
const activeStep = ref(0)

function nextStep() {
  if (activeStep.value < relaxationTechnique.value.steps.length) {
    activeStep.value++
  } else {
    ElMessage.success('完成练习！')
    activeStep.value = 0
  }
}

function prevStep() {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 推荐资源
const resourcesDatabase = {
  happy: [
    {
      icon: '📖',
      title: '《幸福的方法》',
      description: '哈佛大学积极心理学课程',
      link: 'https://www.coursera.org/learn/positive-psychology'
    },
    {
      icon: '🎵',
      title: '愉悦音乐播放列表',
      description: '增强正面情绪的音乐推荐',
      link: 'https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC'
    },
    {
      icon: '🎨',
      title: '创意表达工作坊',
      description: '通过艺术保持积极心态',
      link: 'https://www.arttherapy.org/consumer-information/'
    }
  ],
  sad: [
    {
        icon: '📖',
        title: '《情绪急救》',
        description: '应对日常心理伤害的策略',
        link: 'https://www.amazon.cn/dp/B075F9537D'
      },
    {
      icon: '💬',
      title: '在线支持小组',
      description: '与有相似经历的人交流',
      link: 'https://www.7cuo.com/'
    },
    {
      icon: '🧘',
      title: '正念疗愈课程',
      description: '学习接纳和处理悲伤',
      link: 'https://www.100mentors.com/courses/mindfulness-meditation'
    }
  ],
  anger: [
    {
      icon: '📖',
      title: '《愤怒管理》',
      description: '了解和控制愤怒情绪',
      link: 'https://www.amazon.cn/dp/B00M9Y145S'
    },
    {
      icon: '🥊',
      title: '运动减压计划',
      description: '通过运动释放情绪',
      link: 'https://www.keep.com/course/5bf13a1d1ce1b41ce53ad12c'
    },
    {
      icon: '🎯',
      title: '冲突解决技巧',
      description: '学习有效沟通和解决问题',
      link: 'https://www.coursera.org/learn/conflict-resolution'
    }
  ],
  fear: [
    {
      icon: '📖',
      title: '《走出焦虑风暴》',
      description: 'CBT认知行为疗法入门',
      link: 'https://www.amazon.cn/dp/B017OUD6K4'
    },
    {
        icon: '🛡️',
        title: '安全感建立课程',
        description: '增强内心的安全感',
        link: 'https://www.mindful.org/category/mindfulness-practice/mindfulness-exercises/'
      },
    {
      icon: '🌟',
      title: '勇气培养计划',
      description: '逐步面对恐惧',
      link: 'https://www.ted.com/playlists/251/building_your_courage'
    }
  ],
  normal: [
    {
      icon: '📖',
      title: '《心流》',
      description: '最优体验心理学',
      link: 'https://www.amazon.cn/dp/B00K3Q8V46'
    },
    {
      icon: '🧘',
      title: '正念生活指南',
      description: '在日常中保持觉察',
      link: 'https://www.mindful.org/mindfulness-meditation-instruction-for-beginners/'
    },
    {
      icon: '🎯',
      title: '目标设定工作坊',
      description: '规划有意义的生活',
      link: 'https://www.coursera.org/learn/goal-setting-success'
    }
  ],
  disgust: [
    {
      icon: '📖',
      title: '《接纳与承诺疗法》',
      description: '学习接纳不愉快的情绪',
      link: 'https://www.amazon.cn/dp/B08R683JZ6'
    },
    {
      icon: '🌿',
      title: '环境净化指南',
      description: '创造舒适的生活空间',
      link: 'https://www.verywellmind.com/how-to-create-a-peaceful-home-3144764'
    },
    {
      icon: '💆',
      title: '感官舒缓疗法',
      description: '通过五感放松身心',
      link: 'https://positivepsychology.com/sensory-therapy/'
    }
  ],
  surprised: [
    {
      icon: '📖',
      title: '《适应力》',
      description: '如何应对变化和不确定性',
      link: 'https://www.amazon.cn/dp/B07C7K7R8L'
    },
    {
      icon: '🧠',
      title: '认知灵活性训练',
      description: '提升应对变化的能力',
      link: 'https://www.psychologytoday.com/intl/blog/think-act-be/202004/cognitive-flexibility-essential-skill-uncertain-times'
    },
    {
      icon: '🎯',
      title: '快速决策技巧',
      description: '在不确定中做出选择',
      link: 'https://www.coursera.org/learn/decision-making'
    }
  ]
}

const recommendedResources = ref(resourcesDatabase.normal)

// 情绪教育相关
const activeEducationSections = ref([])
const currentEmotionKnowledge = computed(() => {
  if (!latestEmotion.value) return null
  return getEmotionKnowledge(latestEmotion.value.emotion)
})

const recommendedBooks = computed(() => {
  if (!latestEmotion.value) return []
  const emotion = latestEmotion.value.emotion
  return mentalHealthResources.books[emotion] || []
})

// 获取新建议
function getNewAdvice() {
  if (latestEmotion.value) {
    const emotion = latestEmotion.value.emotion
    
    // 为每个情绪类型准备多个建议选项
    const adviceOptions = {
      happy: [
        {
          title: '保持积极心态',
          description: '您现在的情绪状态很好！继续保持这种积极的心态。',
          actions: [
            '分享你的快乐给身边的人',
            '做一些你喜欢的活动',
            '记录这个美好时刻',
            '帮助他人，传递正能量'
          ]
        },
        {
          title: '快乐能量提升',
          description: '利用当前的积极情绪创造更多美好的体验。',
          actions: [
            '尝试学习一项新技能',
            '与朋友计划一次愉快的活动',
            '做一些公益或帮助他人的事情',
            '设定新的目标并迈出第一步'
          ]
        },
        {
          title: '积极情绪管理',
          description: '学会有意识地维持和拓展你的积极情绪。',
          actions: [
            '练习感恩，写下3件让你感激的事',
            '进行有意义的社交互动',
            '从事让你全神贯注的活动',
            '享受大自然的美好'
          ]
        }
      ],
      sad: [
        {
          title: '温柔对待自己',
          description: '悲伤是正常的情绪。给自己一些时间和空间来感受和处理。',
          actions: [
            '找信任的朋友倾诉',
            '写下你的感受',
            '做一些轻松的运动',
            '听舒缓的音乐',
            '必要时寻求专业帮助'
          ]
        },
        {
          title: '情绪舒缓指南',
          description: '当感到悲伤时，这些方法可以帮助你缓解情绪。',
          actions: [
            '给自己一个温暖的拥抱',
            '喝一杯温热的饮品',
            '看一部温馨的电影或读一本好书',
            '进行短暂的冥想，关注呼吸',
            '到户外散散步，感受阳光和新鲜空气'
          ]
        },
        {
          title: '悲伤疗愈之旅',
          description: '允许自己悲伤，同时照顾好自己的身心。',
          actions: [
            '列出让你感到安全和舒适的事物',
            '创造一个安静舒适的空间',
            '尝试书写日记，表达内心感受',
            '温柔地肯定自己的情绪',
            '小步慢行，不要给自己太大压力'
          ]
        }
      ],
      anger: [
        {
          title: '冷静下来',
          description: '愤怒时做出的决定往往不理智。先让自己冷静下来。',
          actions: [
            '深呼吸10次',
            '离开当前环境',
            '做运动发泄情绪',
            '等冷静后再处理问题',
            '尝试从对方角度思考'
          ]
        },
        {
          title: '愤怒管理技巧',
          description: '有效管理愤怒情绪，避免伤害自己和他人。',
          actions: [
            '练习"暂停-呼吸-思考"技巧',
            '用"我"语句表达感受，避免指责',
            '进行5-10分钟的剧烈运动',
            '尝试涂鸦或撕纸等释放方式',
            '问自己："这件事一年后还重要吗？"'
          ]
        },
        {
          title: '情绪转化法',
          description: '将愤怒转化为建设性的行动。',
          actions: [
            '识别愤怒背后的需求',
            '寻找健康的情绪出口',
            '练习换位思考',
            '设定明确的边界',
            '学习沟通技巧'
          ]
        }
      ],
      fear: [
        {
          title: '面对恐惧',
          description: '恐惧常常来自未知。了解和面对可以减轻恐惧。',
          actions: [
            '分析恐惧的具体原因',
            '制定应对计划',
            '寻求支持和帮助',
            '练习放松技巧',
            '循序渐进面对恐惧'
          ]
        },
        {
          title: '恐惧缓解策略',
          description: '当感到恐惧时，这些方法可以帮助你恢复平静。',
          actions: [
            '进行渐进式肌肉放松',
            '练习4-7-8呼吸法',
            '使用五感官锚定技术',
            '将恐惧写下来，然后理性分析',
            '寻求信任的人的陪伴'
          ]
        },
        {
          title: '勇气培养计划',
          description: '逐步建立面对恐惧的勇气。',
          actions: [
            '从小事开始挑战自己',
            '记录每次面对恐惧的成功经验',
            '学习相关知识，减少未知感',
            '培养积极的自我对话',
            '想象自己成功克服恐惧的场景'
          ]
        }
      ],
      normal: [
        {
          title: '保持平衡',
          description: '平静的状态很好，继续保持生活的平衡。',
          actions: [
            '规律作息',
            '适量运动',
            '培养兴趣爱好',
            '维护社交关系',
            '定期自我反思'
          ]
        },
        {
          title: '平静生活指南',
          description: '在平凡中发现美好，保持内心的平和。',
          actions: [
            '练习正念饮食',
            '进行10分钟的日常冥想',
            '培养一个小的健康习惯',
            '花时间与自然连接',
            '记录生活中的小确幸'
          ]
        },
        {
          title: '心灵滋养计划',
          description: '在平静的状态下滋养自己的心灵。',
          actions: [
            '阅读一本启发性的书籍',
            '学习一项新的放松技巧',
            '尝试创造性表达',
            '进行自我探索和反思',
            '建立健康的生活仪式'
          ]
        }
      ],
      disgust: [
        {
          title: '接纳情绪',
          description: '厌恶是一种保护性情绪。尝试理解它的来源。',
          actions: [
            '远离引起厌恶的源头',
            '调整环境',
            '练习接纳',
            '寻找积极的方面',
            '必要时设置边界'
          ]
        },
        {
          title: '情绪净化法',
          description: '当感到厌恶时，这些方法可以帮助你重新找回舒适感。',
          actions: [
            '创造一个干净整洁的环境',
            '进行呼吸练习，释放负面情绪',
            '练习情绪接纳冥想',
            '思考情绪背后的信息',
            '寻找替代视角'
          ]
        },
        {
          title: '界限设定指南',
          description: '学会识别和维护自己的边界，减少厌恶感。',
          actions: [
            '明确自己的底线和边界',
            '学习礼貌而坚定地表达拒绝',
            '关注自己的身体信号',
            '创造安全的空间',
            '培养自我照顾的习惯'
          ]
        }
      ],
      surprised: [
        {
          title: '应对变化',
          description: '惊讶说明遇到了意外。让自己时间适应新情况。',
          actions: [
            '了解情况',
            '评估影响',
            '保持开放心态',
            '寻求信息和支持',
            '制定应对策略'
          ]
        },
        {
          title: '适应性思维训练',
          description: '增强对意外情况的适应能力。',
          actions: [
            '练习灵活思考',
            '关注可以控制的部分',
            '寻找机会和积极面',
            '深呼吸，保持冷静',
            '向他人寻求不同视角'
          ]
        },
        {
          title: '变化应对策略',
          description: '当生活出现意外变化时的应对方法。',
          actions: [
            '给自己时间消化信息',
            '区分事实和想象',
            '制定短期行动计划',
            '保持日常习惯的稳定性',
            '庆祝自己的适应能力'
          ]
        }
      ]
    }
    
    // 随机选择一个建议
    const availableAdvice = adviceOptions[emotion] || adviceOptions.normal
    const randomIndex = Math.floor(Math.random() * availableAdvice.length)
    currentAdvice.value = availableAdvice[randomIndex]
    
    // 为放松技巧也添加随机选择
    const techniqueOptions = {
      happy: relaxationTechniques.happy,
      sad: relaxationTechniques.sad,
      anger: relaxationTechniques.anger,
      fear: relaxationTechniques.fear,
      normal: relaxationTechniques.normal,
      disgust: relaxationTechniques.disgust,
      surprised: relaxationTechniques.surprised
    }
    
    // 随机调整技巧步骤的顺序或内容，增加变化感
    const selectedTechnique = JSON.parse(JSON.stringify(techniqueOptions[emotion] || techniqueOptions.normal))
    if (selectedTechnique.steps.length > 3) {
      // 随机调整步骤顺序，但保持第一步和最后一步不变
      const middleSteps = selectedTechnique.steps.slice(1, -1)
      // Fisher-Yates 洗牌算法
      for (let i = middleSteps.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[middleSteps[i], middleSteps[j]] = [middleSteps[j], middleSteps[i]]
      }
      selectedTechnique.steps = [selectedTechnique.steps[0], ...middleSteps, selectedTechnique.steps[selectedTechnique.steps.length - 1]]
    }
    
    relaxationTechnique.value = selectedTechnique
    
    // 随机打乱推荐资源的顺序
    const resources = resourcesDatabase[emotion] || resourcesDatabase.normal
    recommendedResources.value = [...resources].sort(() => Math.random() - 0.5)
    
    activeStep.value = 0
    activeEducationSections.value = []  // 重置教育板块
    ElMessage.success('已获取新建议')
  } else {
    ElMessage.warning('请先进行情绪识别')
  }
}

// 呼吸训练
const isBreathing = ref(false)
const breathingText = ref('准备')
const breathingInstruction = ref('选择一种呼吸法，点击开始按钮')
const selectedBreathingType = ref('478')
let breathingTimer = null

const breathingTypes = {
  '478': {
    name: '4-7-8呼吸法',
    description: '由Dr. Andrew Weil开发，可快速放松神经系统',
    benefit: '2分钟内降低焦虑，改善睡眠',
    phases: [
      { text: '吸气', duration: 4000, instruction: '用鼻子吸气，数到4...' },
      { text: '屏息', duration: 7000, instruction: '屏住呼吸，数到7...' },
      { text: '呼气', duration: 8000, instruction: '用嘴呼气，发"呼"声，数到8...' }
    ]
  },
  'box': {
    name: '箱式呼吸',
    description: '美国海豹突击队使用的技术，提高专注和抗压能力',
    benefit: '快速冷静，适合高压情况',
    phases: [
      { text: '吸气', duration: 4000, instruction: '吸气，数到4...' },
      { text: '屏息', duration: 4000, instruction: '屏住呼吸，数到4...' },
      { text: '呼气', duration: 4000, instruction: '呼气，数到4...' },
      { text: '屏息', duration: 4000, instruction: '屏住呼吸，数到4...' }
    ]
  },
  'resonant': {
    name: '共振呼吸',
    description: '每分钟5.5次呼吸，优化心率变异性',
    benefit: '深度放松，改善心脏健康',
    phases: [
      { text: '吸气', duration: 5500, instruction: '缓慢吸气，数到5.5...' },
      { text: '呼气', duration: 5500, instruction: '缓慢呼气，数到5.5...' }
    ]
  }
}

const currentBreathingInfo = computed(() => {
  return breathingTypes[selectedBreathingType.value]
})

function startBreathing() {
  isBreathing.value = true
  let phase = 0
  const phases = breathingTypes[selectedBreathingType.value].phases
  
  function nextPhase() {
    if (!isBreathing.value) return
    
    const current = phases[phase % phases.length]
    breathingText.value = current.text
    breathingInstruction.value = current.instruction
    
    breathingTimer = setTimeout(() => {
      phase++
      nextPhase()
    }, current.duration)
  }
  
  nextPhase()
}

function stopBreathing() {
  isBreathing.value = false
  breathingText.value = '准备'
  breathingInstruction.value = '选择一种呼吸法，点击开始按钮'
  if (breathingTimer) {
    clearTimeout(breathingTimer)
    breathingTimer = null
  }
}

// 离开页面时终止呼吸训练的 setTimeout 链，否则练习会话会在后台无限延续
onUnmounted(() => {
  stopBreathing()
})

// 渐进式肌肉放松
const pmrStep = ref(0)
const pmrSequence = [
  '双手:握紧拳头5秒,感受紧张,然后完全放松10秒',
  '前臂:弯曲手腕向后,紧张5秒,放松10秒',
  '上臂:绷紧肱二头肌,保持5秒,放松10秒',
  '肩部:耸肩触耳,保持5秒,让肩膀自然下落',
  '面部:皱眉、闭眼、咬牙,保持5秒,放松面部',
  '胸部:深吸气使胸部紧张,保持5秒,慢慢呼气',
  '腹部:绷紧腹肌,保持5秒,放松',
  '臀部和大腿:绷紧臀大肌,保持5秒,放松',
  '小腿:绷直脚尖向前,保持5秒,放松',
  '脚部:弯曲脚趾,保持5秒,完全放松全身'
]

function nextPmrStep() {
  if (pmrStep.value < pmrSequence.length - 1) {
    pmrStep.value++
  } else {
    ElMessage.success('🎉 完成渐进式肌肉放松！感觉如何？')
    pmrStep.value = 0
  }
}

function prevPmrStep() {
  if (pmrStep.value > 0) {
    pmrStep.value--
  }
}

function resetPmr() {
  pmrStep.value = 0
  ElMessage.info('已重置到第一步')
}

// 接地技术
const groundingInputs = ref(['', '', '', '', ''])
const groundingSteps = [
  { number: 5, title: '看到的5样东西', placeholder: '例如: 桌子、窗户、杯子、书、笔' },
  { number: 4, title: '能触摸的4样东西', placeholder: '例如: 椅子、地板、衣服、手机' },
  { number: 3, title: '听到的3种声音', placeholder: '例如: 空调声、汽车声、鸟叫' },
  { number: 2, title: '闻到的2种气味', placeholder: '例如: 咖啡、空气清新剂' },
  { number: 1, title: '尝到的1种味道', placeholder: '例如: 口中的茶味' }
]

function completeGrounding() {
  const filled = groundingInputs.value.filter(input => input.trim()).length
  if (filled >= 3) {
    ElMessage.success('✅ 很好！你已经回到当下,感觉是否平静了一些？')
    // 保存记录
    const records = JSON.parse(localStorage.getItem('groundingRecords') || '[]')
    records.push({
      date: new Date().toISOString(),
      inputs: groundingInputs.value
    })
    localStorage.setItem('groundingRecords', JSON.stringify(records))
  } else {
    ElMessage.warning('请至少完成3项练习')
  }
}

// 冥想
const activeTab = ref('breathing')
const selectedMeditation = ref('')
const meditations = [
  {
    id: 'body-scan',
    title: '身体扫描冥想',
    description: '通过系统地关注身体各部位的感受，释放身体紧张，达到深度放松状态。适合睡前或感到压力时练习。',
    video: '/videos/身体扫描冥想.mp4',
    duration: '约15分钟',
    poster: ''
  },
  {
    id: 'breathing',
    title: '呼吸观察冥想',
    description: '通过专注于自然呼吸，训练注意力的稳定性，帮助平静思绪，缓解焦虑。适合初学者入门练习。',
    video: '/videos/呼吸观察冥想.mp4',
    duration: '约10分钟',
    poster: ''
  },
  {
    id: 'loving-kindness',
    title: '慈悲冥想',
    description: '通过系统化的祝福练习，培养对自己和他人的善意与慈悲，提升积极情绪和人际关系质量。',
    video: '/videos/慈悲冥想.mp4',
    duration: '约12分钟',
    poster: ''
  }
]

function getCurrentMeditation() {
  return meditations.find(m => m.id === selectedMeditation.value) || meditations[0]
}

// 感恩日记
const gratitudeList = ref(['', '', ''])
const showGratitudeHistory = ref(false)
const gratitudeHistoryList = ref([])
const selectedGratitude = ref(null)
const showGratitudeDetail = ref(false)

async function saveGratitude() {
  if (gratitudeList.value.some(item => item.trim())) {
    try {
      // 保存到MySQL数据库
      const items = gratitudeList.value.filter(item => item.trim())
      const result = await saveGratitudeApi({ items })
      
      if (result.success) {
        // 同时保存到localStorage作为本地备份
        const gratitudes = JSON.parse(localStorage.getItem('gratitudes') || '[]')
        gratitudes.push({
          id: result.data.id,
          date: result.data.date,
          items: items
        })
        localStorage.setItem('gratitudes', JSON.stringify(gratitudes))
        
        ElMessage.success('感恩记录已保存！')
        gratitudeList.value = ['', '', '']
      } else {
        ElMessage.error(result.error || '保存失败')
      }
    } catch (error) {
      console.error('保存感恩记录失败:', error)
      ElMessage.error('保存失败，请检查网络连接')
    }
  } else {
    ElMessage.warning('请至少写一件感恩的事')
  }
}

async function loadGratitudeHistory() {
  try {
    // 从MySQL数据库加载
    const result = await getGratitudes(50)
    
    if (result.success) {
      gratitudeHistoryList.value = result.data
      
      // 同步到localStorage作为备份
      localStorage.setItem('gratitudes', JSON.stringify(result.data))
    } else {
      // 如果API失败，从localStorage加载
      const gratitudes = JSON.parse(localStorage.getItem('gratitudes') || '[]')
      gratitudes.sort((a, b) => new Date(b.date) - new Date(a.date))
      gratitudeHistoryList.value = gratitudes
    }
  } catch (error) {
    console.error('加载感恩记录失败:', error)
    // API失败时从localStorage加载
    const gratitudes = JSON.parse(localStorage.getItem('gratitudes') || '[]')
    gratitudes.sort((a, b) => new Date(b.date) - new Date(a.date))
    gratitudeHistoryList.value = gratitudes
  }
}

function viewGratitudeHistory() {
  loadGratitudeHistory()
  showGratitudeHistory.value = true
}

function closeGratitudeHistory() {
  showGratitudeHistory.value = false
}

function viewGratitudeDetail(gratitude) {
  selectedGratitude.value = gratitude
  showGratitudeDetail.value = true
}

function closeGratitudeDetail() {
  showGratitudeDetail.value = false
}

async function deleteGratitude(gratitudeId) {
  ElMessageBox.confirm('确定要删除这条感恩记录吗？此操作不可恢复！', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 从MySQL数据库删除
      const result = await deleteGratitudeApi(gratitudeId)
      
      if (result.success) {
        // 同时从localStorage删除
        const gratitudes = JSON.parse(localStorage.getItem('gratitudes') || '[]')
        const filteredGratitudes = gratitudes.filter(g => g.id !== gratitudeId)
        localStorage.setItem('gratitudes', JSON.stringify(filteredGratitudes))
        
        loadGratitudeHistory() // 重新加载历史记录
        ElMessage.success('感恩记录已删除')
      } else {
        ElMessage.error(result.error || '删除失败')
      }
    } catch (error) {
      console.error('删除感恩记录失败:', error)
      ElMessage.error('删除失败，请检查网络连接')
    }
  }).catch(() => {})
}

// 情绪日记
const journalContent = ref('')
const showJournalHistory = ref(false)
const journalHistoryList = ref([])
const selectedJournal = ref(null)
const showJournalDetail = ref(false)

// 导入日记API和感恩记录API
import { 
  saveJournal as saveJournalApi, 
  getJournals, 
  deleteJournal as deleteJournalApi,
  saveGratitude as saveGratitudeApi,
  getGratitudes,
  deleteGratitude as deleteGratitudeApi
} from '@/api/health'

async function saveJournal() {
  if (journalContent.value.trim()) {
    try {
      // 保存到MySQL数据库
      const result = await saveJournalApi({
        content: journalContent.value,
        emotion: latestEmotion.value?.emotion,
        emotion_cn: latestEmotion.value?.emotion_cn
      })
      
      if (result.success) {
        // 同时保存到localStorage作为本地备份
        const journals = JSON.parse(localStorage.getItem('journals') || '[]')
        journals.push({
          id: result.data.id,
          date: result.data.date,
          content: journalContent.value,
          emotion: latestEmotion.value?.emotion
        })
        localStorage.setItem('journals', JSON.stringify(journals))
        
        ElMessage.success('日记已保存到云端！')
        journalContent.value = ''
      } else {
        throw new Error(result.error || '保存失败')
      }
    } catch (error) {
      console.error('保存日记失败:', error)
      // 如果网络失败，至少保存到本地
      const journals = JSON.parse(localStorage.getItem('journals') || '[]')
      journals.push({
        id: Date.now(),
        date: new Date().toISOString(),
        content: journalContent.value,
        emotion: latestEmotion.value?.emotion
      })
      localStorage.setItem('journals', JSON.stringify(journals))
      ElMessage.warning('网络错误，日记已保存到本地')
      journalContent.value = ''
    }
  } else {
    ElMessage.warning('请写下你的感受')
  }
}

async function loadJournalHistory() {
  try {
    // 从MySQL数据库加载
    const result = await getJournals(100, 0)
    
    if (result.success) {
      journalHistoryList.value = result.data
      
      // 同步到localStorage
      localStorage.setItem('journals', JSON.stringify(result.data))
    } else {
      throw new Error(result.error || '加载失败')
    }
  } catch (error) {
    console.error('加载日记失败:', error)
    // 如果网络失败，从本地加载
    const journals = JSON.parse(localStorage.getItem('journals') || '[]')
    journals.sort((a, b) => new Date(b.date) - new Date(a.date))
    journalHistoryList.value = journals
    ElMessage.warning('从本地加载日记')
  }
}

async function viewJournalHistory() {
  await loadJournalHistory()
  showJournalHistory.value = true
}

function closeJournalHistory() {
  showJournalHistory.value = false
}

function viewJournalDetail(journal) {
  selectedJournal.value = journal
  showJournalDetail.value = true
}

function closeJournalDetail() {
  showJournalDetail.value = false
}

async function deleteJournal(journalId) {
    ElMessageBox.confirm('确定要删除这条日记吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      try {
        // 从MySQL数据库删除
        const result = await deleteJournalApi(journalId)
        
        if (result.success) {
          // 同时从localStorage删除
          const journals = JSON.parse(localStorage.getItem('journals') || '[]')
          const filteredJournals = journals.filter(j => j.id !== journalId)
          localStorage.setItem('journals', JSON.stringify(filteredJournals))
          
          await loadJournalHistory() // 重新加载历史记录
          ElMessage.success('日记已删除')
        } else {
          throw new Error(result.error || '删除失败')
        }
      } catch (error) {
        console.error('删除日记失败:', error)
        // 如果网络失败，至少从本地删除
        const journals = JSON.parse(localStorage.getItem('journals') || '[]')
        const filteredJournals = journals.filter(j => j.id !== journalId)
        localStorage.setItem('journals', JSON.stringify(filteredJournals))
        loadJournalHistory()
        ElMessage.warning('网络错误，已从本地删除')
      }
    }).catch(() => {})
  }

// 格式化日记时间显示
function formatJournalTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 复用现有的getEmotionTagType函数，不再重复声明

// 复用现有的getEmotionEmoji函数，不再重复声明

// 初始化
onMounted(async () => {
  getNewAdvice()

  // 拉取服务端历史与健康评估（失败时静默降级为本地数据）
  try {
    await emotionStore.fetchServerHistories(100, 3)
  } catch (error) {
    console.warn('服务端历史拉取失败，使用本地数据', error)
  }
  try {
    const response = await api.get('/health/assessment')
    const data = response.data?.data
    serverAssessment.value = Array.isArray(data) ? data[data.length - 1] : data || null
  } catch (error) {
    console.warn('健康评估获取失败，使用本地计算', error)
  }
})
</script>

<style scoped>
.health-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
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

.emotion-status-card {
  margin-bottom: 2rem;
}

.emotion-status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.emotion-display {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.emotion-emoji {
  font-size: 5rem;
}

.emotion-details h3 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.emotion-time {
  color: var(--color-mahogany);
  margin-top: 0.5rem;
}

.advice-section {
  margin-bottom: 2rem;
}

.advice-card {
  height: 100%;
  margin-bottom: 1rem;
}

.more-advice-card {
  margin-bottom: 2rem;
}

.advice-list-container {
  padding: 1rem 0;
}

.advice-item {
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  margin-bottom: 1rem;
  transition: all 0.3s;
  min-height: 120px;
}

.advice-item:hover {
  background: #e8eaed;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.advice-item p {
  color: var(--color-ink);
  line-height: 1.6;
  margin: 0;
  font-size: 0.9rem;
}

.empty-state-card {
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.advice-content h4 {
  color: var(--color-ink);
  margin-bottom: 0.75rem;
}

.advice-content p {
  color: var(--color-mahogany);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.advice-content ul {
  padding-left: 1.5rem;
}

.advice-content li {
  color: var(--color-mahogany);
  margin: 0.5rem 0;
  line-height: 1.6;
}

.technique-steps {
  margin-top: 1rem;
}

.step-controls {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.resource-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  transition: all 0.3s;
}

.resource-item:hover {
  background: #e8eaed;
  transform: translateX(4px);
}

.resource-icon {
  font-size: 2rem;
}

.resource-info h5 {
  color: var(--color-ink);
  margin-bottom: 0.5rem;
}

.resource-info p {
  color: var(--color-mahogany);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.toolbox-card {
  margin-bottom: 2rem;
}

.breathing-exercise {
  text-align: center;
  padding: 2rem;
}

.breathing-circle {
  width: 200px;
  height: 200px;
  margin: 0 auto 2rem;
  border-radius: 50%;
  background: var(--el-color-primary-light-9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  transition: all 4s ease-in-out;
}

.breathing-circle.breathing {
  transform: scale(1.3);
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.5);
}

.breathing-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.breathing-instruction {
  color: var(--color-mahogany);
  font-size: 1.1rem;
  margin-top: 1rem;
}

.breathing-info {
  text-align: center;
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.breathing-info p {
  margin: 0.5rem 0;
  color: var(--color-mahogany);
}

.benefit-text {
  color: #67c23a !important;
  font-weight: 500;
}

/* PMR样式 */
.pmr-exercise {
  padding: 1rem;
}

.pmr-intro {
  text-align: center;
  color: var(--color-mahogany);
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 8px;
}

.pmr-sequence {
  margin: 2rem 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.pmr-controls {
  text-align: center;
  margin-top: 2rem;
}

.pmr-tip {
  text-align: center;
  color: #e6a23c;
  margin-top: 1.5rem;
  font-weight: 500;
}

/* 接地技术样式 */
.grounding-exercise {
  padding: 1rem;
}

.grounding-intro {
  text-align: center;
  color: var(--color-mahogany);
  margin-bottom: 1.5rem;
}

.grounding-steps {
  max-width: 600px;
  margin: 0 auto 2rem;
}

.grounding-step {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.step-number {
  width: 32px;
  height: 32px;
  background: var(--el-color-primary-light-9);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.step-header h5 {
  margin: 0;
  color: var(--color-ink);
  font-size: 1rem;
}

.grounding-benefit {
  text-align: center;
  color: #67c23a;
  margin-top: 1.5rem;
  font-weight: 500;
}

.grounding-exercise .el-button--primary {
  display: block;
  margin: 0 auto;
}

.meditation-guide {
  padding: 1rem;
}

.meditation-content {
  margin-top: 2rem;
}

.meditation-audio {
  margin-top: 1rem;
}

.meditation-audio audio {
  width: 100%;
}

.positive-exercise,
.emotion-journal {
  padding: 1rem;
}

.journal-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

.gratitude-item {
  padding: 4px 0;
  line-height: 1.5;
}

.emergency-card {
  background: linear-gradient(135deg, #fff5f5 0%, #fee 100%);
  margin-bottom: 2rem;
}

.emergency-content p {
  color: var(--color-mahogany);
  margin-bottom: 1.5rem;
  font-size: 1.05rem;
}

.emergency-contacts {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contact-item {
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.contact-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.contact-item h5 {
  color: var(--color-ink);
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.contact-phone {
  margin: 0.5rem 0 !important;
}

.contact-phone strong {
  color: #f56c6c;
  font-size: 1.3rem;
}

.contact-desc {
  color: var(--color-mahogany);
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

/* 在线资源卡片 */
.resources-card {
  margin-bottom: 2rem;
}

.resources-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.resource-link {
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  transition: all 0.3s;
}

.resource-link:hover {
  background: #e8eaed;
  transform: translateX(4px);
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.resource-header h5 {
  margin: 0;
  color: var(--color-ink);
}

.resource-link p {
  color: var(--color-mahogany);
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

/* 课程卡片 */
.courses-card {
  margin-bottom: 2rem;
}

.courses-content {
  padding: 1rem 0;
}

.course-card {
  padding: 1.5rem;
  background: var(--el-color-primary-light-9);
  border-radius: 12px;
  height: 100%;
  transition: all 0.3s;
}

.course-card:hover {
  background: #e8eaed;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.course-card h5 {
  color: var(--color-ink);
  margin: 0.5rem 0;
  font-size: 1rem;
}

.course-platform,
.course-instructor {
  color: var(--color-mahogany);
  font-size: 0.85rem;
  margin: 0.25rem 0;
}

/* 情绪教育卡片样式 */
.emotion-education-card {
  margin-bottom: 2rem;
}

.education-content {
  padding: 1rem 0;
}

.education-intro {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--color-accent)15 0%, var(--color-accent)15 100%);
  border-radius: 12px;
  border-left: 4px solid var(--color-accent);
}

.education-intro h4 {
  color: var(--color-ink);
  font-size: 1.3rem;
  margin-bottom: 0.75rem;
}

.intro-text {
  color: var(--color-mahogany);
  line-height: 1.8;
  font-size: 1rem;
}

.section-content {
  color: var(--color-mahogany);
  line-height: 1.8;
  padding: 1rem;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  margin: 0.5rem 0;
}

.knowledge-tips {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fff7e6;
  border-radius: 12px;
  border-left: 4px solid #e6a23c;
}

.knowledge-tips h5 {
  color: var(--color-ink);
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.knowledge-tips ul {
  list-style: none;
  padding: 0;
}

.knowledge-tips li {
  color: var(--color-mahogany);
  line-height: 1.8;
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}

.knowledge-tips li::before {
  content: "▸";
  position: absolute;
  left: 0;
  color: #e6a23c;
  font-weight: bold;
}

.recommended-books {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f0f9ff;
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.recommended-books h5 {
  color: var(--color-ink);
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.book-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.book-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  transition: all 0.3s;
}

.book-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.book-info {
  flex: 1;
}

.book-info h6 {
  color: var(--color-ink);
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.book-author {
  color: var(--color-mahogany);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.book-desc {
  color: var(--color-mahogany);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .emotion-status-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .emotion-display {
    flex-direction: column;
    text-align: center;
  }
  
  .breathing-circle {
    width: 150px;
    height: 150px;
  }

  .book-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .education-intro,
  .knowledge-tips,
  .recommended-books {
    padding: 1rem;
  }
}
    /* 冥想引导样式 */
    .meditation-guide {
      padding: 20px;
    }
    
    .meditation-content {
      margin-top: 20px;
    }
    
    .meditation-description {
      font-size: 15px;
      line-height: 1.6;
      color: var(--color-mahogany);
      margin-bottom: 10px;
    }
    
    .meditation-duration {
      font-size: 14px;
      color: var(--color-mahogany);
      margin-bottom: 15px;
    }
    
    .meditation-video-container {
      background: var(--el-color-primary-light-9);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      display: flex;
      justify-content: center;
      transition: all 0.3s ease;
    }
    
    .meditation-video-container:hover {
      box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
    }
    
    .meditation-video {
      width: 100%;
      max-width: 800px;
      border-radius: 6px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    .meditation-tips {
      background: #ecf5ff;
      border: 1px solid #d9ecff;
      border-radius: 6px;
      padding: 15px 20px;
    }
    
    .meditation-tips h5 {
      color: #1890ff;
      margin-top: 0;
      margin-bottom: 10px;
    }
    
    .meditation-tips ul {
      padding-left: 20px;
      margin-bottom: 0;
    }
    
    .meditation-tips li {
      color: var(--color-mahogany);
      margin-bottom: 5px;
      font-size: 14px;
    }
    
    .meditation-tips li:last-child {
      margin-bottom: 0;
    }
    
    /* 深色模式下的冥想样式 */
    .dark .meditation-video-container {
      background: #2c3e50;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3);
    }
    
    .dark .meditation-video-container:hover {
      box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.4);
    }
    
    .dark .meditation-description,
    .dark .meditation-tips li {
      color: var(--color-mahogany);
    }
    
    .dark .meditation-duration {
      color: var(--color-mahogany);
    }
    
    .dark .meditation-tips {
      background: #1f2937;
      border-color: #374151;
    }
    
    .dark .meditation-tips h5 {
      color: #409eff;
    }
    
    /* 响应式布局 */
    @media (max-width: 768px) {
      .meditation-guide {
        padding: 15px;
      }
      
      .meditation-video-container {
        padding: 15px;
      }
      
      .meditation-video {
        width: 100%;
      }
      
      .meditation-tips {
        padding: 12px 15px;
      }
    }
    
    /* 情绪趋势卡片 */
    .emotion-trend-card {
      margin-bottom: 2rem;
    }
    
    .trend-content {
      padding: 10px 0;
    }
    
    .trend-stat {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px;
      background: var(--el-color-primary-light-9);
      border-radius: 10px;
      margin-bottom: 15px;
      transition: all 0.3s;
    }
    
    .trend-stat:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    
    .trend-icon {
      width: 50px;
      height: 50px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;
    }
    
    .trend-info {
      flex: 1;
    }
    
    .trend-label {
      font-size: 13px;
      color: var(--color-mahogany);
      margin-bottom: 5px;
    }
    
    .trend-value {
      font-size: 24px;
      font-weight: bold;
      color: var(--color-ink);
    }
  </style>
