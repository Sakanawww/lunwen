<template>
  <div class="diagnose-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/performance')"><i class="ri-arrow-left-line"></i> 返回平时表现</button>
        <h1>AI 学情诊断 — {{ studentName }}</h1>
      </div>
    </div>

    <div v-if="loading" class="loading-state"><i class="ri-loader-4-line spin"></i> 加载中…</div>

    <template v-if="!loading && scores">
      <!-- 四维得分卡片 -->
      <div class="scores-grid">
        <div class="score-card"><div class="score-val">{{ scores.attendance_score }}</div><div class="score-label">出勤 (30%)</div></div>
        <div class="score-card"><div class="score-val">{{ scores.assignment_score }}</div><div class="score-label">作业 (30%)</div></div>
        <div class="score-card"><div class="score-val">{{ scores.practice_score }}</div><div class="score-label">练习 (20%)</div></div>
        <div class="score-card"><div class="score-val">{{ scores.engagement_score }}</div><div class="score-label">答疑 (20%)</div></div>
        <div class="score-card total"><div class="score-val">{{ scores.total_score }}</div><div class="score-label">总分</div></div>
      </div>

      <!-- AI 诊断报告 -->
      <div class="diagnose-card">
        <div class="diagnose-header">
          <h2><i class="ri-microscope-line"></i> AI 学情分析报告</h2>
          <span class="agent-tag">学情分析 Agent</span>
        </div>
        <div class="diagnose-body">
          <pre v-if="diagnoseText" class="diagnose-text">{{ diagnoseText }}<span v-if="isStreaming" class="cursor">▋</span></pre>
          <div v-else class="diagnose-loading">
            <i class="ri-loader-4-line spin"></i>
            <p>正在生成诊断报告…</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCourseStore } from '@/stores/course.store'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()
const toast = useToast()

const loading = ref(true)
const scores = ref<any>(null)
const studentName = ref('')
const diagnoseText = ref('')
const isStreaming = ref(false)

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const loadAndDiagnose = async () => {
  const studentId = route.params.studentId as string
  const courseId = courseStore.currentCourseId || (courseStore.courses[0]?.id ?? null)
  if (!courseId) { toast.error('未选择课程'); return }

  // 先加载该课程所有学生分数，找到当前学生
  loading.value = true
  try {
    const res = await fetch(`/api/performance/scores/${courseId}`, { headers: authHeaders() })
    if (res.ok) {
      const data = await res.json()
      const found = data.scores?.find((s: any) => String(s.student_id) === studentId)
      if (found) {
        scores.value = found
        studentName.value = found.real_name
      }
    }
  } catch { toast.error('加载分数失败') } finally { loading.value = false }

  // 发起 SSE 诊断
  isStreaming.value = true
  try {
    const res = await fetch('/api/performance/diagnose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ course_id: courseId, student_id: Number(studentId) }),
    })
    if (!res.ok) { diagnoseText.value = '诊断请求失败'; isStreaming.value = false; return }
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
  } catch { diagnoseText.value = '诊断失败' } finally { isStreaming.value = false }
}

onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  await loadAndDiagnose()
})
</script>

<style lang="scss" scoped>
.diagnose-page { padding: var(--space-6); max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); .header-left { display: flex; align-items: center; gap: var(--space-4); } h1 { font-size: var(--text-2xl); font-weight: var(--font-semibold); margin: 0; } }
.back-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-card); cursor: pointer; font-size: var(--text-sm); color: var(--text-secondary); transition: all 0.2s; &:hover { color: var(--text-primary); } }
.loading-state { text-align: center; padding: var(--space-16); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
.scores-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
.score-card { text-align: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5) var(--space-4); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; .score-val { font-size: 32px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; } .score-label { font-size: var(--text-xs); color: var(--text-secondary); margin-top: 4px; } &.total { background: rgba(var(--green),0.08); .score-val { color: rgb(var(--green)); } } &:nth-child(1) { animation-delay: 0s; } &:nth-child(2) { animation-delay: 0.08s; } &:nth-child(3) { animation-delay: 0.16s; } &:nth-child(4) { animation-delay: 0.24s; } &:nth-child(5) { animation-delay: 0.32s; } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.diagnose-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; animation: fadeUp 0.4s ease-out both; animation-delay: 0.4s; }
.diagnose-header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border); h2 { font-size: var(--text-lg); font-weight: var(--font-semibold); margin: 0; display: flex; align-items: center; gap: var(--space-2); i { color: rgb(var(--green)); } } }
.agent-tag { font-size: var(--text-xs); padding: 2px 10px; border-radius: 12px; background: rgba(var(--green),0.1); color: rgb(var(--green)); font-weight: 500; }
.diagnose-body { padding: var(--space-6); }
.diagnose-text { white-space: pre-wrap; word-wrap: break-word; background: var(--bg-tertiary); padding: var(--space-4) var(--space-6); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: var(--text-sm); line-height: 1.8; margin: 0; max-height: none; }
.cursor { animation: blink 1s step-end infinite; color: rgb(var(--green)); }
@keyframes blink { 50% { opacity: 0; } }
.diagnose-loading { text-align: center; padding: var(--space-12); color: var(--text-muted); .spin { animation: spin 1s linear infinite; font-size: 32px; } p { margin-top: var(--space-3); } }
</style>
