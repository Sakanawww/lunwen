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
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>课程名称</th>
              <th>课程代码</th>
              <th>学分</th>
              <th>学期</th>
              <th>状态</th>
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
              <td class="td-mono">{{ course.code }}</td>
              <td>{{ course.credits }}</td>
              <td>{{ course.semester }}</td>
              <td>
                <span class="status-badge" :class="course.status === 'active' ? 'status-active' : 'status-ended'">
                  {{ course.status === 'active' ? '进行中' : '已结束' }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-primary btn-sm"
                  @click="selectCourse(course.id)"
                >
                  <i class="ri-checkbox-circle-line"></i> 选择
                </button>
              </td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="6" class="empty-state">
                <i class="ri-book-line"></i>
                <p>暂无课程</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCourseStore } from '@/stores/course.store'
import { useAuthStore } from '@/stores/auth.store'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const courses = computed(() => courseStore.courses)

const selectCourse = (courseId: number) => {
  courseStore.setCurrentCourse(courseId)
  // 根据角色跳转到不同页面
  const role = user.value?.role
  if (role === 'student') {
    window.location.href = '/chat'
  } else {
    window.location.href = '/dashboard'
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
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);

  .card-title {
    margin: 0;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);

    .doc-count {
      font-size: var(--text-sm);
      color: var(--text-muted);
    }
  }
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
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &.td-mono {
      font-family: var(--font-mono);
    }
  }

  tbody tr:hover {
    background: var(--bg-tertiary);
  }
}

.course-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);

  i {
    color: rgb(var(--green));
  }
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.status-active {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.status-ended {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
  }
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

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
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
</style>
