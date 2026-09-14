<template>
  <div class="student-detail-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.back()"><i class="ri-arrow-left-line"></i> 返回</button>
        <h1 v-if="data">学生详情 — {{ data.student.real_name }}</h1>
      </div>
      <div class="header-right">
        <DropdownSelect v-model="selectedCourseId" :options="courseOptions" placeholder="选择课程…" />
      </div>
    </div>

    <div v-if="loading" class="loading-state"><i class="ri-loader-4-line spin"></i> 加载中…</div>

    <template v-if="data && !loading">
      <!-- 基本信息 -->
      <div class="info-card">
        <div class="info-avatar">{{ data.student.real_name.charAt(0) }}</div>
        <div class="info-main">
          <h2>{{ data.student.real_name }}</h2>
          <div class="info-meta">
            <span><i class="ri-id-card-line"></i> {{ data.student.student_no || '—' }}</span>
            <span><i class="ri-mail-line"></i> {{ data.student.username }}</span>
            <span><i class="ri-book-open-line"></i> {{ data.course_name }}</span>
            <span v-if="data.student.class_name"><i class="ri-team-line"></i> {{ data.student.class_name }}</span>
          </div>
        </div>
      </div>

      <!-- 四维得分概览 -->
      <div class="section">
        <h3 class="section-title"><i class="ri-bar-chart-line"></i> 平时分四维得分</h3>
        <div class="perf-grid">
          <div class="perf-card">
            <div class="perf-val">{{ data.performance.attendance_score }}</div>
            <div class="perf-label">出勤 (30%)</div>
          </div>
          <div class="perf-card">
            <div class="perf-val">{{ data.performance.assignment_score }}</div>
            <div class="perf-label">作业 (30%)</div>
          </div>
          <div class="perf-card">
            <div class="perf-val">{{ data.performance.practice_score }}</div>
            <div class="perf-label">练习 (20%)</div>
          </div>
          <div class="perf-card">
            <div class="perf-val">{{ data.performance.engagement_score }}</div>
            <div class="perf-label">答疑 (20%)</div>
          </div>
          <div class="perf-card total">
            <div class="perf-val">{{ data.performance.total_score }}</div>
            <div class="perf-label">总分</div>
          </div>
        </div>
      </div>

      <!-- 统计概览 -->
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-num">{{ data.attendance.present + data.attendance.late }}/{{ data.attendance.total }}</span>
          <span class="stat-label">出勤/总次</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ data.submissions.length }}</span>
          <span class="stat-label">作业提交</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ data.practices.length }}</span>
          <span class="stat-label">练习记录</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ data.question_count }}</span>
          <span class="stat-label">提问数</span>
        </div>
      </div>

      <div class="content-grid">
        <!-- 作业提交明细 -->
        <div class="section">
          <h3 class="section-title"><i class="ri-file-list-3-line"></i> 作业提交明细</h3>
          <div v-if="data.submissions.length === 0" class="empty">暂无作业提交</div>
          <div v-else class="sub-list">
            <div v-for="s in data.submissions" :key="s.id" class="sub-item">
              <div class="sub-info">
                <span class="sub-title">{{ s.assignment_title }}</span>
                <span class="sub-date">{{ s.submitted_at }}</span>
              </div>
              <div class="sub-right">
                <span v-if="s.score !== null" class="sub-score" :class="scoreClass(s.score)">{{ s.score }}</span>
                <span v-else class="sub-status">{{ s.status }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 练习记录 -->
        <div class="section">
          <h3 class="section-title"><i class="ri-edit-line"></i> 练习记录（近 30 条）</h3>
          <div v-if="data.practices.length === 0" class="empty">暂无练习记录</div>
          <div v-else class="practice-list">
            <div v-for="p in data.practices" :key="p.id" class="practice-item">
              <div class="practice-info">
                <span class="practice-stem">{{ p.stem }}…</span>
                <span class="practice-date">{{ p.created_at }}</span>
              </div>
              <i :class="p.is_correct ? 'ri-check-line correct' : 'ri-close-line wrong'"></i>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()
const toast = useToast()

const data = ref<any>(null)
const loading = ref(true)
const selectedCourseId = ref<number | null>(null)
const courseOptions = computed(() => courseStore.courses.map(c => ({ value: c.id, label: c.name })))

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const scoreClass = (score: number) => score >= 90 ? 'excellent' : score >= 60 ? 'pass' : 'fail'

const loadDetail = async () => {
  const studentId = route.params.id as string
  const courseId = selectedCourseId.value
  if (!courseId) { toast.error('未选择课程'); return }
  loading.value = true
  try {
    const res = await fetch(`/api/dashboard/students/${studentId}/detail?course_id=${courseId}`, { headers: authHeaders() })
    if (res.ok) data.value = await res.json()
    else toast.error('加载失败')
  } catch { toast.error('网络错误') } finally { loading.value = false }
}

watch(selectedCourseId, (v) => {
  if (v) { courseStore.setActiveCourse(v); loadDetail() }
})

onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0]?.id || null
  await loadDetail()
})
</script>

<style lang="scss" scoped>
.student-detail-page { padding: var(--space-6); max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-6); .header-left { display: flex; align-items: center; gap: var(--space-4); } .header-right { min-width: 180px; } h1 { font-size: var(--text-2xl); font-weight: var(--font-semibold); margin: 0; } }
.back-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-card); cursor: pointer; font-size: var(--text-sm); color: var(--text-secondary); transition: all 0.2s; &:hover { color: var(--text-primary); border-color: var(--text-muted); } }
.loading-state { text-align: center; padding: var(--space-16); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
.info-card { display: flex; align-items: center; gap: var(--space-4); background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-6); margin-bottom: var(--space-6); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.info-avatar { width: 56px; height: 56px; border-radius: 50%; background: rgba(var(--green),0.15); color: rgb(var(--green)); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; flex-shrink: 0; }
.info-main { h2 { font-size: var(--text-xl); font-weight: var(--font-semibold); margin: 0 0 var(--space-2) 0; } }
.info-meta { display: flex; gap: var(--space-5); flex-wrap: wrap; font-size: var(--text-sm); color: var(--text-secondary); span { display: inline-flex; align-items: center; gap: 4px; } }
.section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-6); margin-bottom: var(--space-6); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; animation-delay: 0.1s; }
.section-title { font-size: var(--text-base); font-weight: var(--font-semibold); margin: 0 0 var(--space-4) 0; display: flex; align-items: center; gap: var(--space-2); i { color: rgb(var(--green)); } }
.perf-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: var(--space-3); }
.perf-card { text-align: center; padding: var(--space-4); background: var(--bg-tertiary); border-radius: var(--radius-md); .perf-val { font-size: 28px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; } .perf-label { font-size: var(--text-xs); color: var(--text-secondary); margin-top: 4px; } &.total { background: rgba(var(--green),0.1); .perf-val { color: rgb(var(--green)); } } }
.stats-row { display: flex; gap: var(--space-4); margin-bottom: var(--space-6); flex-wrap: wrap; }
.stat-item { flex: 1; min-width: 120px; text-align: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4); box-shadow: var(--shadow-sm); .stat-num { display: block; font-size: 24px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; } .stat-label { font-size: var(--text-xs); color: var(--text-secondary); } }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-6); @media (max-width: 768px) { grid-template-columns: 1fr; } }
.empty { text-align: center; padding: var(--space-8); color: var(--text-muted); font-size: var(--text-sm); }
.sub-list, .practice-list { display: flex; flex-direction: column; gap: var(--space-2); max-height: 400px; overflow-y: auto; }
.sub-item, .practice-item { display: flex; align-items: center; justify-content: space-between; padding: var(--space-2) var(--space-3); background: var(--bg-tertiary); border-radius: var(--radius-md); transition: background 0.15s; &:hover { background: rgba(var(--ink),0.05); } }
.sub-info, .practice-info { display: flex; flex-direction: column; gap: 2px; .sub-title, .practice-stem { font-size: var(--text-sm); color: var(--text-primary); } .sub-date, .practice-date { font-size: var(--text-xs); color: var(--text-secondary); } }
.sub-score { font-weight: 700; font-variant-numeric: tabular-nums; &.excellent { color: rgb(var(--green)); } &.pass { color: var(--text-primary); } &.fail { color: #DC2626; } }
.sub-status { font-size: var(--text-xs); color: var(--text-secondary); }
.correct { color: rgb(var(--green)); font-size: 20px; }
.wrong { color: #DC2626; font-size: 20px; }
</style>
