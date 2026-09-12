<template>
  <div class="assignments-page">
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-assignment-line"></i> 作业管理</h1>
        <p class="page-subtitle">发布作业、查看学生提交情况</p>
      </div>
    </div>

    <!-- 发布作业 -->
    <div class="card">
      <h2 class="card-title"><i class="ri-add-circle-line"></i> 发布新作业</h2>
      <form @submit.prevent="handleCreate" class="gen-form">
        <div class="form-group">
          <label><i class="ri-book-open-line"></i> 选择课程</label>
          <DropdownSelect v-model="form.courseId" :options="courseOptions" placeholder="选择课程…" />
        </div>
        <div class="form-group full">
          <label><i class="ri-heading-line"></i> 作业标题</label>
          <input v-model="form.title" type="text" class="form-input" placeholder="例如：第一次作业——排序算法实现" required />
        </div>
        <div class="form-group full">
          <label><i class="ri-file-text-line"></i> 作业描述</label>
          <textarea v-model="form.description" class="form-input form-textarea" rows="3" placeholder="作业要求、题目说明等…"></textarea>
        </div>
        <div class="form-group">
          <label><i class="ri-calendar-line"></i> 截止日期</label>
          <input v-model="form.deadline" type="date" class="form-input" />
        </div>
        <div class="submit-row">
          <button type="submit" class="btn btn-primary" :disabled="creating">
            <i v-if="creating" class="ri-loader-4-line spin"></i>
            <i v-else class="ri-send-plane-line"></i>
            {{ creating ? '发布中…' : '发布作业' }}
          </button>
        </div>
      </form>
      <div v-if="message" :class="['msg', messageOk ? 'ok' : 'error']">
        <i :class="messageOk ? 'ri-checkbox-circle-line' : 'ri-error-warning-line'"></i>
        {{ message }}
      </div>
    </div>

    <!-- 作业列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-list-check"></i> 已发布作业</h2>
        <div class="actions">
          <span class="doc-count">共 {{ assignments.length }} 份</span>
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>描述</th>
              <th>截止日期</th>
              <th class="num">提交数</th>
              <th>发布时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in assignments" :key="a.id">
              <td class="td-mono">{{ a.id }}</td>
              <td class="title-cell">{{ a.title }}</td>
              <td class="desc-cell">{{ a.description || '—' }}</td>
              <td class="td-mono">{{ a.deadline || '—' }}</td>
              <td class="num">{{ a.submission_count ?? 0 }}</td>
              <td class="td-mono">{{ a.created_at }}</td>
              <td>
                <button class="btn btn-danger btn-sm" @click="deleteAssignment(a.id)">
                  <i class="ri-delete-bin-line"></i> 删除
                </button>
              </td>
            </tr>
            <tr v-if="assignments.length === 0">
              <td colspan="7" class="empty-state">
                <i class="ri-inbox-line"></i>
                <p>暂无作业，请先发布</p>
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

interface Assignment {
  id: number
  course_id: number
  title: string
  description: string | null
  deadline: string | null
  created_at: string | null
  submission_count?: number
}

const courseStore = useCourseStore()

const form = ref({
  courseId: null as number | null,
  title: '',
  description: '',
  deadline: '',
})

const assignments = ref<Assignment[]>([])
const creating = ref(false)
const message = ref('')
const messageOk = ref(false)

const courseOptions = computed(() =>
  courseStore.courses.map(c => ({ value: c.id, label: c.name }))
)

const loadAssignments = async () => {
  const cid = form.value.courseId || courseStore.currentCourseId
  if (!cid) {
    assignments.value = []
    return
  }
  try {
    const data: any = await api.get(`/api/assignments/course/${cid}`)
    assignments.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('加载作业失败:', e)
    assignments.value = []
  }
}

const handleCreate = async () => {
  if (!form.value.courseId) { showToast('请先选择课程', false); return }
  if (!form.value.title.trim()) { showToast('请填写作业标题', false); return }
  creating.value = true
  message.value = ''
  try {
    await api.post('/api/assignments', {
      course_id: form.value.courseId,
      title: form.value.title,
      description: form.value.description || null,
      deadline: form.value.deadline || null,
    })
    form.value.title = ''
    form.value.description = ''
    form.value.deadline = ''
    await loadAssignments()
    showToast('作业发布成功', true)
  } catch (e) {
    showToast('发布失败，请重试', false)
  } finally {
    creating.value = false
  }
}

const deleteAssignment = async (id: number) => {
  if (!confirm('删除作业将一并删除所有学生提交，确定？')) return
  try {
    await api.delete(`/api/assignments/${id}`)
    await loadAssignments()
  } catch (e) {
    console.error('删除失败:', e)
    alert('删除失败')
  }
}

const showToast = (msg: string, ok: boolean) => {
  message.value = msg
  messageOk.value = ok
}

watch(() => form.value.courseId, () => loadAssignments())

onMounted(async () => {
  if (courseStore.courses.length === 0) {
    try { await courseStore.fetchCourses() } catch (e) { /* ignore */ }
  }
  if (courseStore.currentCourseId) {
    form.value.courseId = courseStore.currentCourseId
  } else if (courseStore.courses.length > 0) {
    form.value.courseId = courseStore.courses[0].id
  }
  // courseId watcher 会自动触发 loadAssignments，无需再手动调用
  if (!form.value.courseId) {
    await loadAssignments()
  }
})
</script>

<style lang="scss" scoped>
.assignments-page {
  padding: var(--space-6);
  max-width: 1200px;
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
.card-title {
  font-size: var(--text-lg); font-weight: var(--font-medium); color: var(--text-primary);
  display: flex; align-items: center; gap: var(--space-2); margin: 0 0 var(--space-4) 0;
  i { color: rgb(var(--green)); }
}
.gen-form {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4) var(--space-5); align-items: end;
  .form-group {
    display: flex; flex-direction: column; gap: var(--space-2);
    &.full { grid-column: 1 / -1; }
    label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); display: inline-flex; align-items: center; gap: var(--space-1); i { color: rgb(var(--green)); } }
    .form-input {
      height: 40px; padding: 0 var(--space-3); border: 1px solid var(--border); border-radius: var(--radius-md);
      background: var(--bg-card); font-size: var(--text-base); color: var(--text-primary); transition: all 0.2s;
      &:focus { outline: none; border-color: rgb(var(--green)); box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.15); }
    }
    .form-textarea { height: auto; padding: var(--space-3); resize: vertical; font-family: var(--font-sans); }
  }
  .submit-row { grid-column: 1 / -1; display: flex; gap: var(--space-3); align-items: center; margin-top: var(--space-2); }
}
.msg {
  display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md); font-size: var(--text-sm); margin-top: var(--space-4);
  &.ok { background: rgba(16, 185, 129, 0.1); color: rgb(6, 118, 71); }
  &.error { background: rgba(239, 68, 68, 0.1); color: rgb(185, 28, 28); }
}
.section-head {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-4);
  .doc-count { font-size: var(--text-sm); color: var(--text-muted); }
}
.data-table {
  width: 100%; border-collapse: collapse; font-size: var(--text-sm);
  thead th { background: var(--bg-tertiary); color: var(--text-secondary); font-weight: var(--font-semibold); font-size: var(--text-xs); padding: var(--space-3) var(--space-4); text-align: left; border-bottom: 2px solid var(--border); white-space: nowrap; &.num { text-align: right; } }
  tbody td { padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--border); color: var(--text-secondary); }
  tbody tr:hover { background: var(--bg-tertiary); }
  .td-mono { font-family: var(--font-mono); font-size: var(--text-xs); white-space: nowrap; }
  .title-cell { font-weight: var(--font-medium); color: var(--text-primary); max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .desc-cell { max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .num { text-align: right; }
}
.btn {
  display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--font-medium); cursor: pointer; transition: all 0.2s; border: 1px solid transparent;
  &.btn-sm { height: 32px; padding: 0 var(--space-3); font-size: var(--text-xs); }
  &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); border: none; box-shadow: 0 2px 0 rgba(var(--ink), 0.2); &:hover:not(:disabled) { background: rgb(25, 75, 55); } &:disabled { opacity: 0.6; cursor: not-allowed; } }
  &.btn-danger { background: var(--bg-card); color: rgb(239, 68, 68); border: 1px solid rgba(239, 68, 68, 0.35); &:hover { background: rgba(239, 68, 68, 0.1); } }
}
.empty-state { text-align: center; padding: var(--space-10) 0; color: var(--text-muted); i { font-size: 34px; display: block; margin-bottom: var(--space-2); } p { margin: 0; font-size: var(--text-sm); } }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
