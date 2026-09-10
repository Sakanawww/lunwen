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

interface TrendDatum {
  labels: string[]
  submissions: number[]
  questions: number[]
  kb: number[]
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

// 后端返回的最新数据（供图表按趋势粒度渲染）
const trendData = ref<TrendDatum>({ labels: [], submissions: [], questions: [], kb: [] })
const completionData = ref<{ done: number; pending: number; overdue: number }>({ done: 0, pending: 0, overdue: 0 })
const kbUsageData = ref<{ docs: number; chunks: number; references: number; gradings: number }>({ docs: 0, chunks: 0, references: 0, gradings: 0 })

// 认证请求头
const authHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
})

/** 按趋势粒度切取子序列：把后端返回的趋势数据投影到「周/月/季/全部」标签体系 */
const sliceTrend = (arr: number[], days: number): number[] => {
  const src = trendData.value
  if (!arr || arr.length === 0) return []
  const n = src.labels.length
  if (n === 0) return []
  // days<=0 表示全部，整段使用
  if (days <= 0) return [...arr]
  // 目标点数：历史累计最多取 days 个点（若数据不足则全量）
  const take = Math.min(days, n)
  return arr.slice(n - take)
}

const trendLabels = computed<string[]>(() => {
  const src = trendData.value
  const days = selectedTrendDays.value
  const n = src.labels.length
  if (n === 0) return []
  if (days <= 0) return [...src.labels]
  const take = Math.min(days, n)
  return src.labels.slice(n - take)
})

// 初始化图表
const initCharts = () => {
  const labels = trendLabels.value
  const submissions = sliceTrend(trendData.value.submissions, selectedTrendDays.value)
  const questions = sliceTrend(trendData.value.questions, selectedTrendDays.value)
  const kb = sliceTrend(trendData.value.kb, selectedTrendDays.value)

  // 学习趋势图（作业提交 / 答疑提问 / 知识库引用 三线）
  trendOption.value = {
    tooltip: { trigger: 'axis' },
    legend: { bottom: '0%', left: 'center', textStyle: { color: '#6B6B6B' } },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: labels,
      axisLine: { lineStyle: { color: '#DAD5C8' } },
      axisLabel: { color: '#6B6B6B', rotate: labels.length > 12 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#F0EFEA', type: 'dashed' } },
      axisLabel: { color: '#6B6B6B' }
    },
    series: [
      {
        name: '作业提交',
        type: 'line',
        smooth: true,
        data: submissions,
        itemStyle: { color: '#10B981' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.01)' }
          ])
        }
      },
      {
        name: '答疑提问',
        type: 'line',
        smooth: true,
        data: questions,
        itemStyle: { color: '#3B82F6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.25)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.01)' }
          ])
        }
      },
      {
        name: '知识库引用',
        type: 'line',
        smooth: true,
        data: kb,
        itemStyle: { color: '#8B5CF6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(139, 92, 246, 0.2)' },
            { offset: 1, color: 'rgba(139, 92, 246, 0.01)' }
          ])
        }
      }
    ]
  }

  // 作业完成情况饼图
  const { done, pending, overdue } = completionData.value
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
        { value: done, name: '已完成', itemStyle: { color: '#10B981' } },
        { value: pending, name: '待批改', itemStyle: { color: '#F59E0B' } },
        { value: overdue, name: '已逾期', itemStyle: { color: '#EF4444' } }
      ]
    }]
  }

  // 知识库使用柱状图
  const { docs, chunks, references, gradings } = kbUsageData.value
  kbOption.value = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['文档', '知识分块', '引用', 'AI 批改'],
      axisLine: { lineStyle: { color: '#DAD5C8' } },
      axisLabel: { color: '#6B6B6B' }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#F0EFEA', type: 'dashed' } },
      axisLabel: { color: '#6B6B6B' }
    },
    series: [{
      type: 'bar',
      barWidth: '40%',
      data: [docs, chunks, references, gradings],
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
  if (!selectedCourseId.value) return
  const courseId = selectedCourseId.value
  const range = Number(selectedTimeRange.value) || 30
  try {
    const res = await fetch(`/api/dashboard/overview?course_id=${courseId}&range=${range}`, {
      method: 'GET',
      credentials: 'include',
      headers: authHeaders(),
    })
    if (!res.ok) return
    const data = await res.json()

    // 核心指标
    Object.assign(metrics, {
      totalStudents: data.metrics.total_students,
      submissionCount: data.metrics.submission_count,
      gradedCount: data.metrics.graded_count,
      avgScore: data.metrics.avg_score ?? '0',
      chatCount: data.metrics.chat_count,
      activeStudents: data.metrics.active_students,
    })

    // 热门问题
    hotQuestions.value = (data.hot_questions || []).map((q: any) => ({
      id: q.text,
      text: q.text,
      studentCount: q.count,
      trend: 0,
    }))

    // 图表数据
    completionData.value = data.completion || { done: 0, pending: 0, overdue: 0 }
    kbUsageData.value = data.kb_usage || { docs: 0, chunks: 0, references: 0, gradings: 0 }
    trendData.value = data.trend || { labels: [], submissions: [], questions: [], kb: [] }
  } finally {
    initCharts()
  }
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

// 监听课程下拉变化：切换课程并重新拉整份看板数据
watch(selectedCourseId, (newId) => {
  if (newId) {
    courseStore.setActiveCourse(newId)
    loadDashboardData()
  }
})

// 监听时间范围下拉变化：以新范围重新拉取看板数据
watch(selectedTimeRange, () => {
  if (selectedCourseId.value) {
    loadDashboardData()
  }
})

// 监听趋势粒度切换：仅重绘图表，不重新请求数据
watch(selectedTrendDays, () => {
  initCharts()
})

onMounted(async () => {
  // 加载课程下拉选项
  if (courseStore.courses.length === 0) {
    try {
      await courseStore.fetchCourses()
    } catch (e) {
      console.error('加载课程列表失败:', e)
    }
  }

  // 初始化选中课程
  if (courseStore.courses.length > 0) {
    const saved = courseStore.currentCourseId || courseStore.courses[0].id
    selectedCourseId.value = saved
  }

  await loadDashboardData()
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
