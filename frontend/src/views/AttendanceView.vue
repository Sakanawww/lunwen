<template>
  <div class="attendance-page">
    <div class="page-header">
      <div class="page-title">
        <h1>考勤管理</h1>
        <p class="page-subtitle">发起考勤、查看出勤率、生成缺勤预警</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect v-model="selectedCourseId" :options="courseOptions" placeholder="选择课程…" />
      </div>
      <div class="filter-group">
        <button class="btn btn-primary" @click="createSession" :disabled="!selectedCourseId || isCreating">
          <i class="ri-add-line"></i>
          <span>{{ isCreating ? '创建中…' : '发起考勤' }}</span>
        </button>
      </div>
    </div>

    <!-- 考勤统计卡片 -->
    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.session_count }}</div>
        <div class="stat-label">考勤次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.overall_rate }}%</div>
        <div class="stat-label">总体出勤率</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.present_records }}</div>
        <div class="stat-label">出勤人次</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ warningStudents.length }}</div>
        <div class="stat-label">缺勤预警</div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title"><i class="ri-line-chart-line"></i> 出勤率趋势</div>
        </div>
        <div class="chart-container">
          <VChart :option="trendOption" auto-resize />
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title"><i class="ri-bar-chart-line"></i> 缺勤排行榜</div>
        </div>
        <div class="chart-container">
          <VChart :option="absentRankOption" auto-resize />
        </div>
      </div>
    </div>

    <!-- 考勤课次列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-calendar-check-line"></i> 考勤课次</h2>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>状态</th>
              <th>签到人数</th>
              <th>出勤率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in sessions" :key="s.id">
              <td>{{ s.session_date }}</td>
              <td>
                <span class="badge" :class="s.status === 'open' ? 'badge-green' : 'badge-gray'">
                  {{ s.status === 'open' ? '进行中' : '已关闭' }}
                </span>
              </td>
              <td>{{ s.signed_count }} / {{ s.total_students }}</td>
              <td>{{ s.attendance_rate }}%</td>
              <td>
                <button class="btn btn-sm btn-secondary" @click="viewRecords(s.id)">明细</button>
                <button v-if="s.status === 'open'" class="btn btn-sm btn-secondary" @click="closeSession(s.id)">关闭</button>
                <button class="btn btn-sm btn-danger" @click="deleteSession(s.id)">删除</button>
              </td>
            </tr>
            <tr v-if="sessions.length === 0">
              <td colspan="5" class="empty">暂无考勤记录，点击「发起考勤」开始</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 缺勤预警区 -->
    <div class="card" v-if="warningStudents.length > 0">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-alarm-warning-line" style="color: rgb(var(--destructive))"></i> 缺勤预警</h2>
        <button class="btn btn-primary btn-sm" @click="generateWarnings" :disabled="isWarning">
          <i class="ri-magic-line"></i> {{ isWarning ? '生成中…' : '生成预警文案' }}
        </button>
      </div>
      <div class="warning-body">
        <div class="warning-students">
          <p class="warning-hint">连续缺勤 ≥ 3 次的学生（共 {{ warningStudents.length }} 人）：</p>
          <div class="warning-list">
            <div class="warning-item" v-for="s in warningStudents" :key="s.user_id">
              <span class="warning-name">{{ s.real_name }}</span>
              <span class="warning-count">缺勤 {{ s.absent_count }} 次</span>
            </div>
          </div>
        </div>
        <div class="warning-result" v-if="warningText">
          <p class="warning-hint">AI 生成的预警提醒（考勤预警 Agent）：</p>
          <pre class="warning-text">{{ warningText }}</pre>
        </div>
      </div>
    </div>

    <ConfirmDialog
      v-model:visible="showConfirm"
      title="删除考勤"
      message="确认删除该次考勤？删除后不可恢复。"
      type="danger"
      confirm-text="删除"
      @confirm="doDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'

const courseStore = useCourseStore()
const router = useRouter()
const toast = useToast()

const selectedCourseId = ref<number | null>(null)
const courseOptions = computed(() => courseStore.courses.map(c => ({ value: c.id, label: c.name })))

const isCreating = ref(false)
const isWarning = ref(false)
const sessions = ref<any[]>([])
const stats = ref<any>(null)
const warningStudents = ref<any[]>([])
const warningText = ref('')

const showConfirm = ref(false)
const confirmDeleteId = ref<number | null>(null)

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const statusLabel = (s: string) => ({ present: '出勤', late: '迟到', leave: '请假', absent: '旷课' }[s] || s)
const statusBadge = (s: string) => ({ present: 'badge-green', late: 'badge-yellow', leave: 'badge-blue', absent: 'badge-red' }[s] || 'badge-gray')

const trendOption = computed(() => {
  const trend = stats.value?.trend || []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: trend.map((t: any) => t.date), axisLabel: { color: '#6B6B6B' } },
    yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#F0EFEA', type: 'dashed' } }, axisLabel: { color: '#6B6B6B', formatter: '{value}%' } },
    series: [{
      type: 'line', smooth: true, data: trend.map((t: any) => t.rate),
      lineStyle: { width: 2.5, color: '#10B981' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(16,185,129,0.3)' }, { offset: 1, color: 'rgba(16,185,129,0.01)' }]) },
      itemStyle: { color: '#10B981' },
    }],
  }
})

const absentRankOption = computed(() => {
  const students = (stats.value?.students || []).filter((s: any) => s.absent > 0).slice(0, 10)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#F0EFEA', type: 'dashed' } }, axisLabel: { color: '#6B6B6B' } },
    yAxis: { type: 'category', data: students.map((s: any) => s.real_name).reverse(), axisLabel: { color: '#6B6B6B' } },
    series: [{
      type: 'bar', data: students.map((s: any) => s.absent).reverse(),
      itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#EF4444' }, { offset: 1, color: '#F87171' }]), borderRadius: [0, 4, 4, 0] },
    }],
  }
})

const loadData = async () => {
  if (!selectedCourseId.value) return
  const cid = selectedCourseId.value
  try {
    const [sessRes, statsRes, warnRes] = await Promise.all([
      fetch(`/api/attendance/sessions/${cid}`, { headers: authHeaders() }),
      fetch(`/api/attendance/stats/${cid}`, { headers: authHeaders() }),
      fetch(`/api/attendance/warnings/${cid}?threshold=3`, { headers: authHeaders() }),
    ])
    if (sessRes.ok) sessions.value = (await sessRes.json()).sessions
    if (statsRes.ok) stats.value = await statsRes.json()
    if (warnRes.ok) warningStudents.value = (await warnRes.json()).students
  } catch (e) { console.error(e) }
}

const createSession = async () => {
  if (!selectedCourseId.value) return
  isCreating.value = true
  try {
    const res = await fetch(`/api/attendance/sessions`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ course_id: selectedCourseId.value }),
    })
    if (res.ok) { await loadData(); toast.success('考勤已发起') }
  } finally { isCreating.value = false }
}

const closeSession = async (id: number) => {
  try {
    const res = await fetch(`/api/attendance/sessions/${id}/close`, { method: 'PUT', headers: authHeaders() })
    if (res.ok) { await loadData(); toast.success('已关闭签到') } else { toast.error('操作失败') }
  } catch { toast.error('网络错误') }
}

const deleteSession = (id: number) => {
  confirmDeleteId.value = id
  showConfirm.value = true
}

const doDelete = async () => {
  showConfirm.value = false
  if (!confirmDeleteId.value) return
  try {
    const res = await fetch(`/api/attendance/sessions/${confirmDeleteId.value}`, { method: 'DELETE', headers: authHeaders() })
    if (res.ok) { await loadData(); toast.success('已删除') } else toast.error('删除失败')
  } catch { toast.error('网络错误') } finally { confirmDeleteId.value = null }
}

const viewRecords = (sessionId: number) => {
  router.push({ name: 'AttendanceSession', params: { id: sessionId } })
}

const updateRecord = async (recordId: number, status: string) => {
  try {
    const res = await fetch(`/api/attendance/records`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ record_id: recordId, status }),
    })
    if (res.ok) { toast.success('已修正') } else { toast.error('修正失败') }
  } catch { toast.error('网络错误') }
}

const generateWarnings = async () => {
  if (!selectedCourseId.value) return
  isWarning.value = true
  warningText.value = ''
  try {
    const res = await fetch(`/api/attendance/warnings/${selectedCourseId.value}/generate?threshold=3`, {
      method: 'POST', headers: authHeaders(),
    })
    if (!res.ok) { toast.error('生成失败'); return }
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
        try {
          const obj = JSON.parse(payload)
          if (obj.token) warningText.value += obj.token
        } catch {}
      }
    }
  } finally { isWarning.value = false }
}

watch(selectedCourseId, (v) => { if (v) { courseStore.setActiveCourse(v); loadData() } })
onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  if (courseStore.courses.length > 0) selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
})
</script>

<style lang="scss" scoped>
.attendance-page { padding: var(--space-6); max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); h1 { font-size: var(--text-3xl); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; } .page-subtitle { font-size: var(--text-sm); color: var(--text-secondary); margin: var(--space-2) 0 0 0; } }
.filter-bar { display: flex; align-items: flex-end; gap: var(--space-6); flex-wrap: wrap; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); margin-bottom: var(--space-6); .filter-group { display: flex; flex-direction: column; gap: var(--space-2); label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); display: inline-flex; align-items: center; gap: var(--space-1); i { color: rgb(var(--green)); } } } }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-4); margin-bottom: var(--space-6); @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); } }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-4); box-shadow: var(--shadow-sm); transition: all 0.2s ease; animation: fadeUp 0.5s ease-out both; &:hover { border-color: rgba(var(--ink), 0.1); box-shadow: var(--shadow-md); transform: translateY(-2px); } &:nth-child(1) { animation-delay: 0s; } &:nth-child(2) { animation-delay: 0.08s; } &:nth-child(3) { animation-delay: 0.16s; } &:nth-child(4) { animation-delay: 0.24s; } .stat-value { font-size: 28px; font-weight: var(--font-bold); color: var(--text-primary); font-variant-numeric: tabular-nums; } .stat-label { font-size: var(--text-sm); color: var(--text-secondary); margin-top: var(--space-1); } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); margin-bottom: var(--space-6); @media (max-width: 1024px) { grid-template-columns: 1fr; } }
.chart-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; animation: fadeUp 0.6s ease-out both; }
.chart-header { margin-bottom: var(--space-2); .chart-title { font-size: var(--text-lg); font-weight: var(--font-semibold); display: flex; align-items: center; gap: var(--space-2); i { color: rgb(var(--green)); } } }
.chart-container { flex: 1; min-height: 280px; :deep(.echarts) { width: 100%; height: 100%; min-height: 280px; } }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); margin-bottom: var(--space-6); animation: fadeUp 0.6s ease-out both; animation-delay: 0.3s; }
.section-head { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); .card-title { font-size: var(--text-lg); font-weight: var(--font-semibold); display: flex; align-items: center; gap: var(--space-2); margin: 0; } }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th, td { padding: var(--space-3) var(--space-4); text-align: left; border-bottom: 1px solid var(--border); font-size: var(--text-sm); } th { color: var(--text-secondary); font-weight: var(--font-medium); background: var(--bg-tertiary); } tbody tr { transition: background 0.15s ease; &:hover { background: var(--bg-tertiary); } } .empty { text-align: center; color: var(--text-muted); padding: var(--space-10); } }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: var(--font-medium); &.badge-green { background: rgba(16,185,129,0.15); color: #059669; } &.badge-gray { background: var(--bg-tertiary); color: var(--text-secondary); } &.badge-yellow { background: rgba(245,158,11,0.15); color: #D97706; } &.badge-blue { background: rgba(59,130,246,0.15); color: #2563EB; } &.badge-red { background: rgba(239,68,68,0.15); color: #DC2626; } }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); border: 1px solid var(--border); background: var(--bg-card); transition: all 0.2s; &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); border-color: rgb(var(--green)); } &.btn-secondary { color: var(--text-primary); } &.btn-danger { color: rgb(var(--destructive)); border-color: rgba(var(--destructive),0.3); } &.btn-sm { padding: 4px 10px; font-size: 12px; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.warning-body { padding: var(--space-4) var(--space-6); display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-6); @media (max-width: 768px) { grid-template-columns: 1fr; } }
.warning-hint { font-size: var(--text-sm); color: var(--text-secondary); margin-bottom: var(--space-3); }
.warning-list { display: flex; flex-direction: column; gap: var(--space-2); }
.warning-item { display: flex; justify-content: space-between; padding: var(--space-2) var(--space-3); background: var(--bg-tertiary); border-radius: var(--radius-md); .warning-name { font-weight: var(--font-medium); } .warning-count { color: rgb(var(--destructive)); font-size: var(--text-sm); } }
.warning-text { white-space: pre-wrap; word-wrap: break-word; background: var(--bg-tertiary); padding: var(--space-4); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: var(--text-sm); line-height: 1.7; max-height: 300px; overflow-y: auto; }
.form-select-sm { padding: 2px 6px; font-size: 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-card); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 999; animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal-content { background: var(--bg-card); border-radius: var(--radius-lg); max-width: 700px; width: 90%; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column; animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: none; } }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); h3 { margin: 0; } .modal-close { background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary); } }
.modal-body { padding: var(--space-4) var(--space-6); overflow-y: auto; }
</style>
