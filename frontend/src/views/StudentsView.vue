<template>
  <div class="students-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-group-line"></i> 学生名单</h1>
        <p class="page-subtitle">查看课程选课学生详情与学习数据</p>
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
        <label><i class="ri-search-line"></i> 搜索学生</label>
        <input
          v-model="searchQuery"
          type="text"
          class="form-input"
          placeholder="输入姓名或学号…"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ students.length }}</div>
        <div class="stat-label">总人数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ activeStudents }}</div>
        <div class="stat-label">活跃学生</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ pendingStudents }}</div>
        <div class="stat-label">待完成作业</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ avgScore }}</div>
        <div class="stat-label">平均分</div>
      </div>
    </div>

    <!-- 学生列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-team-line"></i> 学生列表</h2>
        <div class="actions">
          <span class="doc-count">共 {{ students.length }} 人</span>
          <button class="btn btn-primary btn-sm" @click="exportStudents">
            <i class="ri-download-line"></i>
            导出名单
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>邮箱</th>
              <th>作业提交</th>
              <th>平均分</th>
              <th>活跃度</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.user_id">
              <td class="td-mono">{{ student.student_no || '—' }}</td>
              <td>
                <div class="student-name">
                  <div class="avatar">{{ student.real_name.charAt(0) }}</div>
                  <span>{{ student.real_name }}</span>
                </div>
              </td>
              <td class="td-mono">{{ student.username }}</td>
              <td>{{ student.submissions }}</td>
              <td>
                <span class="score-badge" :class="getScoreClass(student.accuracy)">
                  {{ student.accuracy !== null ? (student.accuracy * 100).toFixed(0) + '%' : '—' }}
                </span>
              </td>
              <td>{{ student.practice_count }}</td>
              <td>{{ student.questions }}</td>
              <td>
                <button class="btn btn-secondary btn-sm" @click="viewDetail(student)">
                  <i class="ri-eye-line"></i>
                  详情
                </button>
              </td>
            </tr>
            <tr v-if="filteredStudents.length === 0">
              <td colspan="8" class="empty-state">
                <i class="ri-inbox-line"></i>
                <p>{{ loading ? '加载中…' : '暂无学生数据' }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { api } from '@/utils/request'

interface Student {
  user_id: number
  username: string
  real_name: string
  student_no: string
  class_name: string
  submissions: number
  graded: number
  practice_count: number
  accuracy: number | null
  questions: number
}

const courseStore = useCourseStore()

const selectedCourseId = ref<number | null>(null)
const searchQuery = ref('')
const loading = ref(false)
const students = ref<Student[]>([])

const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

const fetchStudents = async () => {
  if (!selectedCourseId.value) return
  loading.value = true
  try {
    const data: any = await api.get(`/api/dashboard/${selectedCourseId.value}/students`)
    students.value = data.students || []
  } catch (error) {
    console.error('获取学生列表失败:', error)
    students.value = []
  } finally {
    loading.value = false
  }
}

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(s =>
    s.real_name.toLowerCase().includes(query) ||
    s.student_no.toLowerCase().includes(query) ||
    s.username.toLowerCase().includes(query)
  )
})

const activeStudents = computed(() => {
  return students.value.filter(s => s.questions > 0 || s.submissions > 0).length
})

const pendingStudents = computed(() => {
  return students.value.filter(s => s.submissions === 0).length
})

const avgScore = computed(() => {
  const withAccuracy = students.value.filter(s => s.accuracy !== null)
  if (withAccuracy.length === 0) return '—'
  const sum = withAccuracy.reduce((acc, s) => acc + (s.accuracy || 0), 0)
  return (sum / withAccuracy.length * 100).toFixed(1)
})

const getScoreClass = (accuracy: number | null) => {
  if (accuracy === null) return 'score-pass'
  const pct = accuracy * 100
  if (pct >= 90) return 'score-excellent'
  if (pct >= 80) return 'score-good'
  if (pct >= 60) return 'score-pass'
  return 'score-fail'
}

const exportStudents = () => {
  const headers = ['学号', '姓名', '用户名', '作业提交', '已批改', '练习次数', '正确率', '提问数']
  const rows = students.value.map(s => [
    s.student_no || '-',
    s.real_name,
    s.username,
    s.submissions,
    s.graded,
    s.practice_count,
    s.accuracy !== null ? (s.accuracy * 100).toFixed(1) + '%' : '—',
    s.questions
  ])
  const csvContent = [headers.join(','), ...rows.map(r => r.map(c => `"${c}"`).join(','))].join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `学生名单_${new Date().toLocaleDateString('zh-CN')}.csv`
  link.click()
}

const viewDetail = (student: Student) => {
  alert(`查看学生详情：${student.real_name}\n学号：${student.student_no || '无'}\n作业提交：${student.submissions}\n练习次数：${student.practice_count}\n提问数：${student.questions}`)
}

watch(selectedCourseId, () => {
  if (selectedCourseId.value) fetchStudents()
})

onMounted(() => {
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.students-page {
  padding: var(--space-6);
  max-width: 1400px;
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
        color: rgb(var(--green));
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

      i {
        color: rgb(var(--green));
      }
    }

    .form-input {
      height: 40px;
      padding: 0 var(--space-3);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: var(--bg-card);
      font-size: var(--text-sm);
      font-family: var(--font-sans);
      color: var(--text-primary);
      min-width: 220px;

      &:focus {
        outline: none;
        border-color: rgb(var(--green));
        box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.1);
      }
    }
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);

  .stat-value {
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
  }

  .stat-label {
    font-size: var(--text-sm);
    color: var(--text-secondary);
  }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-sm);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);

  .card-title {
    margin: 0;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);

    .doc-count {
      font-size: var(--text-sm);
      color: var(--text-muted);
    }
  }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);

  thead th {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: var(--font-semibold);
    font-size: var(--text-xs);
    padding: var(--space-3) var(--space-4);
    text-align: left;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &.td-mono {
      font-family: var(--font-mono);
    }
  }

  tbody tr:hover {
    background: var(--bg-tertiary);
  }
}

.student-name {
  display: flex;
  align-items: center;
  gap: var(--space-2);

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgb(var(--green));
    color: rgb(var(--paper));
    display: grid;
    place-items: center;
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
  }
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);

  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-full);
    overflow: hidden;
    min-width: 80px;

    .progress-fill {
      height: 100%;
      background: rgb(var(--green));
      border-radius: var(--radius-full);
      transition: width 0.3s ease;
    }
  }

  .progress-text {
    font-size: var(--text-xs);
    color: var(--text-secondary);
    font-family: var(--font-mono);
    white-space: nowrap;
  }
}

.score-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  font-family: var(--font-mono);

  &.score-excellent {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.score-good {
    background: rgba(59, 130, 246, 0.1);
    color: rgb(37, 99, 235);
  }

  &.score-pass {
    background: rgba(245, 158, 11, 0.1);
    color: rgb(184, 106, 0);
  }

  &.score-fail {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(185, 28, 28);
  }
}

.activity-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  i {
    font-size: 12px;
  }

  &.activity-high {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.activity-medium {
    background: rgba(245, 158, 11, 0.1);
    color: rgb(184, 106, 0);
  }

  &.activity-low {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(185, 28, 28);
  }
}

.status-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.status-active {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.status-inactive {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
  }
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
