<template>
  <div class="questions-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-edit-circle-line"></i> 试题生成</h1>
        <p class="page-subtitle">由 Question Agent 根据知识点与难度批量生成题目</p>
      </div>
    </div>

    <!-- AI 批量出题表单 -->
    <div class="card">
      <h2 class="card-title"><i class="ri-sparkling-2-line"></i> AI 批量出题</h2>
      
      <form @submit.prevent="handleSubmit" class="gen-form">
        <div class="form-row">
          <div class="form-group">
            <label for="courseSelect"><i class="ri-book-open-line"></i> 选择课程</label>
            <DropdownSelect
              v-model="selectedCourseId"
              :options="courseOptions"
              placeholder="选择课程…"
            />
          </div>
        </div>
        
        <div class="form-group full">
          <label for="topic"><i class="ri-lightbulb-flash-line"></i> 知识点</label>
          <input
            v-model="topic"
            type="text"
            id="topic"
            class="form-input"
            placeholder="例如：二叉树遍历、排序算法时间复杂度"
            required
          />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="num">题目数量</label>
            <input
              v-model.number="numQuestions"
              type="number"
              id="num"
              min="1"
              max="10"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label for="difficulty">难度</label>
            <input
              v-model.number="difficulty"
              type="number"
              id="difficulty"
              min="1"
              max="5"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="submit-row">
          <button type="submit" class="btn btn-primary" :disabled="isGenerating">
            <i v-if="isGenerating" class="ri-loader-4-line spin"></i>
            <i v-else class="ri-lightbulb-flash-line"></i>
            {{ isGenerating ? '生成中…' : '生成试题' }}
          </button>
        </div>
      </form>

      <div v-if="message" :class="['msg', messageSuccess ? 'ok' : 'error']">
        <i :class="messageSuccess ? 'ri-checkbox-circle-line' : 'ri-error-warning-line'"></i>
        {{ message }}
      </div>
    </div>

    <!-- 试题库列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-stack-line"></i> 试题库列表</h2>
        <div class="actions">
          <span class="doc-count">共 {{ questions.length }} 题</span>
          <router-link to="/questions/recycle" class="btn btn-secondary btn-sm">
            <i class="ri-delete-bin-line"></i> 回收站
          </router-link>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>题型</th>
              <th>题干</th>
              <th class="num">难度</th>
              <th>来源</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questions" :key="q.id">
              <td class="td-mono">{{ q.id }}</td>
              <td>
                <span class="q-type">
                  <i class="ri-question-line"></i>
                  {{ typeLabels[q.type] || q.type }}
                </span>
              </td>
              <td class="stem-cell">{{ q.stem }}</td>
              <td class="num">
                <span class="difficulty-badge" :class="`diff-${q.difficulty}`">
                  {{ q.difficulty }}
                </span>
              </td>
              <td>
                <span class="badge" :class="q.source === 'ai' ? 'b-info' : 'b-off'">
                  {{ q.source }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-danger btn-sm"
                  @click="deleteQuestion(q.id)"
                >
                  <i class="ri-delete-bin-line"></i> 删除
                </button>
              </td>
            </tr>
            <tr v-if="questions.length === 0">
              <td colspan="6" class="empty-state">
                <i class="ri-file-edit-line"></i>
                <p>暂无试题，请先生成</p>
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

interface Question {
  id: number
  type: 'choice' | 'fill' | 'short'
  stem: string
  difficulty: number
  source: 'ai' | 'manual'
}

const courseStore = useCourseStore()

// 表单状态
const selectedCourseId = ref<number | null>(null)
const topic = ref('')
const numQuestions = ref(3)
const difficulty = ref(3)
const isGenerating = ref(false)
const message = ref('')
const messageSuccess = ref(false)

// 试题列表
const questions = ref<Question[]>([])

// 题型标签映射
const typeLabels: Record<string, string> = {
  choice: '选择题',
  fill: '填空题',
  short: '简答题'
}

// 选项
const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

// 认证请求头
const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
})

// 方法
const handleSubmit = async () => {
  const topicVal = topic.value.trim()
  if (!selectedCourseId.value) {
    showToast('请先选择课程', 'error')
    return
  }
  if (!topicVal) {
    showToast('请填写知识点', 'error')
    return
  }

  isGenerating.value = true
  message.value = ''

  try {
    const res = await fetch('/api/question/generate', {
      method: 'POST',
      credentials: 'include',
      headers: authHeaders(),
      body: JSON.stringify({
        course_id: selectedCourseId.value,
        topic: topicVal,
        num: numQuestions.value,
        difficulty: difficulty.value,
      }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => null)
      throw new Error(err?.detail || '生成失败')
    }
    const data = await res.json()

    messageSuccess.value = true
    message.value = `已生成 ${data.count} 道试题`
    topic.value = ''

    await loadQuestions()
  } catch (error) {
    messageSuccess.value = false
    message.value = (error as Error).message || '生成失败，请稍后重试'
  } finally {
    isGenerating.value = false
  }
}

const loadQuestions = async () => {
  if (!selectedCourseId.value) {
    questions.value = []
    return
  }
  try {
    const res = await fetch(`/api/question/list/${selectedCourseId.value}`, {
      method: 'GET',
      credentials: 'include',
      headers: { 'Authorization': authHeaders().Authorization },
    })
    if (!res.ok) {
      questions.value = []
      return
    }
    const data = await res.json()
    questions.value = (data || []).map((q: any) => ({
      id: q.id,
      type: q.type,
      stem: q.stem,
      difficulty: q.difficulty ?? 3,
      source: q.source || 'ai',
    }))
  } catch (e) {
    console.error('加载试题失败:', e)
    questions.value = []
  }
}

const deleteQuestion = async (id: number) => {
  if (!confirm('删除后可在回收站恢复，确定继续？')) return

  try {
    const res = await fetch(`/api/question/${id}?permanent=0`, {
      method: 'DELETE',
      credentials: 'include',
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error('删除失败')
    questions.value = questions.value.filter(q => q.id !== id)
    showToast('已移入回收站', 'success')
  } catch (error) {
    showToast('删除失败', 'error')
  }
}

const showToast = (msg: string, type: 'success' | 'error') => {
  console.log(`[${type}] ${msg}`)
}

onMounted(async () => {
  if (courseStore.courses.length === 0) {
    try {
      await courseStore.fetchCourses()
    } catch (e) {
      console.error('加载课程列表失败:', e)
    }
  }

  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
  }

  await loadQuestions()
})

// 切换课程下拉时重新拉取该课程的试题库
watch(selectedCourseId, () => {
  if (selectedCourseId.value) {
    loadQuestions()
  }
})
</script>

<style lang="scss" scoped>
.questions-page {
  padding: var(--space-6);
  max-width: 1200px;
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

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0 0 var(--space-4) 0;

  i {
    color: rgb(var(--green));
  }
}

.gen-form {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4) var(--space-5);
  align-items: end;

  .form-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);

    &.full {
      grid-column: 1 / -1;
    }

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
      font-size: var(--text-base);
      font-family: var(--font-sans);
      color: var(--text-primary);
      transition: all 0.2s ease;

      &:focus {
        outline: none;
        border-color: rgb(var(--green));
        box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.15);
      }

      &::placeholder {
        color: var(--text-muted);
      }
    }
  }

  .submit-row {
    grid-column: 1 / -1;
    display: flex;
    gap: var(--space-3);
    align-items: center;
    margin-top: var(--space-2);
  }
}

.msg {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  margin-top: var(--space-4);

  &.ok {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.error {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(185, 28, 28);
  }
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

    &.num {
      text-align: right;
    }
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &.td-mono {
      font-family: var(--font-mono);
      white-space: nowrap;
    }

    &.stem-cell {
      max-width: 400px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    &.num {
      text-align: right;
    }
  }

  tbody tr:hover {
    background: var(--bg-tertiary);
  }
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

  i {
    margin-right: 2px;
  }
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

  &.diff-1 {
    background: rgba(16, 185, 129, 0.15);
    color: rgb(6, 118, 71);
  }

  &.diff-2 {
    background: rgba(59, 130, 246, 0.15);
    color: rgb(37, 99, 235);
  }

  &.diff-3 {
    background: rgba(245, 158, 11, 0.15);
    color: rgb(184, 106, 0);
  }

  &.diff-4 {
    background: rgba(239, 68, 68, 0.15);
    color: rgb(185, 28, 28);
  }

  &.diff-5 {
    background: rgba(139, 92, 246, 0.15);
    color: rgb(124, 58, 237);
  }
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.b-info {
    background: rgba(139, 92, 246, 0.1);
    color: rgb(124, 58, 237);
  }

  &.b-off {
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

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);

    &:hover {
      background: var(--bg-tertiary);
      border-color: rgb(var(--green));
    }
  }

  &.btn-danger {
    background: var(--bg-card);
    color: rgb(239, 68, 68);
    border: 1px solid rgba(239, 68, 68, 0.35);

    &:hover {
      background: rgba(239, 68, 68, 0.1);
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.td-mono {
  font-family: var(--font-mono);
}
</style>
