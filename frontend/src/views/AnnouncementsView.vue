<template>
  <div class="announcements-page">
    <div class="page-header">
      <div class="page-title">
        <h1>课程公告</h1>
        <p class="page-subtitle">查看课程通知与教师发布的公告</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect v-model="selectedCourseId" :options="courseOptions" placeholder="选择课程…" />
      </div>
      <div class="filter-group" v-if="isTeacher">
        <button class="btn btn-primary" @click="showForm = !showForm">
          <i class="ri-add-line"></i> <span>{{ showForm ? '取消' : '发布公告' }}</span>
        </button>
      </div>
    </div>

    <!-- 发布表单 -->
    <div class="card form-card" v-if="showForm && isTeacher">
      <div class="form-row">
        <label>标题</label>
        <input v-model="formData.title" type="text" class="form-input" placeholder="公告标题…" />
      </div>
      <div class="form-row">
        <label>内容</label>
        <textarea v-model="formData.content" class="form-input" rows="4" placeholder="公告内容…"></textarea>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="submitAnnouncement" :disabled="!formData.title.trim()">
          <i class="ri-send-line"></i> 发布
        </button>
      </div>
    </div>

    <!-- 公告列表 -->
    <div class="announcements-list" v-if="announcements.length > 0">
      <div class="announcement-item" v-for="a in announcements" :key="a.id">
        <div class="ann-header">
          <h3 class="ann-title">{{ a.title }}</h3>
          <button v-if="isTeacher" class="btn btn-sm btn-danger" @click="deleteAnnouncement(a.id)">
            <i class="ri-delete-bin-line"></i>
          </button>
        </div>
        <p class="ann-content">{{ a.content }}</p>
        <div class="ann-meta">
          <span><i class="ri-user-line"></i> {{ a.author_name }}</span>
          <span><i class="ri-time-line"></i> {{ a.created_at }}</span>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <i class="ri-notification-line"></i>
      <p>暂无公告</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { useAuthStore } from '@/stores/auth.store'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const selectedCourseId = ref<number | null>(null)
const courseOptions = computed(() => courseStore.courses.map(c => ({ value: c.id, label: c.name })))
const isTeacher = computed(() => ['teacher', 'admin'].includes(authStore.user?.role || ''))
const announcements = ref<any[]>([])
const showForm = ref(false)
const formData = reactive({ title: '', content: '' })

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const loadData = async () => {
  if (!selectedCourseId.value) return
  try {
    const res = await fetch(`/api/announcements/${selectedCourseId.value}`, { headers: authHeaders() })
    if (res.ok) announcements.value = (await res.json()).announcements
  } catch (e) { console.error(e) }
}

const submitAnnouncement = async () => {
  if (!selectedCourseId.value || !formData.title.trim()) return
  try {
    const res = await fetch(`/api/announcements`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ course_id: selectedCourseId.value, title: formData.title, content: formData.content }),
    })
    if (res.ok) {
      formData.title = ''; formData.content = ''; showForm.value = false
      await loadData()
    }
  } catch (e) { console.error(e) }
}

const deleteAnnouncement = async (id: number) => {
  if (!confirm('确认删除该公告？')) return
  await fetch(`/api/announcements/${id}`, { method: 'DELETE', headers: authHeaders() })
  await loadData()
}

watch(selectedCourseId, (v) => { if (v) { courseStore.setActiveCourse(v); loadData() } })
onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  if (courseStore.courses.length > 0) selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
})
</script>

<style lang="scss" scoped>
.announcements-page { padding: var(--space-6); max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); h1 { font-size: var(--text-3xl); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; } .page-subtitle { font-size: var(--text-sm); color: var(--text-secondary); margin: var(--space-2) 0 0 0; } }
.filter-bar { display: flex; align-items: flex-end; gap: var(--space-6); flex-wrap: wrap; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); margin-bottom: var(--space-6); .filter-group { display: flex; flex-direction: column; gap: var(--space-2); label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); display: inline-flex; align-items: center; gap: var(--space-1); i { color: rgb(var(--green)); } } } }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.form-card { padding: var(--space-5) var(--space-6); margin-bottom: var(--space-6); animation: fadeUp 0.4s ease-out both; }
.form-row { margin-bottom: var(--space-4); label { display: block; font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); margin-bottom: var(--space-2); } }
.form-input { width: 100%; padding: var(--space-3) var(--space-4); border: 1px solid var(--border); border-radius: var(--radius-md); font-size: var(--text-sm); font-family: var(--font-sans); background: var(--bg-card); color: var(--text-primary); transition: border-color 0.2s ease; &:focus { outline: none; border-color: rgb(var(--green)); box-shadow: 0 0 0 3px rgba(var(--green), 0.1); } &textarea { resize: vertical; } }
.form-actions { display: flex; justify-content: flex-end; }
.announcements-list { display: flex; flex-direction: column; gap: var(--space-4); }
.announcement-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-6); box-shadow: var(--shadow-sm); transition: all 0.2s ease; animation: fadeUp 0.5s ease-out both; &:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); border-color: rgba(var(--ink), 0.1); } &:nth-child(1) { animation-delay: 0s; } &:nth-child(2) { animation-delay: 0.1s; } &:nth-child(3) { animation-delay: 0.2s; } &:nth-child(4) { animation-delay: 0.3s; } &:nth-child(5) { animation-delay: 0.4s; } }
.ann-header { display: flex; align-items: center; justify-content: space-between; .ann-title { font-size: var(--text-lg); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; } }
.ann-content { font-size: var(--text-sm); color: var(--text-primary); line-height: 1.7; margin: var(--space-3) 0; white-space: pre-wrap; }
.ann-meta { display: flex; gap: var(--space-4); font-size: var(--text-xs); color: var(--text-muted); span { display: inline-flex; align-items: center; gap: var(--space-1); } }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); border: 1px solid var(--border); background: var(--bg-card); transition: all 0.2s ease; &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); border-color: rgb(var(--green)); &:hover { box-shadow: 0 4px 12px rgba(var(--green), 0.3); transform: translateY(-1px); } } &.btn-danger { color: rgb(var(--destructive)); border-color: rgba(var(--destructive), 0.3); &:hover { background: rgba(var(--destructive), 0.08); } } &.btn-sm { padding: 4px 10px; font-size: 12px; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.empty-state { text-align: center; padding: var(--space-16); color: var(--text-muted); i { font-size: 48px; display: block; margin-bottom: var(--space-3); } }
</style>
