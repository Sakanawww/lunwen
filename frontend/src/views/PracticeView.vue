<template>
  <div class="practice-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-book-open-line"></i> 答题练习</h1>
        <p class="page-subtitle">选择课程进行在线练习，巩固所学知识</p>
      </div>
    </div>

    <!-- 课程选择 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-book-3-line"></i> 选择课程</h2>
      </div>
      <div class="course-selector">
        <DropdownSelect
          v-model="selectedCourseId"
          :options="courseOptions"
          placeholder="选择课程…"
          @update:modelValue="onCourseChange"
        />
      </div>
    </div>

    <!-- 题目列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-stack-line"></i> 试题列表</h2>
        <span class="doc-count">共 {{ questions.length }} 题</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>题型</th>
              <th>题干</th>
              <th class="num">难度</th>
              <th class="num">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questions" :key="q.id">
              <td class="td-mono">{{ q.id }}</td>
              <td>
                <span class="q-type">
                  <i class="ri-question-line"></i>
                  {{ typeLabels[q.type] || q.type }}
                </span>
              </td>
              <td class="stem-cell">{{ q.stem }}</td>
              <td class="num">
                <span class="difficulty-badge" :class="`diff-${q.difficulty}`">
                  {{ q.difficulty }}
                </span>
              </td>
              <td class="num">
                <button class="btn btn-primary btn-sm" @click="startPractice(q)">
                  <i class="ri-pencil-line"></i> 练习
                </button>
              </td>
            </tr>
            <tr v-if="questions.length === 0">
              <td colspan="5" class="empty-state">
                <i class="ri-book-read-line"></i>
                <p>暂无试题</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 练习弹窗 -->
    <div
      v-if="showPracticeModal"
      class="modal-mask"
      @click.self="closePractice"
    >
      <div class="modal-box modal-large" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3>{{ currentQuestion?.type === 'choice' ? '选择题' : currentQuestion?.type === 'fill' ? '填空题' : '简答题' }}</h3>
          <button type="button" class="modal-x" @click="closePractice">
            <i class="ri-close-line"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="question-stem">
            <span class="difficulty-badge" :class="`diff-${currentQuestion?.difficulty}`">
              难度：{{ currentQuestion?.difficulty }}
            </span>
            <p>{{ currentQuestion?.stem }}</p>
          </div>

          <!-- 选择题选项 -->
          <div v-if="currentQuestion?.type === 'choice' && currentQuestion?.options" class="options-list">
            <div
              v-for="(option, key) in currentQuestion.options"
              :key="key"
              class="option-item"
              :class="{ selected: userAnswer === key }"
              @click="selectOption(key)"
            >
              <span class="option-label">{{ key }}.</span>
              <span class="option-text">{{ option }}</span>
            </div>
          </div>

          <!-- 填空题/简答题输入 -->
          <div v-else class="answer-input-wrap">
            <textarea
              v-model="userAnswer"
              class="answer-textarea"
              placeholder="请输入您的答案..."
              rows="6"
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closePractice">
            <i class="ri-close-line"></i> 取消
          </button>
          <button type="button" class="btn btn-primary" @click="submitAnswer" :disabled="!userAnswer || isSubmitting">
            <i v-if="isSubmitting" class="ri-loader-4-line spin"></i>
            <i v-else class="ri-check-line"></i>
            {{ isSubmitting ? '提交中…' : '提交答案' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 结果弹窗 -->
    <div
      v-if="showResultModal"
      class="modal-mask"
      @click.self="closeResult"
    >
      <div class="modal-box" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3>练习结果</h3>
          <button type="button" class="modal-x" @click="closeResult">
            <i class="ri-close-line"></i>
          </button>
        </div>

        <div class="result-content">
          <div class="result-icon" :class="isCorrect ? 'correct' : 'incorrect'">
            <i :class="isCorrect ? 'ri-checkbox-circle-fill' : 'ri-close-circle-fill'"></i>
          </div>
          <div class="result-text">
            <p class="result-title">{{ isCorrect ? '回答正确！' : '回答错误' }}</p>
            <p class="result-hint" v-if="!isCorrect">正确答案：{{ correctAnswer }}</p>
          </div>
        </div>

        <div v-if="explanation" class="explanation">
          <h4><i class="ri-lightbulb-flash-line"></i> 解析</h4>
          <p>{{ explanation }}</p>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-primary" @click="closeResult">
            <i class="ri-check-line"></i> 确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'

interface Question {
  id: number
  type: 'choice' | 'fill' | 'short'
  stem: string
  options?: Record<string, string>
  answer: string
  difficulty: number
  explanation?: string
}

const courseStore = useCourseStore()

// 状态
const selectedCourseId = ref<number | null>(null)
const showPracticeModal = ref(false)
const showResultModal = ref(false)
const currentQuestion = ref<Question | null>(null)
const userAnswer = ref<string>('')
const isSubmitting = ref(false)
const isCorrect = ref(false)
const correctAnswer = ref('')
const explanation = ref('')

// 试题列表
const questions = ref<Question[]>([])

// 题型标签映射
const typeLabels: Record<string, string> = {
  choice: '选择题',
  fill: '填空题',
  short: '简答题'
}

// 选项
const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

// 方法
const onCourseChange = (courseId: number) => {
  courseStore.setActiveCourse(courseId)
  loadQuestions()
}

const loadQuestions = async () => {
  // TODO: 调用 API 加载试题
  questions.value = [
    {
      id: 1,
      type: 'choice',
      stem: '以下哪个排序算法的平均时间复杂度为 O(nlogn)？',
      options: {
        A: '冒泡排序',
        B: '快速排序',
        C: '插入排序',
        D: '选择排序'
      },
      answer: 'B',
      difficulty: 2,
      explanation: '快速排序采用分治策略，平均时间复杂度为 O(nlogn)。冒泡排序、插入排序和选择排序的平均时间复杂度均为 O(n²)。'
    },
    {
      id: 2,
      type: 'fill',
      stem: '在二叉树遍历中，____ 遍历的顺序是：左子树 → 根节点 → 右子树。',
      answer: '中序',
      difficulty: 2,
      explanation: '中序遍历的顺序是：先遍历左子树，然后访问根节点，最后遍历右子树。'
    },
    {
      id: 3,
      type: 'short',
      stem: '请简述机器学习中过拟合的概念。',
      answer: '过拟合是指模型在训练集上表现很好，但在测试集或新数据上表现较差的现象。',
      difficulty: 3,
      explanation: '过拟合通常发生在模型过于复杂或训练数据不足时，模型记住了训练数据的噪声而非学习一般规律。'
    }
  ]
}

const startPractice = (question: Question) => {
  currentQuestion.value = question
  userAnswer.value = ''
  showPracticeModal.value = true
}

const selectOption = (key: string) => {
  userAnswer.value = key
}

const submitAnswer = async () => {
  if (!currentQuestion.value || !userAnswer.value) return

  isSubmitting.value = true

  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 判断答案是否正确
    const correct = currentQuestion.value.answer.toUpperCase() === userAnswer.value.toUpperCase()
    isCorrect.value = correct
    correctAnswer.value = currentQuestion.value.answer
    explanation.value = currentQuestion.value.explanation || ''
    
    showPracticeModal.value = false
    showResultModal.value = true
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    isSubmitting.value = false
  }
}

const closePractice = () => {
  showPracticeModal.value = false
  currentQuestion.value = null
  userAnswer.value = ''
}

const closeResult = () => {
  showResultModal.value = false
  currentQuestion.value = null
  userAnswer.value = ''
}

onMounted(() => {
  loadQuestions()
  
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.activeCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.practice-page {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-6);

  .page-title {
    h1 {
      font-size: var(--text-2xl);
      font-weight: var(--font-semibold);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: var(--space-2);
      margin: 0;

      i {
        color: rgb(var(--green));
      }
    }

    .page-subtitle {
      font-size: var(--text-sm);
      color: var(--text-secondary);
      margin: var(--space-2) 0 0 0;
    }
  }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;

  i {
    color: rgb(var(--green));
  }
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);

  .doc-count {
    font-size: var(--text-sm);
    color: var(--text-muted);
  }
}

.course-selector {
  max-width: 300px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);

  thead th {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: var(--font-semibold);
    font-size: var(--text-xs);
    padding: var(--space-3) var(--space-4);
    text-align: left;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;

    &.num {
      text-align: right;
    }
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &.td-mono {
      font-family: var(--font-mono);
      white-space: nowrap;
    }

    &.stem-cell {
      max-width: 400px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    &.num {
      text-align: right;
    }
  }

  tbody tr:hover {
    background: var(--bg-tertiary);
  }
}

.q-type {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  background: rgba(6, 182, 212, 0.1);
  color: rgb(6, 182, 212);
  border-radius: var(--radius-full);

  i {
    margin-right: 2px;
  }
}

.difficulty-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 var(--space-1);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  font-family: var(--font-mono);

  &.diff-1 { background: rgba(16, 185, 129, 0.15); color: rgb(6, 118, 71); }
  &.diff-2 { background: rgba(59, 130, 246, 0.15); color: rgb(37, 99, 235); }
  &.diff-3 { background: rgba(245, 158, 11, 0.15); color: rgb(184, 106, 0); }
  &.diff-4 { background: rgba(239, 68, 68, 0.15); color: rgb(185, 28, 28); }
  &.diff-5 { background: rgba(139, 92, 246, 0.15); color: rgb(124, 58, 237); }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;

  &.btn-sm {
    height: 32px;
    padding: 0 var(--space-3);
    font-size: var(--text-xs);
  }

  &.btn-primary {
    background: rgb(var(--green));
    color: rgb(var(--paper));
    border: none;
    box-shadow: 0 2px 0 rgba(var(--ink), 0.2);

    &:hover:not(:disabled) {
      background: rgb(25, 75, 55);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);

    &:hover {
      background: var(--bg-tertiary);
      border-color: rgb(var(--green));
    }
  }
}

.empty-state {
  text-align: center;
  padding: var(--space-10) 0;
  color: var(--text-muted);

  i {
    font-size: 34px;
    display: block;
    margin-bottom: var(--space-2);
  }

  p {
    margin: 0;
    font-size: var(--text-sm);
  }
}

// 弹窗
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
}

.modal-box {
  width: 100%;
  max-width: 520px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.25);
  padding: var(--space-5);

  &.modal-large {
    max-width: 720px;
  }
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);

  h3 {
    margin: 0;
    font-size: var(--text-lg);
    color: var(--text-primary);
  }
}

.modal-x {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  line-height: 1;

  &:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
  }
}

.modal-body {
  margin-bottom: var(--space-4);
}

.question-stem {
  position: relative;
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);

  .difficulty-badge {
    position: absolute;
    top: var(--space-2);
    right: var(--space-2);
  }

  p {
    font-size: var(--text-base);
    color: var(--text-primary);
    line-height: 1.6;
    margin: var(--space-3) 0 0 0;
  }
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.option-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: rgb(var(--green));
    background: rgba(var(--green), 0.05);
  }

  &.selected {
    background: rgba(var(--green), 0.1);
    border-color: rgb(var(--green));
  }
}

.option-label {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  min-width: 24px;
}

.option-text {
  flex: 1;
  font-size: var(--text-base);
  color: var(--text-primary);
}

.answer-input-wrap {
  margin-top: var(--space-4);
}

.answer-textarea {
  width: 100%;
  min-height: 120px;
  padding: var(--space-3);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--text-primary);
  resize: vertical;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: rgb(var(--green));
    box-shadow: 0 0 0 3px rgba(var(--green), 0.1);
  }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

// 结果弹窗
.result-content {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.result-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 32px;
  flex-shrink: 0;

  &.correct {
    background: rgba(16, 185, 129, 0.15);
    color: rgb(6, 118, 71);
  }

  &.incorrect {
    background: rgba(239, 68, 68, 0.15);
    color: rgb(185, 28, 28);
  }
}

.result-text {
  flex: 1;

  .result-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0 0 var(--space-1) 0;
  }

  .result-hint {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    margin: 0;
  }
}

.explanation {
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);

  h4 {
    font-size: var(--text-base);
    font-weight: var(--font-medium);
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin: 0 0 var(--space-2) 0;

    i {
      color: rgb(245, 158, 11);
    }
  }

  p {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
  }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.td-mono {
  font-family: var(--font-mono);
}
</style>
