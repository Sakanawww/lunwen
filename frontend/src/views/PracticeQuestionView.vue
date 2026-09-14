<template>
  <div class="practice-question-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/practice')"><i class="ri-arrow-left-line"></i> 返回练习列表</button>
        <h1>在线答题</h1>
      </div>
    </div>

    <div v-if="loading" class="loading-state"><i class="ri-loader-4-line spin"></i> 加载中…</div>

    <template v-if="question && !loading">
      <div class="question-card">
        <div class="question-meta">
          <span class="type-badge" :class="`type-${question.type}`">{{ typeLabel(question.type) }}</span>
          <span class="difficulty" v-if="question.difficulty">难度 {{ question.difficulty }}/5</span>
        </div>
        <div class="question-stem">{{ question.stem }}</div>

        <!-- 选择题 -->
        <div v-if="question.type === 'choice' && parsedOptions" class="options-list">
          <label
            v-for="(opt, i) in parsedOptions"
            :key="i"
            class="option-item"
            :class="{ selected: selectedAnswer === keys[i], correct: submitted && keys[i] === correctKey, wrong: submitted && selectedAnswer === keys[i] && keys[i] !== correctKey }"
          >
            <input type="radio" :value="keys[i]" v-model="selectedAnswer" :disabled="submitted" />
            <span class="option-key">{{ keys[i] }}</span>
            <span class="option-text">{{ opt }}</span>
            <i v-if="submitted && keys[i] === correctKey" class="ri-check-line correct-icon"></i>
            <i v-if="submitted && selectedAnswer === keys[i] && keys[i] !== correctKey" class="ri-close-line wrong-icon"></i>
          </label>
        </div>

        <!-- 填空/简答 -->
        <div v-else class="text-answer">
          <textarea
            v-model="textAnswer"
            :disabled="submitted"
            placeholder="请输入你的答案…"
            rows="4"
          ></textarea>
        </div>

        <!-- 结果反馈 -->
        <transition name="result">
          <div v-if="submitted" class="result-box" :class="isCorrect ? 'result-correct' : 'result-wrong'">
            <div class="result-header">
              <i :class="isCorrect ? 'ri-checkbox-circle-line' : 'ri-close-circle-line'"></i>
              <span>{{ isCorrect ? '回答正确！' : '回答错误' }}</span>
            </div>
            <div v-if="!isCorrect" class="result-answer">正确答案：{{ expectedAnswer }}</div>
          </div>
        </transition>

        <!-- 提交按钮 -->
        <div class="actions" v-if="!submitted">
          <button class="btn-primary" @click="submit" :disabled="!canSubmit">提交答案</button>
        </div>
        <div class="actions" v-else>
          <button class="btn-secondary" @click="router.push('/practice')">返回列表</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCourseStore } from '@/stores/course.store'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()
const toast = useToast()

const loading = ref(true)
const question = ref<any>(null)
const selectedAnswer = ref('')
const textAnswer = ref('')
const submitted = ref(false)
const isCorrect = ref(false)
const expectedAnswer = ref('')

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })
const keys = ['A', 'B', 'C', 'D', 'E', 'F']

const parsedOptions = computed(() => {
  const opts = question.value?.options
  if (!opts) return null
  if (Array.isArray(opts)) return opts
  try { return JSON.parse(opts) } catch { return null }
})

const correctKey = computed(() => (question.value?.answer || '').trim().charAt(0).toUpperCase())
const canSubmit = computed(() => question.value?.type === 'choice' ? !!selectedAnswer.value : !!textAnswer.value.trim())

const typeLabel = (t: string) => ({ choice: '选择题', fill: '填空题', short: '简答题' }[t] || t)

const loadQuestion = async () => {
  const qid = route.params.questionId as string
  const courseId = courseStore.currentCourseId || (courseStore.courses[0]?.id ?? null)
  if (!courseId) { toast.error('未选择课程'); return }
  loading.value = true
  try {
    const res = await fetch(`/api/question/list/${courseId}`, { headers: authHeaders() })
    if (res.ok) {
      const all = await res.json()
      question.value = all.find((q: any) => String(q.id) === qid) || null
      if (!question.value) toast.error('题目不存在')
    }
  } catch { toast.error('加载失败') } finally { loading.value = false }
}

const submit = async () => {
  if (!question.value) return
  const answer = question.value.type === 'choice' ? selectedAnswer.value : textAnswer.value
  try {
    const res = await fetch('/api/practice/submit', {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ question_id: question.value.id, answer }),
    })
    if (res.ok) {
      const data = await res.json()
      isCorrect.value = data.correct
      expectedAnswer.value = data.expected
      submitted.value = true
      if (data.correct) toast.success('回答正确！')
    } else toast.error('提交失败')
  } catch { toast.error('网络错误') }
}

onMounted(async () => {
  if (courseStore.courses.length === 0) await courseStore.fetchCourses()
  await loadQuestion()
})
</script>

<style lang="scss" scoped>
.practice-question-page { padding: var(--space-6); max-width: 800px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); .header-left { display: flex; align-items: center; gap: var(--space-4); } h1 { font-size: var(--text-2xl); font-weight: var(--font-semibold); margin: 0; } }
.back-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-card); cursor: pointer; font-size: var(--text-sm); color: var(--text-secondary); transition: all 0.2s; &:hover { color: var(--text-primary); } }
.loading-state { text-align: center; padding: var(--space-16); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
.question-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-6); box-shadow: var(--shadow-sm); animation: fadeUp 0.4s ease-out both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.question-meta { display: flex; gap: var(--space-3); align-items: center; margin-bottom: var(--space-4); }
.type-badge { padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; &.type-choice { background: rgba(59,130,246,0.15); color: #2563EB; } &.type-fill { background: rgba(245,158,11,0.15); color: #D97706; } &.type-short { background: rgba(139,92,246,0.15); color: #7C3AED; } }
.difficulty { font-size: var(--text-xs); color: var(--text-secondary); }
.question-stem { font-size: var(--text-lg); line-height: 1.7; color: var(--text-primary); margin-bottom: var(--space-6); white-space: pre-wrap; }
.options-list { display: flex; flex-direction: column; gap: var(--space-3); margin-bottom: var(--space-6); }
.option-item { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3) var(--space-4); border: 1px solid var(--border); border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s; input { accent-color: rgb(var(--green)); } &:hover { border-color: rgb(var(--green)); background: rgba(var(--green),0.03); } &.selected { border-color: rgb(var(--green)); background: rgba(var(--green),0.05); } &.correct { border-color: #10B981; background: rgba(16,185,129,0.1); } &.wrong { border-color: #EF4444; background: rgba(239,68,68,0.1); } }
.option-key { width: 28px; height: 28px; border-radius: 50%; background: var(--bg-tertiary); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; flex-shrink: 0; }
.option-text { font-size: var(--text-sm); color: var(--text-primary); }
.correct-icon { color: #10B981; margin-left: auto; }
.wrong-icon { color: #EF4444; margin-left: auto; }
.text-answer { margin-bottom: var(--space-6); textarea { width: 100%; padding: var(--space-3) var(--space-4); border: 1px solid var(--border); border-radius: var(--radius-md); font-size: var(--text-sm); font-family: var(--font-sans); resize: vertical; background: var(--bg-card); color: var(--text-primary); &:focus { outline: none; border-color: rgb(var(--green)); box-shadow: 0 0 0 2px rgba(var(--green),0.1); } } }
.result-box { padding: var(--space-4); border-radius: var(--radius-md); margin-bottom: var(--space-6); animation: slideDown 0.3s ease-out; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }
.result-correct { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); }
.result-wrong { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); }
.result-header { display: flex; align-items: center; gap: var(--space-2); font-size: var(--text-base); font-weight: 600; i { font-size: 20px; } .result-correct & { color: #059669; } .result-wrong & { color: #DC2626; } }
.result-answer { font-size: var(--text-sm); color: var(--text-secondary); margin-top: var(--space-2); }
.actions { display: flex; justify-content: center; gap: var(--space-3); }
.btn-primary, .btn-secondary { padding: 10px 28px; border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: 500; cursor: pointer; border: none; transition: all 0.2s; }
.btn-primary { background: rgb(var(--green)); color: rgb(var(--paper)); &:hover { filter: brightness(1.05); box-shadow: 0 2px 8px rgba(var(--green),0.3); } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); }
</style>
