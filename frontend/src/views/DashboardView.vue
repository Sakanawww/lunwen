<template>
  <div class="dashboard-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="page-title">
        <h1>学情数据看板</h1>
        <p class="page-subtitle">实时查看课程学习数据与 AI 助教使用情况</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-secondary" @click="refreshData" :disabled="isLoading">
          <i class="ri-refresh-line" :class="{ 'spin': isLoading }"></i>
          <span>刷新</span>
        </button>
        <button class="btn btn-primary" @click="exportReport">
          <i class="ri-download-line"></i>
          <span>导出报告</span>
        </button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label for="courseSelect"><i class="ri-book-open-line"></i>选择课程</label>
        <DropdownSelect
          v-model="selectedCourseId"
          :options="courseOptions"
          placeholder="选择课程…"
        />
      </div>
      <div class="filter-group">
        <label for="timeRange"><i class="ri-time-line"></i>时间范围</label>
        <DropdownSelect
          v-model="selectedTimeRange"
          :options="timeRangeOptions"
          placeholder="选择时间范围…"
        />
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card" title="点击查看选课学生明细">
        <div class="metric-top">
          <div class="metric-value">{{ metrics.totalStudents }}</div>
          <div class="metric-label">选课人数</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-top">
          <div class="metric-value">{{ metrics.submissionCount }}</div>
          <div class="metric-label">作业提交</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-top">
          <div class="metric-value">{{ metrics.gradedCount }}</div>
          <div class="metric-label">已批改</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-top">
          <div class="metric-value">{{ metrics.avgScore }}</div>
          <div class="metric-label">平均分</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-top">
          <div class="metric-value">{{ metrics.chatCount }}</div>
          <div class="metric-label">答疑消息</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-top">
          <div class="metric-value">{{ metrics.activeStudents }}</div>
          <div class="metric-label">活跃学生</div>
        </div>
      </div>
    </div>

    <!-- 图表行 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <i class="ri-trend-up-line"></i>学习趋势
          </div>
          <div class="chart-tabs">
            <button
              v-for="tab in trendTabs"
              :key="tab.days"
              class="chart-tab"
              :class="{ active: selectedTrendDays === tab.days }"
              @click="selectedTrendDays = tab.days"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
        <div class="chart-container">
          <VChart :option="trendOption" auto-resize />
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <i class="ri-pie-chart-line"></i>作业完成情况
          </div>
        </div>
        <div class="chart-container">
          <VChart :option="completionOption" auto-resize />
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <i class="ri-book-open-line"></i>知识库使用
          </div>
        </div>
        <div class="chart-container tall">
          <VChart :option="kbOption" auto-resize />
        </div>
      </div>

      <div class="hot-questions-card">
        <div class="card-header">
          <div class="card-title">
            <i class="ri-fire-line" style="color: rgb(var(--destructive))"></i>
            热门问题 TOP 8
          </div>
          <router-link to="/dashboard/hot-questions" class="card-link">查看全部 →</router-link>
        </div>
        <div class="question-list">
          <div
            v-for="(q, index) in hotQuestions"
            :key="q.id"
            class="question-item"
            :class="'fade-in'"
            :style="{ animationDelay: `${index * 0.05}s` }"
          >
            <div class="question-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
            <div class="question-content">
              <div class="question-text">{{ q.text }}</div>
              <div class="question-meta">
                <span><i class="ri-user-line"></i> {{ q.studentCount }}人提问</span>
                <span class="question-trend" :class="q.trend > 0 ? 'up' : 'down'">
                  <i :class="q.trend > 0 ? 'ri-arrow-up-line' : 'ri-arrow-down-line'"></i>
                  {{ Math.abs(q.trend) }}%
                </span>
              </div>
            </div>
          </div>
          <div v-if="hotQuestions.length === 0" class="empty-state">
            <i class="ri-inbox-line"></i>
            <p>暂无热门问题</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'

interface Course {
  id: number
  name: string
}

interface Metric {
  totalStudents: number
  submissionCount: number
  gradedCount: number
  avgScore: string
  chatCount: number
  activeStudents: number
}

interface HotQuestion {
  id: number
  text: string
  studentCount: number
  trend: number
}

const courseStore = useCourseStore()

// 状态
const isLoading = ref(false)
const selectedCourseId = ref<number | null>(null)
const selectedTimeRange = ref<string>('30')
const selectedTrendDays = ref(7)

// 指标数据
const metrics = reactive<Metric>({
  totalStudents: 0,
  submissionCount: 0,
  gradedCount: 0,
  avgScore: '0',
  chatCount: 0,
  activeStudents: 0
})

// 选项
const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

const timeRangeOptions = [
  { value: '7', label: '最近 7 天' },
  { value: '30', label: '最近 30 天' },
  { value: '90', label: '最近 90 天' }
]

const trendTabs = [
  { days: 7, label: '周' },
  { days: 30, label: '月' },
  { days: 90, label: '季' },
  { days: 0, label: '全部' }
]

// 热门问题
const hotQuestions = ref<HotQuestion[]>([])

// 图表数据
const trendOption = ref()
const completionOption = ref()
const kbOption = ref()

// 不同时间范围的数据
const trendDataMap: Record<number, number[]> = {
  7: [120, 132, 101, 134, 90, 230, 210],
  30: [150, 180, 140, 160, 120, 200, 180, 160, 140, 170, 190, 210, 180, 160, 140, 170, 190, 210, 230, 200, 180, 160, 140, 170, 190, 210, 230, 250, 220, 200],
  90: [150, 180, 140, 160, 120, 200, 180],
  0: [100, 120, 150, 180, 200, 220, 250, 280, 300, 320, 350, 380]
}

const trendDateLabels: Record<number, string[]> = {
  7: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  30: Array.from({ length: 30 }, (_, i) => `${i + 1}日`),
  90: ['第 1 周', '第 2 周', '第 3 周', '第 4 周', '第 5 周', '第 6 周', '第 7 周', '第 8 周', '第 9 周', '第 10 周', '第 11 周', '第 12 周'],
  0: ['1 月', '2 月', '3 月', '4 月', '5 月', '6 月', '7 月', '8 月', '9 月', '10 月', '11 月', '12 月']
}

// 不同课程的数据
const courseDataMap: Record<number, { metrics: Partial<Metric>, questions: HotQuestion[] }> = {
  1: { // 计算机科学基础
    metrics: { totalStudents: 42, submissionCount: 156, gradedCount: 148, avgScore: '85.6', chatCount: 328, activeStudents: 38 },
    questions: [
      { id: 1, text: '如何理解机器学习中的过拟合问题？', studentCount: 12, trend: 15 },
      { id: 2, text: 'Python 装饰器的使用场景有哪些？', studentCount: 9, trend: 8 },
    ]
  },
  2: { // 数据结构与算法
    metrics: { totalStudents: 38, submissionCount: 142, gradedCount: 135, avgScore: '82.3', chatCount: 285, activeStudents: 32 },
    questions: [
      { id: 1, text: '快速排序的实现原理？', studentCount: 15, trend: 20 },
      { id: 2, text: '二叉树遍历的递归与非递归实现？', studentCount: 11, trend: 12 },
    ]
  },
  3: { // 数据库原理
    metrics: { totalStudents: 35, submissionCount: 128, gradedCount: 120, avgScore: '78.9', chatCount: 256, activeStudents: 28 },
    questions: [
      { id: 1, text: '数据库索引的原理是什么？', studentCount: 14, trend: 18 },
      { id: 2, text: '事务隔离级别有哪些？', studentCount: 10, trend: 5 },
    ]
  },
  4: { // 机器学习基础
    metrics: { totalStudents: 45, submissionCount: 168, gradedCount: 160, avgScore: '88.2', chatCount: 380, activeStudents: 42 },
    questions: [
      { id: 1, text: '梯度下降与反向传播的关系？', studentCount: 18, trend: 25 },
      { id: 2, text: '过拟合与欠拟合的区别？', studentCount: 13, trend: 10 },
    ]
  }
}

// 初始化图表
const initCharts = () => {
  const data = trendDataMap[selectedTrendDays.value] || trendDataMap[7]
  const labels = trendDateLabels[selectedTrendDays.value] || trendDateLabels[7]
  const courseData = courseDataMap[selectedCourseId.value || 1]
  
  // 更新指标数据
  if (courseData) {
    Object.assign(metrics, courseData.metrics)
    hotQuestions.value = courseData.questions
  }
  
  // 学习趋势图
  trendOption.value = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: labels,
      axisLine: { lineStyle: { color: '#DAD5C8' } },
      axisLabel: { color: '#6B6B6B', rotate: labels.length > 12 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F0EFEA', type: 'dashed' } },
      axisLabel: { color: '#6B6B6B' }
    },
    series: [{
      type: 'line',
      smooth: true,
      data: data,
      itemStyle: { color: '#10B981' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
          { offset: 1, color: 'rgba(16, 185, 129, 0.01)' }
        ])
      }
    }]
  }

  // 作业完成情况饼图
  completionOption.value = {
    tooltip: { trigger: 'item' },
    legend: { bottom: '0%', left: 'center', textStyle: { color: '#6B6B6B' } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#FBFAF6',
        borderWidth: 2
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 18, fontWeight: 'bold', color: '#1E190F' }
      },
      data: [
        { value: 148, name: '已批改', itemStyle: { color: '#10B981' } },
        { value: 8, name: '待批改', itemStyle: { color: '#F59E0B' } }
      ]
    }]
  }

  // 知识库使用柱状图
  kbOption.value = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['文档', '视频', '习题', '代码'],
      axisLine: { lineStyle: { color: '#DAD5C8' } },
      axisLabel: { color: '#6B6B6B' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F0EFEA', type: 'dashed' } },
      axisLabel: { color: '#6B6B6B' }
    },
    series: [{
      type: 'bar',
      barWidth: '40%',
      data: [120, 200, 150, 80],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#10B981' },
          { offset: 1, color: '#34D399' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }
}

// 方法
const refreshData = async () => {
  isLoading.value = true
  try {
    await loadDashboardData()
    // 显示刷新成功提示
    alert('数据已刷新')
  } finally {
    isLoading.value = false
  }
}

const loadDashboardData = async () => {
  // TODO: 调用 API 加载数据
  // 模拟数据
  metrics.totalStudents = 42
  metrics.submissionCount = 156
  metrics.gradedCount = 148
  metrics.avgScore = '85.6'
  metrics.chatCount = 328
  metrics.activeStudents = 38
  
  hotQuestions.value = [
    { id: 1, text: '如何理解机器学习中的过拟合问题？', studentCount: 12, trend: 15 },
    { id: 2, text: 'Python 装饰器的使用场景有哪些？', studentCount: 9, trend: 8 },
    { id: 3, text: '数据库索引的原理是什么？', studentCount: 7, trend: -3 },
    { id: 4, text: '如何优化神经网络的训练速度？', studentCount: 6, trend: 22 },
    { id: 5, text: 'RESTful API 设计规范', studentCount: 5, trend: 5 },
    { id: 6, text: 'Git 分支管理策略', studentCount: 4, trend: -8 },
    { id: 7, text: 'Docker 容器化部署流程', studentCount: 4, trend: 12 },
    { id: 8, text: 'Vue3 组合式 API 优势', studentCount: 3, trend: 0 }
  ]
  
  initCharts()
}

const exportReport = () => {
  // 生成 CSV 数据
  const headers = ['指标', '数值']
  const rows = [
    ['选课人数', metrics.totalStudents],
    ['作业提交', metrics.submissionCount],
    ['已批改', metrics.gradedCount],
    ['平均分', metrics.avgScore],
    ['答疑消息', metrics.chatCount],
    ['活跃学生', metrics.activeStudents]
  ]
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')
  
  // 创建下载链接
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `学情报告_${new Date().toLocaleDateString('zh-CN')}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const viewStudents = () => {
  // 跳转到学生名单页面
  window.location.href = '/dashboard/students'
}

// 监听课程变化
watch(selectedCourseId, (newId) => {
  if (newId) {
    courseStore.setActiveCourse(newId)
    loadDashboardData()
  }
})

// 监听时间范围变化，更新图表
watch(selectedTrendDays, () => {
  initCharts()
})

onMounted(() => {
  loadDashboardData()
  
  // 初始化选中课程
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.activeCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  padding: var(--space-6);
  max-width: 1400px;
  margin: 0 auto;
}

// 页面标题区
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-6);

  .page-title {
    h1 {
      font-size: var(--text-3xl);
      font-weight: var(--font-semibold);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: var(--space-3);
      margin: 0;

      i {
        width: 40px;
        height: 40px;
        border-radius: var(--radius-lg);
        background: linear-gradient(135deg, rgb(var(--green)), rgb(52, 211, 153));
        display: grid;
        place-items: center;
        font-size: 20px;
        color: rgb(var(--paper));
        box-shadow: var(--shadow-md);
      }
    }

    .page-subtitle {
      font-size: var(--text-sm);
      color: var(--text-secondary);
      margin: var(--space-2) 0 0 0;
    }
  }

  .page-actions {
    display: flex;
    gap: var(--space-3);

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--space-2);
      min-width: 80px;
      cursor: pointer;
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      .spin {
        animation: spin 1s linear infinite;
      }
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 筛选栏
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: var(--space-6);
  flex-wrap: wrap;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);

    label {
      font-size: var(--text-sm);
      font-weight: var(--font-medium);
      color: var(--text-primary);
      margin: 0;
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      min-height: 18px;

      i {
        color: rgb(var(--green));
      }
    }

    :deep(.dropdown-select) {
      min-width: 220px;
    }
  }
}

// 核心指标卡片
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);

  @media (max-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-4);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
  animation: fadeUp 0.5s ease-out both;
  cursor: pointer;

  &:hover {
    border-color: rgba(var(--ink), 0.1);
    box-shadow: var(--shadow-md);
  }

  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(12px);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }

  .metric-top {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .metric-value {
    font-size: var(--text-metric-value);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
  }

  .metric-label {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    margin-top: var(--space-1);
  }
}

// 图表卡片
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-6);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.chart-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);

  i {
    color: rgb(var(--green));
  }
}

.chart-tabs {
  display: flex;
  gap: var(--space-1);
  background: var(--bg-tertiary);
  padding: var(--space-1);
  border-radius: var(--radius-md);
}

.chart-tab {
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-sans);
  transition: all 0.2s ease;

  &:hover {
    color: var(--text-primary);
  }

  &.active {
    background: var(--bg-card);
    color: var(--text-primary);
    font-weight: var(--font-semibold);
    box-shadow: var(--shadow-sm);
  }
}

.chart-container {
  flex: 1;
  min-height: 300px;

  &.tall {
    min-height: 340px;
  }
}

// 热门问题
.hot-questions-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border);

  .card-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--text-primary);
  }

  .card-link {
    font-size: var(--text-sm);
    color: rgb(var(--green));
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.question-list {
  padding: var(--space-2) var(--space-3);
  overflow-y: auto;
  flex: 1;
  max-height: 400px;
}

.question-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-2);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    background: var(--bg-tertiary);
  }
}

.question-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  background: var(--bg-tertiary);
  color: var(--text-secondary);

  &.rank-1 {
    background: linear-gradient(135deg, rgb(251, 191, 36), rgb(245, 158, 11));
    color: white;
  }

  &.rank-2 {
    background: linear-gradient(135deg, rgb(102, 112, 133), rgb(148, 163, 184));
    color: white;
  }

  &.rank-3 {
    background: linear-gradient(135deg, rgb(234, 179, 8), rgb(202, 138, 4));
    color: white;
  }
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.question-meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
  display: flex;
  gap: var(--space-3);

  span {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
  }
}

.question-trend {
  display: inline-flex;
  align-items: center;
  gap: var(--space-0);
  font-size: 11px;
  flex-shrink: 0;

  &.up {
    color: rgb(16, 185, 129);
  }

  &.down {
    color: rgb(239, 68, 68);
  }
}

.empty-state {
  text-align: center;
  padding: var(--space-10) 0;
  color: var(--text-muted);

  i {
    font-size: 32px;
    display: block;
    margin-bottom: var(--space-2);
  }

  p {
    margin: 0;
    font-size: var(--text-sm);
  }
}
</style>
