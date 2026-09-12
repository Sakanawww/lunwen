<template>
  <div class="courses-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-book-open-line"></i> 我的课程</h1>
        <p class="page-subtitle">查看和管理已选课程</p>
      </div>
    </div>

    <!-- 课程列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-stack-line"></i> 课程列表</h2>
        <div class="actions">
          <span class="doc-count">共 {{ courses.length }} 门</span>
          <button
            v-if="canCreateCourse"
            class="btn btn-primary btn-sm"
            @click="showCreateModal = true"
          >
            <i class="ri-add-line"></i> 新建课程
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>课程名称</th>
              <th>课程代码</th>
              <th>角色</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id">
              <td>
                <div class="course-info">
                  <i class="ri-book-open-line"></i>
                  <span>{{ course.name }}</span>
                </div>
              </td>
              <td class="td-mono">{{ course.code || '—' }}</td>
              <td>
                <span class="status-badge" :class="roleBadgeClass(course.my_role)">
                  {{ roleLabel(course.my_role) }}
                </span>
              </td>
              <td>
                <div class="actions-cell">
                  <button class="btn btn-primary btn-sm" @click="selectCourse(course.id)">
                    <i class="ri-checkbox-circle-line"></i> 进入
                  </button>
                  <button
                    v-if="course.my_role === 'owner'"
                    class="btn btn-secondary btn-sm"
                    @click="editCourse(course)"
                  >
                    <i class="ri-edit-line"></i> 编辑
                  </button>
                  <button
                    v-if="course.my_role === 'owner'"
                    class="btn btn-danger btn-sm"
                    @click="deleteCourse(course)"
                  >
                    <i class="ri-delete-bin-line"></i> 删除
                  </button>
                  <button
                    v-if="isStudent && course.my_role === 'student'"
                    class="btn btn-danger btn-sm"
                    @click="unenroll(course)"
                  >
                    <i class="ri-logout-box-line"></i> 退课
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="4" class="empty-state">
                <i class="ri-book-line"></i>
                <p>暂无课程</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 创建/编辑课程弹窗 -->
    <div v-if="showCreateModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingCourse ? '编辑课程' : '新建课程' }}</h3>
          <button class="btn-close" @click="closeModal">
            <i class="ri-close-line"></i>
          </button>
        </div>
        <form @submit.prevent="saveCourse" class="modal-body">
          <div class="form-group">
            <label for="course-name">课程名称 *</label>
            <input id="course-name" v-model="courseForm.name" type="text" class="form-input" required />
          </div>
          <div class="form-group">
            <label for="course-code">课程代码</label>
            <input id="course-code" v-model="courseForm.code" type="text" class="form-input" placeholder="如 CS101" />
          </div>
          <div class="form-group">
            <label for="course-desc">课程描述</label>
            <textarea id="course-desc" v-model="courseForm.description" class="form-input form-textarea" rows="3"></textarea>
          </div>
        </form>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
          <button type="submit" class="btn btn-primary" @click="saveCourse" :disabled="saving">
            <i v-if="saving" class="ri-loader-4-line spin"></i>
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useCourseStore } from '@/stores/course.store'
import { useAuthStore } from '@/stores/auth.store'
import { api } from '@/utils/request'
import { useRouter } from 'vue-router'

interface CourseItem {
  id: number
  name: string
  code: string | null
  teacher_id: number | null
  description: string | null
  my_role: string
}

const courseStore = useCourseStore()
const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)
const courses = computed(() => courseStore.courses as unknown as CourseItem[])
const isStudent = computed(() => user.value?.role === 'student')
const canCreateCourse = computed(() => {
  const role = user.value?.role
  return role === 'teacher' || role === 'admin'
})

const showCreateModal = ref(false)
const editingCourse = ref<CourseItem | null>(null)
const saving = ref(false)
const courseForm = reactive({
  name: '',
  code: '',
  description: '',
})

const roleLabel = (role: string) => {
  const map: Record<string, string> = {
    owner: '教师',
    teacher: '协教',
    assistant: '助教',
    student: '学生',
    admin: '管理员',
  }
  return map[role] || role
}

const roleBadgeClass = (role: string) => {
  if (role === 'owner' || role === 'teacher') return 'status-active'
  return 'status-ended'
}

const selectCourse = (courseId: number) => {
  courseStore.setActiveCourse(courseId)
  const role = user.value?.role
  if (role === 'student') {
    router.push('/chat')
  } else {
    router.push('/dashboard')
  }
}

const editCourse = (course: CourseItem) => {
  editingCourse.value = course
  courseForm.name = course.name
  courseForm.code = course.code || ''
  courseForm.description = course.description || ''
  showCreateModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  editingCourse.value = null
  courseForm.name = ''
  courseForm.code = ''
  courseForm.description = ''
}

const saveCourse = async () => {
  if (!courseForm.name.trim()) return
  saving.value = true
  try {
    const payload = {
      name: courseForm.name,
      code: courseForm.code || null,
      description: courseForm.description || null,
    }
    if (editingCourse.value) {
      await api.put(`/api/courses/${editingCourse.value.id}`, payload)
    } else {
      await api.post('/api/courses', payload)
    }
    closeModal()
    await courseStore.fetchCourses()
  } catch (e) {
    console.error('保存课程失败:', e)
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const deleteCourse = async (course: CourseItem) => {
  if (!confirm(`确定要删除课程「${course.name}」吗？所有关联数据将被清除。`)) return
  try {
    await api.delete(`/api/courses/${course.id}`)
    await courseStore.fetchCourses()
  } catch (e) {
    console.error('删除课程失败:', e)
    alert('删除失败')
  }
}

const unenroll = async (course: CourseItem) => {
  if (!confirm(`确定要退出课程「${course.name}」吗？`)) return
  try {
    await api.post('/api/courses/enroll', { course_id: course.id, undo: true })
    await courseStore.fetchCourses()
  } catch (e) {
    console.error('退课失败:', e)
    alert('退课失败')
  }
}

onMounted(async () => {
  await courseStore.fetchCourses()
})
</script>

<style lang="scss" scoped>
.courses-page {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-6);
  .page-title {
    h1 {
      font-size: var(--text-2xl); font-weight: var(--font-semibold); color: var(--text-primary);
      display: flex; align-items: center; gap: var(--space-2); margin: 0;
      i { color: rgb(var(--green)); }
    }
    .page-subtitle { font-size: var(--text-sm); color: var(--text-secondary); margin: var(--space-2) 0 0 0; }
  }
}

.card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6); box-shadow: var(--shadow-sm);
}

.section-head {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-4);
  .card-title { margin: 0; }
  .actions { display: flex; align-items: center; gap: var(--space-3); .doc-count { font-size: var(--text-sm); color: var(--text-muted); } }
}

.data-table {
  width: 100%; border-collapse: collapse; font-size: var(--text-sm);
  thead th { background: var(--bg-tertiary); color: var(--text-secondary); font-weight: var(--font-semibold); font-size: var(--text-xs); padding: var(--space-3) var(--space-4); text-align: left; border-bottom: 2px solid var(--border); white-space: nowrap; }
  tbody td { padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--border); color: var(--text-secondary); &.td-mono { font-family: var(--font-mono); } }
  tbody tr:hover { background: var(--bg-tertiary); }
}

.course-info { display: flex; align-items: center; gap: var(--space-2); i { color: rgb(var(--green)); } }

.status-badge {
  display: inline-flex; align-items: center; padding: var(--space-1) var(--space-3); border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: var(--font-medium);
  &.status-active { background: rgba(16, 185, 129, 0.1); color: rgb(6, 118, 71); }
  &.status-ended { background: var(--bg-tertiary); color: var(--text-secondary); }
}

.actions-cell { display: flex; gap: var(--space-2); flex-wrap: wrap; }

.btn {
  display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--font-medium); cursor: pointer; transition: all 0.2s ease; border: 1px solid transparent;
  &.btn-sm { height: 32px; padding: 0 var(--space-3); font-size: var(--text-xs); }
  &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); border: none; box-shadow: 0 2px 0 rgba(var(--ink), 0.2); &:hover:not(:disabled) { background: rgb(25, 75, 55); } &:disabled { opacity: 0.6; cursor: not-allowed; } }
  &.btn-secondary { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border); &:hover { background: var(--bg-tertiary); border-color: rgb(var(--green)); } }
  &.btn-danger { background: var(--bg-card); color: rgb(239, 68, 68); border: 1px solid rgba(239, 68, 68, 0.35); &:hover { background: rgba(239, 68, 68, 0.1); } }
}

.empty-state { text-align: center; padding: var(--space-10) 0; color: var(--text-muted); i { font-size: 34px; display: block; margin-bottom: var(--space-2); } p { margin: 0; font-size: var(--text-sm); } }

.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 1000;
}

.modal {
  background: var(--bg-card); border-radius: var(--radius-lg); padding: var(--space-6); width: 480px; max-width: 90vw; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-4);
  h3 { font-size: var(--text-lg); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; }
  .btn-close { background: none; border: none; cursor: pointer; font-size: var(--text-xl); color: var(--text-muted); padding: 0; &:hover { color: var(--text-primary); } }
}

.modal-body {
  display: flex; flex-direction: column; gap: var(--space-4);
  .form-group { display: flex; flex-direction: column; gap: var(--space-2);
    label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); }
    .form-input { height: 40px; padding: 0 var(--space-3); border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--bg-card); font-size: var(--text-base); color: var(--text-primary); &:focus { outline: none; border-color: rgb(var(--green)); box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.15); } }
    .form-textarea { height: auto; padding: var(--space-3); resize: vertical; font-family: var(--font-sans); }
  }
}

.modal-footer {
  display: flex; justify-content: flex-end; gap: var(--space-3); margin-top: var(--space-6);
}

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
