<template>
  <div class="my-performance-page">
    <div class="page-header">
      <div class="page-title">
        <h1>我的学情</h1>
        <p class="page-subtitle">查看出勤记录、平时表现与 AI 学情诊断</p>
      </div>
    </div>

    <!-- 课程选择 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect v-model="selectedCourseId" :options="courseOptions" placeholder="选择课程…" />
      </div>
    </div>

    <div v-if="selectedCourseId" class="content-grid">
      <!-- 考勤卡片 -->
      <div class="card" v-if="attendance">
        <div class="section-head">
          <h2 class="card-title"><i class="ri-calendar-check-line"></i> 我的考勤</h2>
        </div>
        <div class="attendance-summary">
          <div class="summary-stats">
            <div class="ss-item"><span class="ss-val">{{ attendance.attendance_rate }}%</span><span class="ss-label">出勤率</span></div>
            <div class="ss-item"><span class="ss-val">{{ attendance.present }}</span><span class="ss-label">出勤</span></div>
            <div class="ss-item"><span class="ss-val">{{ attendance.late }}</span><span class="ss-label">迟到</span></div>
            <div class="ss-item"><span class="ss-val">{{ attendance.absent }}</span><span class="ss-label">缺勤</span></div>
            <div class="ss-item"><span class="ss-val">{{ attendance.leave }}</span><span class="ss-label">请假</span></div>
          </div>
          <!-- 签到入口 -->
          <div class="sign-area" v-if="attendance.open_session">
            <button class="btn btn-primary" @click="signPresent">
              <i class="ri-check-line"></i> 签到
            </button>
            <span class="sign-hint">当前有进行中的考勤（{{ attendance.open_session.session_date }}），点击签到</span>
          </div>
          <!-- 考勤记录列表 -->
          <div class="record-list">
            <div class="record-item" v-for="r in attendance.records" :key="r.session_id">
              <span class="record-date">{{ r.session_date }}</span>
              <span class="badge" :class="statusBadge(r.my_status)">{{ statusLabel(r.my_status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 平时表现卡片 -->
      <div class="card" v-if="performance">
        <div class="section-head">
          <h2 class="card-title"><i class="ri-bar-chart-line"></i> 平时表现</h2>
        </div>
        <div class="perf-body">
          <div class="perf-total">
            <div class="perf-total-val">{{ performance.total_score }}</div>
            <div class="perf-total-label">平时分总分</div>
          </div>
          <div class="perf-dims">
            <div class="perf-dim">
              <span class="dim-label">出勤</span>
              <div class="dim-bar"><div class="dim-fill" :style="{ width: performance.attendance_score + '%' }"></div></div>
              <span class="dim-val">{{ performance.attendance_score }}</span>
            </div>
            <div class="perf-dim">
              <span class="dim-label">作业</span>
              <div class="dim-bar"><div class="dim-fill" :style="{ width: performance.assignment_score + '%' }"></div></div>
              <span class="dim-val">{{ performance.assignment_score }}</span>
            </div>
            <div class="perf-dim">
              <span class="dim-label">练习</span>
              <div class="dim-bar"><div class="dim-fill" :style="{ width: performance.practice_score + '%' }"></div></div>
              <span class="dim-val">{{ performance.practice_score }}</span>
            </div>
            <div class="perf-dim">
              <span class="dim-label">答疑</span>
              <div class="dim-bar"><div class="dim-fill" :style="{ width: performance.engagement_score + '%' }"></div></div>
              <span class="dim-val">{{ performance.engagement_score }}</span>
            </div>
          </div>
          <button class="btn btn-primary" @click="diagnose">
            <i class="ri-microscope-line"></i> AI 学情诊断
          </button>
        </div>
      </div>
    </div>

    <!-- 诊断面板 -->
    <div class="diagnose-panel" v-if="showDiagnose">
      <div class="diagnose-header">
        <h2><i class="ri-microscope-line"></i> AI 学情诊断报告</h2>
        <button class="modal-close" @click="showDiagnose = false">×</button>
      </div>
      <div class="diagnose-body">
        <pre v-if="diagnoseText" class="diagnose-text">{{ diagnoseText }}</pre>
        <div v-else class="diagnose-loading"><i class="ri-loader-4-line spin"></i> 正在生成诊断报告…</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { useAuthStore } from '@/stores/auth.store'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const selectedCourseId = ref<number | null>(null)
const courseOptions = computed(() => courseStore.courses.map(c => ({ value: c.id, label: c.name })))
const attendance = ref<any>(null)
const performance = ref<any>(null)
const showDiagnose = ref(false)
const diagnoseText = ref('')

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })
const statusLabel = (s: string) => ({ present: '出勤', late: '迟到', leave: '请假', absent: '旷课' }[s] || s)
const statusBadge = (s: string) => ({ present: 'badge-green', late: 'badge-yellow', leave: 'badge-blue', absent: 'badge-red' }[s] || 'badge-gray')

const loadData = async () => {
  if (!selectedCourseId.value) return
  const cid = selectedCourseId.value
  try {
    const [attRes, perfRes] = await Promise.all([
      fetch(`/api/attendance/my/${cid}`, { headers: authHeaders() }),
      fetch(`/api/performance/my/${cid}`, { headers: authHeaders() }),
    ])
    if (attRes.ok) attendance.value = await attRes.json()
    if (perfRes.ok) performance.value = await perfRes.json()
  } catch (e) { console.error(e) }
}

const signPresent = async () => {
  if (!attendance.value?.open_session) return
  await fetch('/api/attendance/sign', {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ session_id: attendance.value.open_session.session_id, status: 'present' }),
  })
  await loadData()
}

const diagnose = async () => {
  if (!selectedCourseId.value || !authStore.user) return
  diagnoseText.value = ''
  showDiagnose.value = true
  try {
    const res = await fetch('/api/performance/diagnose', {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ course_id: selectedCourseId.value, student_id: authStore.user.id }),
    })
    if (!res.ok) { diagnoseText.value = '诊断请求失败'; return }
    const reader = res.body?.getReader()
    if (!reader) return
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += new TextDecoder().decode(value)
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (payload === '[DONE]') continue
        try { const obj = JSON.parse(payload); if (obj.token) diagnoseText.value += obj.token } catch {}
      }
    }
  } catch (e) { diagnoseText.value = '诊断失败：' + e }
}

watch(selectedCourseId, (v) => { if (v) { courseStore.setActiveCourse(v); loadData() } })
onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
    await loadData()
  }
})
</script>

<style lang="scss" scoped>
.my-performance-page { padding: var(--space-6); max-width: 1000px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); h1 { font-size: var(--text-3xl); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; } .page-subtitle { font-size: var(--text-sm); color: var(--text-secondary); margin: var(--space-2) 0 0 0; } }
.filter-bar { display: flex; align-items: flex-end; gap: var(--space-6); flex-wrap: wrap; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); margin-bottom: var(--space-6); .filter-group { display: flex; flex-direction: column; gap: var(--space-2); label { font-size: var(--text-sm); font-weight: var(--font-medium); display: inline-flex; align-items: center; gap: var(--space-1); i { color: rgb(var(--green)); } } } }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); @media (max-width: 768px) { grid-template-columns: 1fr; } }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); transition: all 0.2s ease; animation: fadeUp 0.5s ease-out both; &:hover { box-shadow: var(--shadow-md); } &:nth-child(1) { animation-delay: 0s; } &:nth-child(2) { animation-delay: 0.15s; } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.section-head { padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); .card-title { font-size: var(--text-lg); font-weight: var(--font-semibold); display: flex; align-items: center; gap: var(--space-2); margin: 0; } }
.attendance-summary { padding: var(--space-4) var(--space-6); }
.summary-stats { display: flex; gap: var(--space-4); flex-wrap: wrap; margin-bottom: var(--space-4); .ss-item { text-align: center; .ss-val { font-size: 24px; font-weight: var(--font-bold); color: var(--text-primary); display: block; font-variant-numeric: tabular-nums; } .ss-label { font-size: var(--text-xs); color: var(--text-secondary); } } }
.sign-area { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); .sign-hint { font-size: var(--text-sm); color: var(--text-secondary); } }
.record-list { max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: var(--space-1); }
.record-item { display: flex; justify-content: space-between; padding: var(--space-2) var(--space-3); background: var(--bg-tertiary); border-radius: var(--radius-md); transition: background 0.15s ease; &:hover { background: rgba(var(--green), 0.08); } .record-date { font-size: var(--text-sm); color: var(--text-primary); } }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: var(--font-medium); &.badge-green { background: rgba(16,185,129,0.15); color: #059669; } &.badge-yellow { background: rgba(245,158,11,0.15); color: #D97706; } &.badge-blue { background: rgba(59,130,246,0.15); color: #2563EB; } &.badge-red { background: rgba(239,68,68,0.15); color: #DC2626; } &.badge-gray { background: var(--bg-tertiary); color: var(--text-secondary); } }
.perf-body { padding: var(--space-4) var(--space-6); }
.perf-total { text-align: center; margin-bottom: var(--space-4); .perf-total-val { font-size: 36px; font-weight: var(--font-bold); color: rgb(var(--green)); } .perf-total-label { font-size: var(--text-sm); color: var(--text-secondary); } }
.perf-dims { display: flex; flex-direction: column; gap: var(--space-3); margin-bottom: var(--space-4); }
.perf-dim { display: flex; align-items: center; gap: var(--space-2); .dim-label { width: 40px; font-size: var(--text-sm); color: var(--text-secondary); } .dim-bar { flex: 1; height: 8px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden; .dim-fill { height: 100%; background: linear-gradient(90deg, rgb(var(--green)), rgb(52, 211, 153)); border-radius: 4px; transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1); } } .dim-val { width: 40px; text-align: right; font-size: var(--text-sm); font-weight: var(--font-medium); } }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); border: 1px solid var(--border); background: var(--bg-card); transition: all 0.2s ease; &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); border-color: rgb(var(--green)); &:hover { box-shadow: 0 4px 12px rgba(var(--green), 0.3); transform: translateY(-1px); } } }
.diagnose-panel { position: fixed; bottom: 0; left: 0; right: 0; background: var(--bg-card); border-top: 1px solid var(--border); box-shadow: 0 -4px 20px rgba(0,0,0,0.1); z-index: 100; max-height: 50vh; overflow-y: auto; animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideUp { from { opacity: 0; transform: translateY(100%); } to { opacity: 1; transform: none; } }
.diagnose-header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); h2 { font-size: var(--text-lg); font-weight: var(--font-semibold); margin: 0; } .modal-close { background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary); } }
.diagnose-body { padding: var(--space-4) var(--space-6); }
.diagnose-text { white-space: pre-wrap; word-wrap: break-word; background: var(--bg-tertiary); padding: var(--space-4); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: var(--text-sm); line-height: 1.7; }
.diagnose-loading { text-align: center; padding: var(--space-8); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
