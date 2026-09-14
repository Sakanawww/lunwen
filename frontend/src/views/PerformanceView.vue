<template>
  <div class="performance-page">
    <div class="page-header">
      <div class="page-title">
        <h1>平时表现评估</h1>
        <p class="page-subtitle">四维平时分（出勤30% + 作业30% + 练习20% + 答疑20%）+ AI 学情诊断</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect v-model="selectedCourseId" :options="courseOptions" placeholder="选择课程…" />
      </div>
      <div class="filter-group">
        <button class="btn btn-primary" @click="loadScores" :disabled="!selectedCourseId">
          <i class="ri-refresh-line"></i> <span>刷新</span>
        </button>
      </div>
    </div>

    <!-- 总体概览 -->
    <div class="overview-grid" v-if="scores.length > 0">
      <div class="overview-card">
        <div class="overview-value">{{ avgTotal }}</div>
        <div class="overview-label">班级平均平时分</div>
      </div>
      <div class="overview-card">
        <div class="overview-value">{{ scores.length }}</div>
        <div class="overview-label">参评学生</div>
      </div>
      <div class="overview-card">
        <div class="overview-value">{{ excellentCount }}</div>
        <div class="overview-label">优秀（≥85）</div>
      </div>
      <div class="overview-card">
        <div class="overview-value">{{ passCount }}</div>
        <div class="overview-label">及格（≥60）</div>
      </div>
      <div class="overview-card alert" v-if="atRiskCount > 0">
        <div class="overview-value">{{ atRiskCount }}</div>
        <div class="overview-label">需关注（&lt;60）</div>
      </div>
    </div>

    <!-- 维度分布 + 学生得分构成 -->
    <div class="main-grid" v-if="scores.length > 0">
      <div class="dimension-card">
        <div class="chart-header">
          <div class="chart-title"><i class="ri-bar-chart-grouped-line"></i> 四维得分分布</div>
          <p class="chart-hint">班级均分 · 虚线标记为及格(60)和优秀(85)线</p>
        </div>
        <div class="dim-bars">
          <div class="dim-bar-item" v-for="(d, i) in dimensionStats" :key="d.label" :style="{ animationDelay: i * 0.1 + 's' }">
            <div class="dim-bar-header">
              <span class="dim-bar-label">{{ d.label }} <small>{{ d.weight }}</small></span>
              <span class="dim-bar-avg" :style="{ color: d.color }">{{ d.avg }}</span>
            </div>
            <div class="dim-bar-track">
              <div class="dim-bar-fill" :style="{ width: d.avg + '%', background: d.color }"></div>
              <div class="dim-bar-marker pass"></div>
              <div class="dim-bar-marker excellent"></div>
            </div>
            <div class="dim-bar-range">
              <span>最低 {{ d.min }}</span>
              <span>最高 {{ d.max }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title"><i class="ri-bar-chart-2-line"></i> 学生得分构成</div>
          <p class="chart-hint">按总分排序 · 四色堆叠展示各维度贡献</p>
        </div>
        <div class="chart-container">
          <VChart :option="stackOption" auto-resize />
        </div>
      </div>
    </div>

    <!-- 学生排名表 -->
    <div class="card ranking-card" v-if="scores.length > 0">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-trophy-line"></i> 学生排名</h2>
        <span class="rank-hint">点击「诊断」生成 AI 学情分析报告</span>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>姓名</th>
              <th>学号</th>
              <th>出勤</th>
              <th>作业</th>
              <th>练习</th>
              <th>答疑</th>
              <th>总分</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(s, i) in scores" :key="s.student_id">
              <td class="rank-cell" :class="rankClass(i)">{{ i + 1 }}</td>
              <td>{{ s.real_name }}</td>
              <td>{{ s.student_no }}</td>
              <td>{{ s.attendance_score }}</td>
              <td>{{ s.assignment_score }}</td>
              <td>{{ s.practice_score }}</td>
              <td>{{ s.engagement_score }}</td>
              <td class="total-cell" :style="{ color: totalColor(Number(s.total_score)) }">{{ s.total_score }}</td>
              <td><button class="btn btn-sm btn-primary" @click="diagnose(s)"><i class="ri-microscope-line"></i> 诊断</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="empty-state">
      <i class="ri-inbox-line"></i>
      <p>暂无数据，请选择课程后刷新</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { useToast } from '@/composables/useToast'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'

const courseStore = useCourseStore()
const router = useRouter()
const toast = useToast()
const selectedCourseId = ref<number | null>(null)
const courseOptions = computed(() => courseStore.courses.map(c => ({ value: c.id, label: c.name })))
const scores = ref<any[]>([])

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const avgTotal = computed(() => {
  if (!scores.value.length) return 0
  return (scores.value.reduce((s, x) => s + Number(x.total_score), 0) / scores.value.length).toFixed(1)
})
const excellentCount = computed(() => scores.value.filter(s => Number(s.total_score) >= 85).length)
const passCount = computed(() => scores.value.filter(s => Number(s.total_score) >= 60).length)
const atRiskCount = computed(() => scores.value.filter(s => Number(s.total_score) < 60).length)

const dimensionStats = computed(() => {
  if (!scores.value.length) return []
  const n = scores.value.length
  const dims = [
    { key: 'attendance_score', label: '出勤', weight: '30%' },
    { key: 'assignment_score', label: '作业', weight: '30%' },
    { key: 'practice_score', label: '练习', weight: '20%' },
    { key: 'engagement_score', label: '答疑', weight: '20%' },
  ]
  return dims.map(d => {
    const vals = scores.value.map(s => Number(s[d.key]))
    const avg = vals.reduce((a: number, b: number) => a + b, 0) / n
    return {
      label: d.label,
      weight: d.weight,
      avg: avg.toFixed(1),
      min: Math.min(...vals).toFixed(1),
      max: Math.max(...vals).toFixed(1),
      color: avg >= 85 ? '#10B981' : avg >= 60 ? '#F59E0B' : '#EF4444',
    }
  })
})

const rankClass = (i: number) => i === 0 ? 'rank-1' : i === 1 ? 'rank-2' : i === 2 ? 'rank-3' : ''

const totalColor = (score: number) => {
  if (score >= 85) return '#10B981'
  if (score >= 60) return 'var(--text-primary)'
  return '#EF4444'
}

const stackOption = computed(() => {
  if (!scores.value.length) return {}
  const sorted = [...scores.value].sort((a, b) => Number(b.total_score) - Number(a.total_score))
  const names = sorted.map(s => s.real_name)
  const raw = (key: string) => sorted.map(s => Number(s[key]))
  const att = raw('attendance_score')
  const asn = raw('assignment_score')
  const pra = raw('practice_score')
  const eng = raw('engagement_score')
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        const name = params[0]?.name ?? ''
        const total = params.reduce((s: number, p: any) => s + (p.value || 0), 0)
        let html = `<b>${name}</b> · 总分 ${total.toFixed(1)}<br/>`
        for (const p of params) html += `${p.marker} ${p.seriesName}：${p.value?.toFixed(1) ?? 0}<br/>`
        return html
      },
    },
    legend: { bottom: 0, left: 'center', textStyle: { color: '#6B6B6B', fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
    grid: { left: '3%', right: '4%', bottom: 40, top: 16, containLabel: true },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#6B6B6B', fontSize: 11, rotate: names.length > 6 ? 30 : 0, interval: 0 },
      axisLine: { lineStyle: { color: '#DAD5C8' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: '#6B6B6B', fontSize: 11 },
      splitLine: { lineStyle: { color: '#E8E3D6', type: 'dashed' } },
    },
    series: [
      { name: '出勤', type: 'bar', stack: 'total', data: att, barMaxWidth: 36, color: '#10B981', itemStyle: { borderRadius: [0, 0, 0, 0] } },
      { name: '作业', type: 'bar', stack: 'total', data: asn, barMaxWidth: 36, color: '#3B82F6' },
      { name: '练习', type: 'bar', stack: 'total', data: pra, barMaxWidth: 36, color: '#F59E0B' },
      { name: '答疑', type: 'bar', stack: 'total', data: eng, barMaxWidth: 36, color: '#8B5CF6', itemStyle: { borderRadius: [4, 4, 0, 0] } },
    ],
  }
})

const loadScores = async () => {
  if (!selectedCourseId.value) return
  try {
    const res = await fetch(`/api/performance/scores/${selectedCourseId.value}`, { headers: authHeaders() })
    if (res.ok) scores.value = (await res.json()).scores
  } catch (e) { console.error(e) }
}

const diagnose = (s: any) => {
  router.push({ name: 'PerformanceDiagnose', params: { studentId: s.student_id } })
}

watch(selectedCourseId, (v) => { if (v) { courseStore.setActiveCourse(v); loadScores() } })
onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  if (courseStore.courses.length > 0) selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
})
</script>

<style lang="scss" scoped>
.performance-page { padding: var(--space-6); max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); h1 { font-size: var(--text-3xl); font-weight: var(--font-semibold); color: var(--text-primary); margin: 0; } .page-subtitle { font-size: var(--text-sm); color: var(--text-secondary); margin: var(--space-2) 0 0 0; } }
.filter-bar { display: flex; align-items: flex-end; gap: var(--space-6); flex-wrap: wrap; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); margin-bottom: var(--space-6); .filter-group { display: flex; flex-direction: column; gap: var(--space-2); label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); display: inline-flex; align-items: center; gap: var(--space-1); i { color: rgb(var(--green)); } } } }
.overview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
.overview-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-4); box-shadow: var(--shadow-sm); transition: all 0.2s ease; animation: fadeUp 0.5s ease-out both; &:hover { border-color: rgba(var(--ink), 0.1); box-shadow: var(--shadow-md); transform: translateY(-2px); } &:nth-child(1) { animation-delay: 0s; } &:nth-child(2) { animation-delay: 0.08s; } &:nth-child(3) { animation-delay: 0.16s; } &:nth-child(4) { animation-delay: 0.24s; } &:nth-child(5) { animation-delay: 0.32s; } &.alert { border-color: rgba(var(--destructive), 0.3); .overview-value { color: rgb(var(--destructive)); } } .overview-value { font-size: 28px; font-weight: var(--font-bold); color: var(--text-primary); font-variant-numeric: tabular-nums; } .overview-label { font-size: var(--text-sm); color: var(--text-secondary); margin-top: var(--space-1); } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-bottom: var(--space-6); @media (max-width: 1024px) { grid-template-columns: 1fr; } }
.chart-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; animation: fadeUp 0.6s ease-out both; }
.chart-header { margin-bottom: var(--space-2); .chart-title { font-size: var(--text-lg); font-weight: var(--font-semibold); display: flex; align-items: center; gap: var(--space-2); i { color: rgb(var(--green)); } } }
.chart-container { flex: 1; min-height: 320px; :deep(.echarts) { width: 100%; height: 100%; min-height: 320px; } }
.chart-hint { font-size: var(--text-xs); color: var(--text-secondary); margin: var(--space-1) 0 0 0; }
.dimension-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; animation: fadeUp 0.6s ease-out both; animation-delay: 0.1s; }
.dim-bars { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: var(--space-5); padding: var(--space-4) 0; }
.dim-bar-item { animation: fadeUp 0.5s ease-out both; }
.dim-bar-header { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: var(--space-2); .dim-bar-label { font-size: var(--text-sm); font-weight: var(--font-medium); color: var(--text-primary); small { color: var(--text-secondary); font-weight: var(--font-regular); margin-left: var(--space-1); } } .dim-bar-avg { font-size: var(--text-lg); font-weight: var(--font-bold); font-variant-numeric: tabular-nums; } }
.dim-bar-track { position: relative; height: 10px; background: var(--bg-tertiary); border-radius: 5px; overflow: hidden; .dim-bar-fill { height: 100%; border-radius: 5px; transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1); } .dim-bar-marker { position: absolute; top: -2px; bottom: -2px; width: 2px; background: var(--text-muted); opacity: 0.5; &.pass { left: 60%; } &.excellent { left: 85%; } } }
.dim-bar-range { display: flex; justify-content: space-between; margin-top: var(--space-1); font-size: var(--text-xs); color: var(--text-secondary); }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); animation: fadeUp 0.6s ease-out both; animation-delay: 0.2s; }
.ranking-card { margin-bottom: var(--space-6); }
.section-head { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); .card-title { font-size: var(--text-lg); font-weight: var(--font-semibold); display: flex; align-items: center; gap: var(--space-2); margin: 0; } .rank-hint { font-size: var(--text-xs); color: var(--text-secondary); } }
.table-wrap { overflow-x: auto; max-height: 500px; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; th, td { padding: var(--space-3) var(--space-4); text-align: left; border-bottom: 1px solid var(--border); font-size: var(--text-sm); } th { color: var(--text-secondary); font-weight: var(--font-medium); background: var(--bg-tertiary); position: sticky; top: 0; z-index: 1; } tbody tr { transition: background 0.15s ease; &:hover { background: var(--bg-tertiary); } } .rank-cell { font-weight: var(--font-bold); text-align: center; &.rank-1 { color: #F59E0B; } &.rank-2 { color: #94A3B8; } &.rank-3 { color: #CA8A04; } } .total-cell { font-weight: var(--font-bold); color: rgb(var(--green)); } }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-4); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); border: 1px solid var(--border); background: var(--bg-card); &.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); border-color: rgb(var(--green)); } &.btn-sm { padding: 4px 10px; font-size: 12px; } }
.empty-state { text-align: center; padding: var(--space-16); color: var(--text-muted); i { font-size: 48px; display: block; margin-bottom: var(--space-3); } }
.diagnose-panel { position: fixed; bottom: 0; left: 0; right: 0; background: var(--bg-card); border-top: 1px solid var(--border); box-shadow: 0 -4px 20px rgba(0,0,0,0.1); z-index: 100; max-height: 50vh; overflow-y: auto; animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideUp { from { opacity: 0; transform: translateY(100%); } to { opacity: 1; transform: none; } }
.diagnose-header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); h2 { font-size: var(--text-lg); font-weight: var(--font-semibold); margin: 0; display: flex; align-items: center; gap: var(--space-2); } .modal-close { background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text-secondary); } }
.diagnose-body { padding: var(--space-4) var(--space-6); display: grid; grid-template-columns: 200px 1fr; gap: var(--space-6); @media (max-width: 768px) { grid-template-columns: 1fr; } }
.diagnose-scores { display: flex; flex-direction: column; gap: var(--space-2); }
.ds-item { display: flex; justify-content: space-between; padding: var(--space-2) var(--space-3); background: var(--bg-tertiary); border-radius: var(--radius-md); &.total { background: rgba(var(--green), 0.1); font-weight: var(--font-bold); } .ds-label { color: var(--text-secondary); font-size: var(--text-sm); } .ds-val { font-weight: var(--font-medium); } }
.diagnose-result { .diagnose-hint { font-size: var(--text-sm); color: var(--text-secondary); margin-bottom: var(--space-2); } }
.diagnose-text { white-space: pre-wrap; word-wrap: break-word; background: var(--bg-tertiary); padding: var(--space-4); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: var(--text-sm); line-height: 1.7; max-height: 300px; overflow-y: auto; }
.diagnose-loading { text-align: center; padding: var(--space-8); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
