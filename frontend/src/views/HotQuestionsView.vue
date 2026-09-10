<template>
  <div class="hot-questions-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-fire-line"></i> 热门问题</h1>
        <p class="page-subtitle">查看学生提问最多的问题排行</p>
      </div>
      <router-link to="/dashboard" class="btn btn-secondary">
        <i class="ri-arrow-left-line"></i>
        <span>返回看板</span>
      </router-link>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label><i class="ri-book-open-line"></i> 选择课程</label>
        <DropdownSelect
          v-model="selectedCourseId"
          :options="courseOptions"
          placeholder="选择课程…"
        />
      </div>
      <div class="filter-group">
        <label><i class="ri-time-line"></i> 时间范围</label>
        <DropdownSelect
          v-model="selectedTimeRange"
          :options="timeRangeOptions"
          placeholder="选择时间范围…"
        />
      </div>
    </div>

    <!-- 热门问题列表 -->
    <div class="questions-card">
      <div class="card-header">
        <div class="card-title">
          <i class="ri-fire-line"></i>
          热门问题 TOP 20
        </div>
        <button class="btn btn-primary btn-sm" @click="exportQuestions">
          <i class="ri-download-line"></i>
          导出报告
        </button>
      </div>

      <div class="question-list">
        <div
          v-for="(q, index) in filteredQuestions"
          :key="q.id"
          class="question-item"
          :class="'fade-in'"
          :style="{ animationDelay: `${index * 0.03}s` }"
        >
          <div class="question-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
          <div class="question-content">
            <div class="question-text">{{ q.text }}</div>
            <div class="question-meta">
              <span><i class="ri-user-line"></i> {{ q.studentCount }}人提问</span>
              <span><i class="ri-chat-1-line"></i> {{ q.replyCount }}条回复</span>
              <span class="question-trend" :class="q.trend > 0 ? 'up' : 'down'">
                <i :class="q.trend > 0 ? 'ri-arrow-up-line' : 'ri-arrow-down-line'"></i>
                {{ Math.abs(q.trend) }}%
              </span>
            </div>
          </div>
          <div class="question-tags">
            <span class="tag" :class="getCategoryTag(q.category)">{{ q.category }}</span>
          </div>
        </div>
        <div v-if="filteredQuestions.length === 0" class="empty-state">
          <i class="ri-inbox-line"></i>
          <p>暂无热门问题</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'

interface HotQuestion {
  id: number
  text: string
  studentCount: number
  replyCount: number
  trend: number
  category: string
}

const courseStore = useCourseStore()

const selectedCourseId = ref<number | null>(null)
const selectedTimeRange = ref<string>('30')

const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

const timeRangeOptions = [
  { value: '7', label: '最近 7 天' },
  { value: '30', label: '最近 30 天' },
  { value: '90', label: '最近 90 天' }
]

const allQuestions: HotQuestion[] = [
  { id: 1, text: '如何理解机器学习中的过拟合问题？', studentCount: 12, replyCount: 8, trend: 15, category: '机器学习' },
  { id: 2, text: 'Python 装饰器的使用场景有哪些？', studentCount: 9, replyCount: 5, trend: 8, category: 'Python' },
  { id: 3, text: '数据库索引的原理是什么？', studentCount: 7, replyCount: 4, trend: -3, category: '数据库' },
  { id: 4, text: '如何优化神经网络的训练速度？', studentCount: 6, replyCount: 6, trend: 22, category: '深度学习' },
  { id: 5, text: 'RESTful API 设计规范', studentCount: 5, replyCount: 3, trend: 5, category: '后端开发' },
  { id: 6, text: 'Git 分支管理策略', studentCount: 4, replyCount: 2, trend: -8, category: '工具' },
  { id: 7, text: 'Docker 容器化部署流程', studentCount: 4, replyCount: 3, trend: 12, category: 'DevOps' },
  { id: 8, text: 'Vue3 组合式 API 优势', studentCount: 3, replyCount: 2, trend: 0, category: '前端' },
  { id: 9, text: '什么是闭包？如何使用？', studentCount: 8, replyCount: 4, trend: 10, category: 'JavaScript' },
  { id: 10, text: 'HTTP 和 HTTPS 的区别', studentCount: 6, replyCount: 3, trend: 5, category: '网络' },
  { id: 11, text: '快速排序的实现原理', studentCount: 5, replyCount: 2, trend: -2, category: '算法' },
  { id: 12, text: 'React Hooks 使用注意事项', studentCount: 4, replyCount: 3, trend: 8, category: '前端' },
  { id: 13, text: 'MySQL 事务隔离级别', studentCount: 4, replyCount: 2, trend: 3, category: '数据库' },
  { id: 14, text: 'Linux 常用命令总结', studentCount: 3, replyCount: 1, trend: -5, category: '操作系统' },
  { id: 15, text: 'TCP 三次握手过程', studentCount: 3, replyCount: 2, trend: 0, category: '网络' },
  { id: 16, text: 'Webpack 打包优化策略', studentCount: 2, replyCount: 1, trend: 15, category: '前端' },
  { id: 17, text: 'Redis 缓存穿透解决方案', studentCount: 2, replyCount: 2, trend: 8, category: '数据库' },
  { id: 18, text: '微服务架构的优缺点', studentCount: 2, replyCount: 1, trend: -3, category: '架构' },
  { id: 19, text: 'JWT 认证原理', studentCount: 1, replyCount: 1, trend: 5, category: '安全' },
  { id: 20, text: 'GraphQL 与 REST 对比', studentCount: 1, replyCount: 0, trend: 2, category: 'API' }
]

const filteredQuestions = computed(() => {
  return allQuestions.slice(0, 20)
})

const getCategoryTag = (category: string) => {
  const map: Record<string, string> = {
    '机器学习': 'tag-ml',
    'Python': 'tag-py',
    '数据库': 'tag-db',
    '深度学习': 'tag-dl',
    '后端开发': 'tag-backend',
    '工具': 'tag-tool',
    'DevOps': 'tag-devops',
    '前端': 'tag-frontend',
    'JavaScript': 'tag-js',
    '网络': 'tag-net',
    '算法': 'tag-algo',
    '操作系统': 'tag-os',
    '架构': 'tag-arch',
    '安全': 'tag-security',
    'API': 'tag-api'
  }
  return map[category] || ''
}

const exportQuestions = () => {
  console.log('导出热门问题报告')
}

onMounted(() => {
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.activeCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.hot-questions-page {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
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
        color: rgb(239, 68, 68);
      }
    }

    .page-subtitle {
      font-size: var(--text-sm);
      color: var(--text-secondary);
      margin: var(--space-2) 0 0 0;
    }
  }
}

.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: var(--space-6);
  flex-wrap: wrap;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);

    label {
      font-size: var(--text-sm);
      font-weight: var(--font-medium);
      color: var(--text-primary);
      margin: 0;
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      min-height: 18px;

      i {
        color: rgb(var(--green));
      }
    }

    :deep(.dropdown-select) {
      min-width: 200px;
    }
  }
}

.questions-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border);

  .card-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--text-primary);

    i {
      color: rgb(239, 68, 68);
    }
  }
}

.question-list {
  padding: var(--space-3);
  max-height: 600px;
  overflow-y: auto;
}

.question-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-2);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  animation: fadeUp 0.4s ease-out both;

  &:hover {
    background: var(--bg-tertiary);
  }

  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }
}

.question-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  background: var(--bg-tertiary);
  color: var(--text-secondary);

  &.rank-1 {
    background: linear-gradient(135deg, rgb(251, 191, 36), rgb(245, 158, 11));
    color: white;
  }

  &.rank-2 {
    background: linear-gradient(135deg, rgb(102, 112, 133), rgb(148, 163, 184));
    color: white;
  }

  &.rank-3 {
    background: linear-gradient(135deg, rgb(234, 179, 8), rgb(202, 138, 4));
    color: white;
  }
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-text {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.question-meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
  display: flex;
  gap: var(--space-3);

  span {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
  }
}

.question-trend {
  display: inline-flex;
  align-items: center;
  gap: var(--space-0);
  font-size: 11px;
  font-weight: var(--font-medium);

  &.up {
    color: rgb(16, 185, 129);
  }

  &.down {
    color: rgb(239, 68, 68);
  }
}

.question-tags {
  flex-shrink: 0;
}

.tag {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.tag-ml { background: rgba(139, 92, 246, 0.1); color: rgb(124, 58, 237); }
  &.tag-py { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
  &.tag-db { background: rgba(245, 158, 11, 0.1); color: rgb(184, 106, 0); }
  &.tag-dl { background: rgba(139, 92, 246, 0.1); color: rgb(124, 58, 237); }
  &.tag-backend { background: rgba(6, 182, 212, 0.1); color: rgb(6, 182, 212); }
  &.tag-tool { background: rgba(102, 112, 133, 0.1); color: rgb(102, 112, 133); }
  &.tag-devops { background: rgba(239, 68, 68, 0.1); color: rgb(239, 68, 68); }
  &.tag-frontend { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
  &.tag-js { background: rgba(245, 158, 11, 0.1); color: rgb(184, 106, 0); }
  &.tag-net { background: rgba(16, 185, 129, 0.1); color: rgb(6, 118, 71); }
  &.tag-algo { background: rgba(139, 92, 246, 0.1); color: rgb(124, 58, 237); }
  &.tag-os { background: rgba(102, 112, 133, 0.1); color: rgb(102, 112, 133); }
  &.tag-arch { background: rgba(6, 182, 212, 0.1); color: rgb(6, 182, 212); }
  &.tag-security { background: rgba(239, 68, 68, 0.1); color: rgb(239, 68, 68); }
  &.tag-api { background: rgba(59, 130, 246, 0.1); color: rgb(37, 99, 235); }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
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
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);

    &:hover {
      background: var(--bg-tertiary);
    }
  }
}

.empty-state {
  text-align: center;
  padding: var(--space-10) 0;
  color: var(--text-muted);

  i {
    font-size: 32px;
    display: block;
    margin-bottom: var(--space-2);
  }

  p {
    margin: 0;
    font-size: var(--text-sm);
  }
}
</style>
