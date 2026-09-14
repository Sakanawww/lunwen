<template>
  <div class="session-detail-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/attendance')"><i class="ri-arrow-left-line"></i> 返回考勤</button>
        <h1>考勤明细 — {{ sessionDate }}</h1>
      </div>
      <div class="header-right">
        <span class="badge" :class="sessionStatus === 'open' ? 'badge-green' : 'badge-gray'">{{ sessionStatus === 'open' ? '进行中' : '已关闭' }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state"><i class="ri-loader-4-line spin"></i> 加载中…</div>

    <template v-if="!loading">
      <!-- 统计概览 -->
      <div class="stats-grid">
        <div class="stat-card"><span class="stat-val">{{ summary.total }}</span><span class="stat-label">总人数</span></div>
        <div class="stat-card"><span class="stat-val green">{{ summary.present }}</span><span class="stat-label">已签到</span></div>
        <div class="stat-card"><span class="stat-val yellow">{{ summary.late }}</span><span class="stat-label">迟到</span></div>
        <div class="stat-card"><span class="stat-val blue">{{ summary.leave }}</span><span class="stat-label">请假</span></div>
        <div class="stat-card"><span class="stat-val red">{{ summary.absent }}</span><span class="stat-label">缺勤</span></div>
      </div>

      <!-- 签到明细表 -->
      <div class="card">
        <div class="section-head"><h2 class="card-title"><i class="ri-list-check-2"></i> 签到明细</h2></div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr><th>学号</th><th>姓名</th><th>签到状态</th><th>签到时间</th><th>操作</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in records" :key="r.record_id">
                <td class="td-mono">{{ r.student_no || '—' }}</td>
                <td>{{ r.real_name }}</td>
                <td><span class="badge" :class="statusClass(r.status)">{{ statusLabel(r.status) }}</span></td>
                <td class="td-mono">{{ r.signed_at || '—' }}</td>
                <td>
                  <select class="status-select" :value="r.status" @change="updateStatus(r.record_id, ($event.target as HTMLSelectElement).value)">
                    <option value="present">签到</option>
                    <option value="late">迟到</option>
                    <option value="leave">请假</option>
                    <option value="absent">缺勤</option>
                  </select>
                </td>
              </tr>
              <tr v-if="records.length === 0"><td colspan="5" class="empty">暂无签到记录</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const loading = ref(true)
const records = ref<any[]>([])
const sessionStatus = ref('closed')
const sessionDate = ref('')

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const summary = computed(() => ({
  total: records.value.length,
  present: records.value.filter(r => r.status === 'present').length,
  late: records.value.filter(r => r.status === 'late').length,
  leave: records.value.filter(r => r.status === 'leave').length,
  absent: records.value.filter(r => r.status === 'absent').length,
}))

const statusClass = (s: string) => ({ present: 'badge-green', late: 'badge-yellow', leave: 'badge-blue', absent: 'badge-red' }[s] || 'badge-gray')
const statusLabel = (s: string) => ({ present: '签到', late: '迟到', leave: '请假', absent: '缺勤' }[s] || s)

const loadRecords = async () => {
  const sid = route.params.id as string
  loading.value = true
  try {
    const res = await fetch(`/api/attendance/sessions/${sid}/records`, { headers: authHeaders() })
    if (res.ok) {
      const data = await res.json()
      records.value = data.records || []
      sessionStatus.value = data.status
      sessionDate.value = data.session_date || ''
    }
  } catch { toast.error('加载失败') } finally { loading.value = false }
}

const updateStatus = async (recordId: number, status: string) => {
  try {
    const res = await fetch('/api/attendance/records', {
      method: 'PUT', headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ record_id: recordId, status }),
    })
    if (res.ok) { toast.success('已修正'); await loadRecords() }
    else toast.error('修正失败')
  } catch { toast.error('网络错误') }
}

onMounted(() => loadRecords())
</script>

<style lang="scss" scoped>
.session-detail-page { padding: var(--space-6); max-width: 1000px; margin: 0 auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-6); .header-left { display: flex; align-items: center; gap: var(--space-4); } h1 { font-size: var(--text-2xl); font-weight: var(--font-semibold); margin: 0; } }
.back-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-card); cursor: pointer; font-size: var(--text-sm); color: var(--text-secondary); transition: all 0.2s; &:hover { color: var(--text-primary); } }
.loading-state { text-align: center; padding: var(--space-16); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
.stat-card { text-align: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; .stat-val { display: block; font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; &.green { color: #059669; } &.yellow { color: #D97706; } &.blue { color: #2563EB; } &.red { color: #DC2626; } } .stat-label { font-size: var(--text-xs); color: var(--text-secondary); } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; animation-delay: 0.2s; }
.section-head { padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); .card-title { font-size: var(--text-lg); font-weight: var(--font-semibold); margin: 0; display: flex; align-items: center; gap: var(--space-2); } }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th, td { padding: var(--space-3) var(--space-4); text-align: left; border-bottom: 1px solid var(--border); font-size: var(--text-sm); } th { color: var(--text-secondary); font-weight: var(--font-medium); background: var(--bg-tertiary); } tbody tr { transition: background 0.15s; &:hover { background: var(--bg-tertiary); } } }
.td-mono { font-family: var(--font-mono); font-size: var(--text-sm); }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; &.badge-green { background: rgba(16,185,129,0.15); color: #059669; } &.badge-gray { background: var(--bg-tertiary); color: var(--text-secondary); } &.badge-yellow { background: rgba(245,158,11,0.15); color: #D97706; } &.badge-blue { background: rgba(59,130,246,0.15); color: #2563EB; } &.badge-red { background: rgba(239,68,68,0.15); color: #DC2626; } }
.status-select { padding: 4px 8px; font-size: var(--text-sm); border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-card); cursor: pointer; }
.empty { text-align: center; color: var(--text-muted); padding: var(--space-10); }
</style>
