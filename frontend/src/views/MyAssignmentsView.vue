<template>
  <div class="submit-page">
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-file-edit-line"></i> 我的作业</h1>
        <p class="page-subtitle">查看作业要求并提交你的答案</p>
      </div>
    </div>

    <!-- 课程选择 -->
    <div class="card" v-if="courseOptions.length > 0">
      <div class="form-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect v-model="selectedCourseId" :options="courseOptions" placeholder="选择课程…" />
      </div>
    </div>

    <!-- 作业列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-list-check"></i> 作业列表</h2>
        <span class="doc-count">共 {{ assignments.length }} 份</span>
      </div>

      <div class="assignment-list">
        <div v-for="a in assignments" :key="a.id" class="assignment-item">
          <div class="assignment-head">
            <h3>{{ a.title }}</h3>
            <span class="status-badge" :class="a.my_submission ? (a.my_submission.status === 'graded' ? 'graded' : 'submitted') : 'pending'">
              {{ a.my_submission ? (a.my_submission.status === 'graded' ? '已批改' : '已提交') : '未提交' }}
            </span>
          </div>
          <p class="assignment-desc">{{ a.description || '（无描述）' }}</p>
          <div class="assignment-meta">
            <span><i class="ri-calendar-line"></i> 截止：{{ a.deadline || '无限制' }}</span>
            <span v-if="a.my_submission?.status === 'graded' && a.my_submission_score !== null">
              <i class="ri-medal-line"></i> 得分：{{ a.my_submission_score }}
            </span>
          </div>

          <!-- 提交区 -->
          <div class="submit-area">
            <textarea
              v-model="submitContent[a.id]"
              class="form-input form-textarea"
              rows="4"
              placeholder="在此输入你的作业答案…"
            ></textarea>
            <div class="submit-actions">
              <button class="btn btn-primary" @click="submitAssignment(a.id)" :disabled="submitting[a.id]">
                <i v-if="submitting[a.id]" class="ri-loader-4-line spin"></i>
                <i v-else class="ri-send-plane-line"></i>
                {{ a.my_submission ? '重新提交' : '提交作业' }}
              </button>
            </div>
            <div v-if="submitMsg[a.id]" :class="['msg', submitOk[a.id] ? 'ok' : 'error']">
              {{ submitMsg[a.id] }}
            </div>
          </div>

          <!-- 批改结果 -->
          <div v-if="a.my_submission?.status === 'graded'" class="grade-result">
            <div class="grade-score">
              <span class="score">{{ a.my_submission_score ?? '--' }}</span>
              <span class="of">/ 100</span>
            </div>
            <div class="grade-feedback">{{ a.my_submission_feedback || '（无评语）' }}</div>
          </div>
        </div>

        <div v-if="assignments.length === 0" class="empty-state">
          <i class="ri-inbox-line"></i>
          <p>暂无作业</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, reactive } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { api } from '@/utils/request'

interface Assignment {
  id: number
  course_id: number
  title: string
  description: string | null
  deadline: string | null
  created_at: string | null
  submission_count?: number
  my_submission: { id: number; status: string; submitted_at: string | null } | null
  my_submission_score?: number | null
  my_submission_feedback?: string | null
}

const courseStore = useCourseStore()

const selectedCourseId = ref<number | null>(null)
const assignments = ref<Assignment[]>([])
const submitContent = reactive<Record<number, string>>({})
const submitting = reactive<Record<number, boolean>>({})
const submitMsg = reactive<Record<number, string>>({})
const submitOk = reactive<Record<number, boolean>>({})

const courseOptions = computed(() =>
  courseStore.courses.map(c => ({ value: c.id, label: c.name }))
)

const loadAssignments = async () => {
  if (!selectedCourseId.value) {
    assignments.value = []
    return
  }
  try {
    const data: any = await api.get(`/api/assignments/course/${selectedCourseId.value}`)
    const list: Assignment[] = Array.isArray(data) ? data : []
    // 如果已提交，预填提交内容
    for (const a of list) {
      if (!submitContent[a.id]) {
        submitContent[a.id] = ''
      }
    }
    // 加载批改分数
    for (const a of list) {
      if (a.my_submission?.status === 'graded') {
        try {
          const detail: any = await api.get(`/api/assignments/${a.id}`)
          if (detail.my_submission) {
            a.my_submission_score = null
            a.my_submission_feedback = null
          }
        } catch { /* ignore */ }
      }
    }
    assignments.value = list
  } catch (e) {
    console.error('加载作业失败:', e)
    assignments.value = []
  }
}

const submitAssignment = async (assignmentId: number) => {
  const content = submitContent[assignmentId]?.trim()
  if (!content) {
    submitMsg[assignmentId] = '请输入作业内容'
    submitOk[assignmentId] = false
    return
  }
  submitting[assignmentId] = true
  submitMsg[assignmentId] = ''
  try {
    await api.post(`/api/assignments/${assignmentId}/submit`, { content })
    submitMsg[assignmentId] = '提交成功！等待教师批改'
    submitOk[assignmentId] = true
    submitContent[assignmentId] = ''
    await loadAssignments()
  } catch (e: any) {
    submitMsg[assignmentId] = e?.message || '提交失败，请重试'
    submitOk[assignmentId] = false
  } finally {
    submitting[assignmentId] = false
  }
}

watch(selectedCourseId, () => loadAssignments())

onMounted(async () => {
  if (courseStore.courses.length === 0) {
    try { await courseStore.fetchCourses() } catch (e) { /* ignore */ }
  }
  if (courseStore.currentCourseId) {
    selectedCourseId.value = courseStore.currentCourseId
  } else if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.courses[0].id
  }
  await loadAssignments()
})
</script>

<style lang="scss" scoped>
.submit-page {
  padding: var(--space-6);
  max-width: 1000px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: var(--space-6);
  .page-title h1 {
    font-size: var(--text-2xl); font-weight: var(--font-semibold); color: var(--text-primary);
    display: flex; align-items: center; gap: var(--space-2); margin: 0;
    i { color: rgb(var(--green)); }
  }
  .page-subtitle { font-size: var(--text-sm); color: var(--text-secondary); margin: var(--space-2) 0 0 0; }
}
.card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6); box-shadow: var(--shadow-sm); margin-bottom: var(--space-6);
}
.form-group {
  display: flex; flex-direction: column; gap: var(--space-2); max-width: 400px;
  label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); display: inline-flex; align-items: center; gap: var(--space-1); i { color: rgb(var(--green)); } }
}
.card-title {
  font-size: var(--text-lg); font-weight: var(--font-medium); color: var(--text-primary);
  display: flex; align-items: center; gap: var(--space-2); margin: 0;
  i { color: rgb(var(--green)); }
}
.section-head {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-4);
  .doc-count { font-size: var(--text-sm); color: var(--text-muted); }
}
.assignment-list { display: flex; flex-direction: column; gap: var(--space-4); }
.assignment-item {
  border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-4);
  .assignment-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2); h3 { font-size: var(--text-base); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; } }
  .assignment-desc { font-size: var(--text-sm); color: var(--text-secondary); margin: 0 0 var(--space-2) 0; }
  .assignment-meta { display: flex; gap: var(--space-4); font-size: var(--text-xs); color: var(--text-muted); margin-bottom: var(--space-3); span { display: inline-flex; align-items: center; gap: var(--space-1); } }
}
.status-badge {
  display: inline-flex; align-items: center; padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: var(--font-medium);
  &.graded { background: rgba(16, 185, 129, 0.1); color: rgb(6, 118, 71); }
  &.submitted { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
  &.pending { background: var(--bg-tertiary); color: var(--text-secondary); }
}
.submit-area {
  .form-input {
    width: 100%; padding: var(--space-3); border: 1px solid var(--border); border-radius: var(--radius-md);
    background: var(--bg-card); font-size: var(--text-sm); color: var(--text-primary); resize: vertical;
    &:focus { outline: none; border-color: rgb(var(--green)); }
  }
  .form-textarea { font-family: var(--font-sans); }
  .submit-actions { margin-top: var(--space-2); }
}
.grade-result {
  margin-top: var(--space-3); padding: var(--space-3) var(--space-4); border-radius: var(--radius-md);
  background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2);
  .grade-score { display: flex; align-items: baseline; gap: var(--space-1); margin-bottom: var(--space-2);
    .score { font-size: var(--text-2xl); font-weight: var(--font-bold); color: rgb(6, 118, 71); }
    .of { font-size: var(--text-sm); color: var(--text-muted); }
  }
  .grade-feedback { font-size: var(--text-sm); color: var(--text-secondary); }
}
.msg {
  margin-top: var(--space-2); padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); font-size: var(--text-sm);
  &.ok { background: rgba(16, 185, 129, 0.1); color: rgb(6, 118, 71); }
  &.error { background: rgba(239, 68, 68, 0.1); color: rgb(185, 28, 28); }
}
.btn {
  display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--font-medium); cursor: pointer; transition: all 0.2s; border: none;
  &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); box-shadow: 0 2px 0 rgba(var(--ink), 0.2); &:hover:not(:disabled) { background: rgb(25, 75, 55); } &:disabled { opacity: 0.6; cursor: not-allowed; } }
}
.empty-state { text-align: center; padding: var(--space-10) 0; color: var(--text-muted); i { font-size: 34px; display: block; margin-bottom: var(--space-2); } p { margin: 0; font-size: var(--text-sm); } }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
