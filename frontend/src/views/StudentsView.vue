<template>
  <div class="students-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-group-line"></i> 学生名单</h1>
        <p class="page-subtitle">查看课程选课学生详情与学习数据</p>
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
        <label><i class="ri-search-line"></i> 搜索学生</label>
        <input
          v-model="searchQuery"
          type="text"
          class="form-input"
          placeholder="输入姓名或学号…"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ students.length }}</div>
        <div class="stat-label">总人数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ activeStudents }}</div>
        <div class="stat-label">活跃学生</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ pendingStudents }}</div>
        <div class="stat-label">待完成作业</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ avgScore }}</div>
        <div class="stat-label">平均分</div>
      </div>
    </div>

    <!-- 学生列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-team-line"></i> 学生列表</h2>
        <div class="actions">
          <span class="doc-count">共 {{ students.length }} 人</span>
          <button class="btn btn-primary btn-sm" @click="exportStudents">
            <i class="ri-download-line"></i>
            导出名单
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>邮箱</th>
              <th>作业提交</th>
              <th>平均分</th>
              <th>活跃度</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id">
              <td class="td-mono">{{ student.studentNo }}</td>
              <td>
                <div class="student-name">
                  <div class="avatar">{{ student.name.charAt(0) }}</div>
                  <span>{{ student.name }}</span>
                </div>
              </td>
              <td class="td-mono">{{ student.email }}</td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: student.submissionRate + '%' }"></div>
                  </div>
                  <span class="progress-text">{{ student.submissionCount }}/{{ totalAssignments }}</span>
                </div>
              </td>
              <td>
                <span class="score-badge" :class="getScoreClass(student.avgScore)">
                  {{ student.avgScore }}
                </span>
              </td>
              <td>
                <span class="activity-badge" :class="getActivityClass(student.activity)">
                  <i class="ri-fire-line"></i>
                  {{ student.activity }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="student.status === 'active' ? 'status-active' : 'status-inactive'">
                  {{ student.status === 'active' ? '正常' : '未激活' }}
                </span>
              </td>
              <td>
                <button class="btn btn-secondary btn-sm" @click="viewDetail(student)">
                  <i class="ri-eye-line"></i>
                  详情
                </button>
              </td>
            </tr>
            <tr v-if="filteredStudents.length === 0">
              <td colspan="8" class="empty-state">
                <i class="ri-inbox-line"></i>
                <p>暂无学生数据</p>
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
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'

interface Student {
  id: number
  studentNo: string
  name: string
  email: string
  submissionCount: number
  submissionRate: number
  avgScore: number
  activity: number
  status: 'active' | 'inactive'
}

const courseStore = useCourseStore()

const selectedCourseId = ref<number | null>(null)
const searchQuery = ref('')

// 不同课程的学生数据
const courseStudentsMap: Record<number, Student[]> = {
  1: [ // 计算机科学基础
    { id: 1, studentNo: '2021001', name: '张三', email: 'zhangsan@example.com', submissionCount: 8, submissionRate: 100, avgScore: 92, activity: 95, status: 'active' },
    { id: 2, studentNo: '2021002', name: '李四', email: 'lisi@example.com', submissionCount: 7, submissionRate: 88, avgScore: 85, activity: 78, status: 'active' },
    { id: 3, studentNo: '2021003', name: '王五', email: 'wangwu@example.com', submissionCount: 6, submissionRate: 75, avgScore: 78, activity: 65, status: 'active' },
    { id: 4, studentNo: '2021004', name: '赵六', email: 'zhaoliu@example.com', submissionCount: 8, submissionRate: 100, avgScore: 88, activity: 82, status: 'active' },
    { id: 5, studentNo: '2021005', name: '钱七', email: 'qianqi@example.com', submissionCount: 5, submissionRate: 63, avgScore: 72, activity: 45, status: 'inactive' },
    { id: 6, studentNo: '2021006', name: '孙八', email: 'sunba@example.com', submissionCount: 7, submissionRate: 88, avgScore: 90, activity: 88, status: 'active' },
    { id: 7, studentNo: '2021007', name: '周九', email: 'zhoujiu@example.com', submissionCount: 8, submissionRate: 100, avgScore: 95, activity: 92, status: 'active' },
    { id: 8, studentNo: '2021008', name: '吴十', email: 'wushi@example.com', submissionCount: 4, submissionRate: 50, avgScore: 65, activity: 35, status: 'inactive' },
  ],
  2: [ // 数据结构与算法
    { id: 1, studentNo: '2021009', name: '郑一', email: 'zhengyi@example.com', submissionCount: 7, submissionRate: 88, avgScore: 89, activity: 85, status: 'active' },
    { id: 2, studentNo: '2021010', name: '冯二', email: 'fenger@example.com', submissionCount: 6, submissionRate: 75, avgScore: 82, activity: 70, status: 'active' },
    { id: 3, studentNo: '2021011', name: '陈三', email: 'chensan@example.com', submissionCount: 8, submissionRate: 100, avgScore: 94, activity: 90, status: 'active' },
    { id: 4, studentNo: '2021012', name: '褚四', email: 'chusi@example.com', submissionCount: 5, submissionRate: 63, avgScore: 75, activity: 55, status: 'inactive' },
    { id: 5, studentNo: '2021013', name: '卫五', email: 'weiwu@example.com', submissionCount: 7, submissionRate: 88, avgScore: 87, activity: 80, status: 'active' },
    { id: 6, studentNo: '2021014', name: '蒋六', email: 'jiangliu@example.com', submissionCount: 8, submissionRate: 100, avgScore: 91, activity: 88, status: 'active' },
  ],
  3: [ // 数据库原理
    { id: 1, studentNo: '2021015', name: '沈七', email: 'shenqi@example.com', submissionCount: 6, submissionRate: 75, avgScore: 80, activity: 68, status: 'active' },
    { id: 2, studentNo: '2021016', name: '韩八', email: 'hanba@example.com', submissionCount: 7, submissionRate: 88, avgScore: 86, activity: 75, status: 'active' },
    { id: 3, studentNo: '2021017', name: '杨九', email: 'yangjiu@example.com', submissionCount: 8, submissionRate: 100, avgScore: 93, activity: 92, status: 'active' },
    { id: 4, studentNo: '2021018', name: '朱十', email: 'zhushi@example.com', submissionCount: 4, submissionRate: 50, avgScore: 68, activity: 40, status: 'inactive' },
    { id: 5, studentNo: '2021019', name: '秦十一', email: 'qinshi@example.com', submissionCount: 7, submissionRate: 88, avgScore: 84, activity: 78, status: 'active' },
  ],
  4: [ // 机器学习基础
    { id: 1, studentNo: '2021020', name: '尤十二', email: 'youshier@example.com', submissionCount: 8, submissionRate: 100, avgScore: 96, activity: 95, status: 'active' },
    { id: 2, studentNo: '2021021', name: '许十三', email: 'xushisan@example.com', submissionCount: 7, submissionRate: 88, avgScore: 88, activity: 82, status: 'active' },
    { id: 3, studentNo: '2021022', name: '何十四', email: 'heshisi@example.com', submissionCount: 8, submissionRate: 100, avgScore: 92, activity: 90, status: 'active' },
    { id: 4, studentNo: '2021023', name: '吕十五', email: 'lvshiwu@example.com', submissionCount: 6, submissionRate: 75, avgScore: 79, activity: 65, status: 'active' },
    { id: 5, studentNo: '2021024', name: '施十六', email: 'shishiliu@example.com', submissionCount: 5, submissionRate: 63, avgScore: 70, activity: 48, status: 'inactive' },
    { id: 6, studentNo: '2021025', name: '张十七', email: 'zhangshiqi@example.com', submissionCount: 8, submissionRate: 100, avgScore: 94, activity: 93, status: 'active' },
  ],
}

const totalAssignments = 8

const students = computed(() => {
  return courseStudentsMap[selectedCourseId.value || 1] || courseStudentsMap[1]
})

const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(s => 
    s.name.toLowerCase().includes(query) || 
    s.studentNo.toLowerCase().includes(query)
  )
})

const activeStudents = computed(() => {
  return students.value.filter(s => s.activity >= 60).length
})

const pendingStudents = computed(() => {
  return students.value.filter(s => s.submissionCount < totalAssignments).length
})

const avgScore = computed(() => {
  if (students.value.length === 0) return '0'
  const sum = students.value.reduce((acc, s) => acc + s.avgScore, 0)
  return (sum / students.value.length).toFixed(1)
})

const getScoreClass = (score: number) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

const getActivityClass = (activity: number) => {
  if (activity >= 80) return 'activity-high'
  if (activity >= 50) return 'activity-medium'
  return 'activity-low'
}

const exportStudents = () => {
  const headers = ['学号', '姓名', '邮箱', '作业提交', '平均分', '活跃度', '状态']
  const rows = students.value.map(s => [
    s.studentNo,
    s.name,
    s.email,
    `${s.submissionCount}/${totalAssignments}`,
    s.avgScore,
    s.activity,
    s.status === 'active' ? '正常' : '未激活'
  ])
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `学生名单_${new Date().toLocaleDateString('zh-CN')}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const viewDetail = (student: Student) => {
  alert(`查看学生详情：${student.name}\n学号：${student.studentNo}\n邮箱：${student.email}`)
}

onMounted(() => {
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.activeCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.students-page {
  padding: var(--space-6);
  max-width: 1400px;
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

      i {
        color: rgb(var(--green));
      }
    }

    .form-input {
      height: 40px;
      padding: 0 var(--space-3);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: var(--bg-card);
      font-size: var(--text-sm);
      font-family: var(--font-sans);
      color: var(--text-primary);
      min-width: 220px;

      &:focus {
        outline: none;
        border-color: rgb(var(--green));
        box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.1);
      }
    }
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);

  .stat-value {
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
  }

  .stat-label {
    font-size: var(--text-sm);
    color: var(--text-secondary);
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

.student-name {
  display: flex;
  align-items: center;
  gap: var(--space-2);

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgb(var(--green));
    color: rgb(var(--paper));
    display: grid;
    place-items: center;
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
  }
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);

  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-full);
    overflow: hidden;
    min-width: 80px;

    .progress-fill {
      height: 100%;
      background: rgb(var(--green));
      border-radius: var(--radius-full);
      transition: width 0.3s ease;
    }
  }

  .progress-text {
    font-size: var(--text-xs);
    color: var(--text-secondary);
    font-family: var(--font-mono);
    white-space: nowrap;
  }
}

.score-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  font-family: var(--font-mono);

  &.score-excellent {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.score-good {
    background: rgba(59, 130, 246, 0.1);
    color: rgb(37, 99, 235);
  }

  &.score-pass {
    background: rgba(245, 158, 11, 0.1);
    color: rgb(184, 106, 0);
  }

  &.score-fail {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(185, 28, 28);
  }
}

.activity-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  i {
    font-size: 12px;
  }

  &.activity-high {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.activity-medium {
    background: rgba(245, 158, 11, 0.1);
    color: rgb(184, 106, 0);
  }

  &.activity-low {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(185, 28, 28);
  }
}

.status-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.status-active {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.status-inactive {
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
