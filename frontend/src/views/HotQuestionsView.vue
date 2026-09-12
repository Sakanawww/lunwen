<template>
  <div class="hot-questions-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-fire-line"></i> 热门问题</h1>
        <p class="page-subtitle">查看学生提问最多的问题排行</p>
      </div>
      <router-link to="/dashboard" class="btn btn-secondary">
        <i class="ri-arrow-left-line"></i>
        <span>返回看板</span>
      </router-link>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect
          v-model="selectedCourseId"
          :options="courseOptions"
          placeholder="选择课程…"
        />
      </div>
      <div class="filter-group">
        <label><i class="ri-time-line"></i> 时间范围</label>
        <DropdownSelect
          v-model="selectedTimeRange"
          :options="timeRangeOptions"
          placeholder="选择时间范围…"
        />
      </div>
    </div>

    <!-- 热门问题列表 -->
    <div class="questions-card">
      <div class="card-header">
        <div class="card-title">
          <i class="ri-fire-line"></i>
          热门问题 TOP 20
        </div>
        <button class="btn btn-primary btn-sm" @click="exportQuestions">
          <i class="ri-download-line"></i>
          导出报告
        </button>
      </div>

      <div class="question-list">
        <div
          v-for="(q, index) in filteredQuestions"
          :key="index"
          class="question-item"
          :class="'fade-in'"
          :style="{ animationDelay: `${index * 0.03}s` }"
        >
          <div class="question-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
          <div class="question-content">
            <div class="question-text">{{ q.text }}</div>
            <div class="question-meta">
              <span><i class="ri-chat-1-line"></i> {{ q.count }} 次提问</span>
            </div>
          </div>
        </div>
        <div v-if="filteredQuestions.length === 0" class="empty-state">
          <i class="ri-inbox-line"></i>
          <p>暂无热门问题</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { api } from '@/utils/request'

interface HotQuestion {
  rank: number
  text: string
  count: number
}

const courseStore = useCourseStore()

const selectedCourseId = ref<number | null>(null)
const selectedTimeRange = ref<string>('30')
const loading = ref(false)
const questions = ref<HotQuestion[]>([])

const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

const timeRangeOptions = [
  { value: '7', label: '最近 7 天' },
  { value: '30', label: '最近 30 天' },
  { value: '90', label: '最近 90 天' }
]

const filteredQuestions = computed(() => questions.value)

const fetchQuestions = async () => {
  if (!selectedCourseId.value) return
  loading.value = true
  try {
    const data: any = await api.get(`/api/dashboard/${selectedCourseId.value}/hot-questions`, {
      params: { limit: 20 }
    })
    questions.value = data.items || []
  } catch (error) {
    console.error('获取热门问题失败:', error)
    questions.value = []
  } finally {
    loading.value = false
  }
}

const exportQuestions = () => {
  const headers = ['排名', '问题', '提问次数']
  const rows = questions.value.map(q => [q.rank, q.text, q.count])
  const csvContent = [headers.join(','), ...rows.map(r => r.map(c => `"${c}"`).join(','))].join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `热门问题_${new Date().toLocaleDateString('zh-CN')}.csv`
  link.click()
}

watch([selectedCourseId, selectedTimeRange], () => {
  if (selectedCourseId.value) fetchQuestions()
})

onMounted(() => {
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.hot-questions-page {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-6);

  .page-title {
    h1 {
      font-size: var(--text-2xl);
      font-weight: var(--font-semibold);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: var(--space-2);
      margin: 0;

      i {
        color: rgb(239, 68, 68);
      }
    }

    .page-subtitle {
      font-size: var(--text-sm);
      color: var(--text-secondary);
      margin: var(--space-2) 0 0 0;
    }
  }
}

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
      min-width: 200px;
    }
  }
}

.questions-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
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

    i {
      color: rgb(239, 68, 68);
    }
  }
}

.question-list {
  padding: var(--space-3);
  max-height: 600px;
  overflow-y: auto;
}

.question-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-2);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  animation: fadeUp 0.4s ease-out both;

  &:hover {
    background: var(--bg-tertiary);
  }

  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }
}

.question-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: var(--text-sm);
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
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.question-meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
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
  font-weight: var(--font-medium);

  &.up {
    color: rgb(16, 185, 129);
  }

  &.down {
    color: rgb(239, 68, 68);
  }
}

.question-tags {
  flex-shrink: 0;
}

.tag {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.tag-ml { background: rgba(139, 92, 246, 0.1); color: rgb(124, 58, 237); }
  &.tag-py { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
  &.tag-db { background: rgba(245, 158, 11, 0.1); color: rgb(184, 106, 0); }
  &.tag-dl { background: rgba(139, 92, 246, 0.1); color: rgb(124, 58, 237); }
  &.tag-backend { background: rgba(6, 182, 212, 0.1); color: rgb(6, 182, 212); }
  &.tag-tool { background: rgba(102, 112, 133, 0.1); color: rgb(102, 112, 133); }
  &.tag-devops { background: rgba(239, 68, 68, 0.1); color: rgb(239, 68, 68); }
  &.tag-frontend { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
  &.tag-js { background: rgba(245, 158, 11, 0.1); color: rgb(184, 106, 0); }
  &.tag-net { background: rgba(16, 185, 129, 0.1); color: rgb(6, 118, 71); }
  &.tag-algo { background: rgba(139, 92, 246, 0.1); color: rgb(124, 58, 237); }
  &.tag-os { background: rgba(102, 112, 133, 0.1); color: rgb(102, 112, 133); }
  &.tag-arch { background: rgba(6, 182, 212, 0.1); color: rgb(6, 182, 212); }
  &.tag-security { background: rgba(239, 68, 68, 0.1); color: rgb(239, 68, 68); }
  &.tag-api { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;

  &.btn-sm {
    height: 32px;
    padding: 0 var(--space-3);
    font-size: var(--text-xs);
  }

  &.btn-primary {
    background: rgb(var(--green));
    color: rgb(var(--paper));
    border: none;
    box-shadow: 0 2px 0 rgba(var(--ink), 0.2);

    &:hover:not(:disabled) {
      background: rgb(25, 75, 55);
    }
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);

    &:hover {
      background: var(--bg-tertiary);
    }
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
