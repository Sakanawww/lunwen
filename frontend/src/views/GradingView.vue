<template>
  <div class="grading-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-checkbox-circle-line"></i> 作业批改</h1>
        <p class="page-subtitle">由 Grading Agent 自动批改，返回得分与评语</p>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="toolbar">
      <div class="filter-group">
        <label for="statusFilter"><i class="ri-filter-3-line"></i> 状态筛选</label>
        <DropdownSelect
          v-model="statusFilter"
          :options="statusOptions"
          placeholder="全部状态"
        />
      </div>
    </div>

    <!-- 提交列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-list-check-3"></i> 待批改 / 已批改提交</h2>
        <span class="doc-count">共 {{ submissions.length }} 份</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>作业</th>
              <th>学生</th>
              <th>内容摘要</th>
              <th>状态</th>
              <th>得分</th>
              <th class="num">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="sub in filteredSubmissions"
              :key="sub.id"
              :class="{ 'loading': sub.grading }"
            >
              <td class="td-mono">{{ sub.id }}</td>
              <td>{{ sub.assignment_title }}</td>
              <td>{{ sub.student_name }}</td>
              <td class="content-cell">{{ sub.content }}</td>
              <td>
                <span
                  class="status-badge"
                  :class="sub.status === 'pending' ? 'status-pending' : 'status-graded'"
                >
                  <i :class="sub.status === 'pending' ? 'ri-time-line' : 'ri-check-double-line'"></i>
                  {{ sub.status === 'pending' ? '待批改' : '已批改' }}
                </span>
              </td>
              <td class="num">
                <strong :class="{ 'score-highlight': sub.score !== null }">
                  {{ sub.score ?? '—' }}
                </strong>
              </td>
              <td class="num">
                <button
                  v-if="sub.status === 'pending'"
                  class="btn btn-primary btn-sm"
                  @click="gradeSubmission(sub.id)"
                  :disabled="sub.grading"
                >
                  <i v-if="sub.grading" class="ri-loader-4-line spin"></i>
                  <i v-else class="ri-sparkling-2-line"></i>
                  {{ sub.grading ? '批改中…' : 'AI 批改' }}
                </button>
                <button
                  v-else
                  class="btn btn-secondary btn-sm"
                  @click="gradeSubmission(sub.id)"
                  :disabled="sub.grading"
                >
                  <i v-if="sub.grading" class="ri-loader-4-line spin"></i>
                  <i v-else class="ri-refresh-line"></i>
                  重新批改
                </button>
              </td>
            </tr>
            <tr v-if="filteredSubmissions.length === 0">
              <td colspan="7" class="empty-state">
                <i class="ri-inbox-archive-line"></i>
                <p>{{ loading ? '加载中…' : '暂无提交' }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 批改结果弹窗 -->
    <div
      v-if="showResultModal"
      class="modal-mask"
      @click.self="closeResult"
    >
      <div class="modal-box" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3>批改结果</h3>
          <button type="button" class="modal-x" @click="closeResult">
            <i class="ri-close-line"></i>
          </button>
        </div>
        <div class="grade-sheet">
          <div class="grade-score">
            <span class="score">{{ resultData.score ?? '--' }}</span>
            <span class="of">/ 100</span>
          </div>
          <div class="grade-feedback">{{ resultData.feedback || '（无评语）' }}</div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-primary" @click="closeResult">
            <i class="ri-check-line"></i> 确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { api } from '@/utils/request'

interface Submission {
  id: number
  assignment_title: string
  student_id: number
  student_name: string
  content: string
  status: 'pending' | 'graded'
  score: number | null
  feedback?: string | null
  grading?: boolean
}

const courseStore = useCourseStore()

const statusFilter = ref<string>('all')
const showResultModal = ref(false)
const resultData = reactive({ score: null as number | null, feedback: '' })
const loading = ref(false)

const statusOptions = [
  { value: 'all', label: '全部状态' },
  { value: 'pending', label: '待批改' },
  { value: 'graded', label: '已批改' }
]

const submissions = ref<Submission[]>([])

const filteredSubmissions = computed(() => {
  if (statusFilter.value === 'all') return submissions.value
  return submissions.value.filter(s => s.status === statusFilter.value)
})

const loadSubmissions = async () => {
  const courseId = courseStore.currentCourseId
  if (!courseId) return
  loading.value = true
  try {
    const data: any = await api.get(`/api/grade/submissions/${courseId}`)
    submissions.value = (Array.isArray(data) ? data : []).map((s: any) => ({
      id: s.id,
      assignment_title: s.assignment_title || '—',
      student_id: s.student_id,
      student_name: s.student_name || `#${s.student_id}`,
      content: s.content || '',
      status: s.status === 'graded' ? 'graded' : 'pending',
      score: s.score,
      feedback: s.feedback,
      grading: false,
    }))
  } catch (error) {
    console.error('获取提交列表失败:', error)
    submissions.value = []
  } finally {
    loading.value = false
  }
}

watch(() => courseStore.currentCourseId, () => loadSubmissions())

const gradeSubmission = async (id: number) => {
  const sub = submissions.value.find(s => s.id === id)
  if (!sub) return

  sub.grading = true
  try {
    const data: any = await api.post(`/api/grade/${id}`)
    sub.status = 'graded'
    sub.score = data.score
    sub.feedback = data.feedback
    sub.grading = false

    resultData.score = data.score
    resultData.feedback = data.feedback || '（无评语）'
    showResultModal.value = true
  } catch (error) {
    sub.grading = false
    console.error('批改失败:', error)
    alert('批改失败，请稍后重试')
  }
}

const closeResult = () => {
  showResultModal.value = false
}

onMounted(() => loadSubmissions())
</script>

<style lang="scss" scoped>
.grading-page {
  padding: var(--space-6);
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
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

.toolbar {
  display: flex;
  align-items: flex-end;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);

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

    :deep(.dropdown-select) {
      min-width: 240px;
    }
  }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);

  .card-title {
    font-size: var(--text-lg);
    font-weight: var(--font-medium);
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin: 0;

    i {
      color: rgb(var(--green));
    }
  }

  .doc-count {
    font-size: var(--text-sm);
    color: var(--text-muted);
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

    &.num {
      text-align: right;
    }
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &.num {
      text-align: right;
    }

    &.td-mono {
      font-family: var(--font-mono);
      white-space: nowrap;
    }

    &.content-cell {
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  tbody tr {
    &:hover {
      background: var(--bg-tertiary);
    }

    &.loading {
      opacity: 0.6;
    }
  }
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);

  &.status-pending {
    background: rgba(245, 158, 11, 0.1);
    color: rgb(184, 106, 0);
  }

  &.status-graded {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
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

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);

    &:hover:not(:disabled) {
      background: var(--bg-tertiary);
      border-color: rgb(var(--green));
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.empty-state {
  text-align: center;
  padding: var(--space-10) 0;
  color: var(--text-muted);

  i {
    font-size: 34px;
    display: block;
    margin-bottom: var(--space-2);
  }

  p {
    margin: 0;
    font-size: var(--text-sm);
  }
}

// 弹窗
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
}

.modal-box {
  width: 100%;
  max-width: 520px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.25);
  padding: var(--space-5);
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);

  h3 {
    margin: 0;
    font-size: var(--text-lg);
    color: var(--text-primary);
  }
}

.modal-x {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  line-height: 1;

  &:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
  }
}

.grade-sheet {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-4);
}

.grade-score {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);

  .score {
    font-size: 34px;
    font-weight: var(--font-bold);
    color: rgb(var(--green));
  }

  .of {
    color: var(--text-muted);
    font-size: var(--text-sm);
  }
}

.grade-feedback {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: pre-wrap;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.score-highlight {
  color: rgb(var(--green));
  font-weight: var(--font-semibold);
}
</style>
