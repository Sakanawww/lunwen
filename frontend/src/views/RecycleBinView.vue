<template>
  <div class="recycle-bin-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-delete-bin-2-line"></i> 试题回收站</h1>
        <p class="page-subtitle">查看和恢复已删除的试题</p>
      </div>
    </div>

    <!-- 课程选择 -->
    <div class="card" v-if="courseOptions.length > 0">
      <div class="form-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect
          v-model="selectedCourseId"
          :options="courseOptions"
          placeholder="选择课程…"
        />
      </div>
    </div>

    <!-- 回收站列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-history-line"></i> 已删除试题</h2>
        <div class="actions">
          <button class="btn btn-secondary" @click="batchRestore" :disabled="selectedIds.length === 0">
            <i class="ri-restore-line"></i>
            <span>批量恢复</span>
          </button>
          <button class="btn btn-danger" @click="batchDelete" :disabled="selectedIds.length === 0">
            <i class="ri-delete-bin-line"></i>
            <span>彻底删除</span>
          </button>
        </div>
      </div>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <div class="search-box">
          <i class="ri-search-line"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索题干..."
            class="search-input"
          />
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th class="th-checkbox">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th>ID</th>
              <th>题型</th>
              <th>题干</th>
              <th>难度</th>
              <th>删除时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="q in filteredQuestions"
              :key="q.id"
            >
              <td>
                <input
                  type="checkbox"
                  :value="q.id"
                  v-model="selectedIds"
                />
              </td>
              <td class="td-mono">{{ q.id }}</td>
              <td>
                <span class="q-type">{{ typeLabels[q.type] || q.type }}</span>
              </td>
              <td class="stem-cell">{{ q.stem }}</td>
              <td>
                <span class="difficulty-badge" :class="`diff-${q.difficulty}`">{{ q.difficulty }}</span>
              </td>
              <td class="td-mono">{{ q.deleted_at || '—' }}</td>
              <td>
                <div class="actions-cell">
                  <button
                    class="btn btn-sm btn-secondary"
                    @click="restoreQuestion(q.id)"
                    title="恢复"
                  >
                    <i class="ri-restore-line"></i>
                  </button>
                  <button
                    class="btn btn-sm btn-danger"
                    @click="permanentlyDelete(q.id)"
                    title="彻底删除"
                  >
                    <i class="ri-delete-bin-line"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredQuestions.length === 0">
              <td colspan="7" class="empty-state">
                <i class="ri-inbox-line"></i>
                <p>暂无已删除试题</p>
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

const courseStore = useCourseStore()

interface DeletedQuestion {
  id: number
  type: string
  stem: string
  difficulty: number
  deleted_at: string | null
}

const typeLabels: Record<string, string> = {
  choice: '选择题',
  fill: '填空题',
  short: '简答题',
}

const selectedCourseId = ref<number | null>(null)
const deletedQuestions = ref<DeletedQuestion[]>([])
const searchQuery = ref('')
const selectedIds = ref<number[]>([])

const courseOptions = computed(() =>
  courseStore.courses.map(c => ({ value: c.id, label: c.name }))
)

const filteredQuestions = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return deletedQuestions.value.filter(q =>
    q.stem.toLowerCase().includes(query)
  )
})

const allSelected = computed(() => {
  return filteredQuestions.value.length > 0 &&
    filteredQuestions.value.every(q => selectedIds.value.includes(q.id))
})

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredQuestions.value.map(q => q.id)
  }
}

const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
})

const loadDeletedQuestions = async () => {
  if (!selectedCourseId.value) {
    deletedQuestions.value = []
    return
  }
  try {
    const res = await fetch(`/api/question/deleted/${selectedCourseId.value}`, {
      headers: { 'Authorization': authHeaders().Authorization },
    })
    if (!res.ok) {
      deletedQuestions.value = []
      return
    }
    const data = await res.json()
    deletedQuestions.value = (data || []).map((q: any) => ({
      id: q.id,
      type: q.type,
      stem: q.stem,
      difficulty: q.difficulty ?? 3,
      deleted_at: q.deleted_at,
    }))
  } catch (e) {
    console.error('加载已删除试题失败:', e)
    deletedQuestions.value = []
  }
}

const restoreQuestion = async (id: number) => {
  try {
    const res = await fetch(`/api/question/${id}/restore`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error('恢复失败')
    await loadDeletedQuestions()
  } catch (error) {
    console.error('恢复失败:', error)
  }
}

const permanentlyDelete = async (id: number) => {
  if (!confirm('确定要彻底删除该试题吗？此操作不可恢复。')) return
  try {
    const res = await fetch(`/api/question/${id}?permanent=1`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error('删除失败')
    await loadDeletedQuestions()
  } catch (error) {
    console.error('彻底删除失败:', error)
  }
}

const batchRestore = async () => {
  if (selectedIds.value.length === 0) return
  try {
    for (const id of [...selectedIds.value]) {
      await fetch(`/api/question/${id}/restore`, {
        method: 'POST',
        headers: authHeaders(),
      })
    }
    selectedIds.value = []
    await loadDeletedQuestions()
  } catch (error) {
    console.error('批量恢复失败:', error)
  }
}

const batchDelete = async () => {
  if (selectedIds.value.length === 0) return
  if (!confirm(`确定要彻底删除 ${selectedIds.value.length} 道试题吗？此操作不可恢复。`)) return
  try {
    for (const id of [...selectedIds.value]) {
      await fetch(`/api/question/${id}?permanent=1`, {
        method: 'DELETE',
        headers: authHeaders(),
      })
    }
    selectedIds.value = []
    await loadDeletedQuestions()
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}

watch(selectedCourseId, () => {
  loadDeletedQuestions()
})

onMounted(async () => {
  if (courseStore.courses.length === 0) {
    try {
      await courseStore.fetchCourses()
    } catch (e) {
      console.error('加载课程列表失败:', e)
    }
  }
  if (courseStore.currentCourseId) {
    selectedCourseId.value = courseStore.currentCourseId
  } else if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.courses[0].id
  }
  await loadDeletedQuestions()
})
</script>

<style lang="scss" scoped>
.recycle-bin-view {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-6);

  .page-title h1 {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);

    i {
      color: var(--danger);
    }
  }

  .page-subtitle {
    margin-top: var(--space-2);
    font-size: var(--text-base);
    color: var(--text-secondary);
  }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 400px;

  label {
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--text-primary);
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);

    i { color: rgb(var(--green)); }
  }
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  gap: var(--space-3);

  .card-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);

    i { color: var(--accent); }
  }

  .actions {
    display: flex;
    gap: var(--space-2);
  }
}

.search-bar {
  margin-bottom: var(--space-4);

  .search-box {
    position: relative;
    max-width: 320px;

    .search-input {
      width: 100%;
      height: 40px;
      padding: 0 var(--space-4) 0 var(--space-9);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius-md);
      background: var(--bg-input);
      color: var(--text-primary);
      font-size: var(--text-sm);

      &:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: var(--shadow-glow);
      }
    }

    i {
      position: absolute;
      left: var(--space-3);
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: var(--text-base);
    }
  }
}

.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);

  th {
    background: var(--bg-table-head);
    color: var(--text-secondary);
    font-weight: var(--font-semibold);
    padding: var(--space-3) var(--space-4);
    text-align: left;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &:first-child {
      width: 40px;
      text-align: center;
    }
  }

  tbody tr:hover {
    background: var(--bg-hover);
  }

  .th-checkbox {
    width: 40px;
    text-align: center;
  }

  .stem-cell {
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .td-mono {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  .q-type {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: var(--text-xs);
    padding: var(--space-1) var(--space-3);
    background: rgba(6, 182, 212, 0.1);
    color: rgb(6, 182, 212);
    border-radius: var(--radius-full);
  }

  .difficulty-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    padding: 0 var(--space-1);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    font-family: var(--font-mono);

    &.diff-1 { background: rgba(16, 185, 129, 0.15); color: rgb(6, 118, 71); }
    &.diff-2 { background: rgba(59, 130, 246, 0.15); color: rgb(37, 99, 235); }
    &.diff-3 { background: rgba(245, 158, 11, 0.15); color: rgb(184, 106, 0); }
    &.diff-4 { background: rgba(239, 68, 68, 0.15); color: rgb(185, 28, 28); }
    &.diff-5 { background: rgba(139, 92, 246, 0.15); color: rgb(124, 58, 237); }
  }

  .actions-cell {
    display: flex;
    gap: var(--space-2);
  }

  .empty-state {
    text-align: center;
    padding: var(--space-10);
    color: var(--text-muted);

    i {
      font-size: 48px;
      color: var(--border-strong);
      display: block;
      margin-bottom: var(--space-3);
    }

    p {
      margin: 0;
      font-size: var(--text-base);
    }
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--t-fast);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.btn-sm {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-strong);

    &:hover:not(:disabled) {
      background: var(--bg-hover);
      border-color: var(--accent);
    }
  }

  &.btn-danger {
    background: var(--danger-soft);
    color: var(--danger);
    border: 1px solid var(--danger-border);

    &:hover:not(:disabled) {
      background: var(--danger);
      color: var(--primary-foreground);
    }
  }
}
</style>
