<template>
  <div class="logs-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-file-list-3-line"></i> 系统日志</h1>
        <p class="page-subtitle">查看系统操作日志和审计记录</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label for="userFilter"><i class="ri-user-line"></i> 用户</label>
        <select id="userFilter" v-model="filters.userId" @change="fetchLogs">
          <option value="">全部用户</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.real_name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label for="actionFilter"><i class="ri-function-line"></i> 操作类型</label>
        <select id="actionFilter" v-model="filters.action" @change="fetchLogs">
          <option value="">全部操作</option>
          <option v-for="action in actionOptions" :key="action.value" :value="action.value">
            {{ action.label }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label for="dateFrom"><i class="ri-time-line"></i> 时间范围</label>
        <div class="date-range">
          <input type="date" id="dateFrom" v-model="filters.dateFrom" @change="fetchLogs" />
          <span>至</span>
          <input type="date" id="dateTo" v-model="filters.dateTo" @change="fetchLogs" />
        </div>
      </div>
    </div>

    <!-- 日志表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>用户</th>
            <th>操作</th>
            <th>详情</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="fade-in">
            <td>
              <div class="time-cell">
                <span class="time-date">{{ formatDate(log.created_at) }}</span>
                <span class="time-clock">{{ formatTime(log.created_at) }}</span>
              </div>
            </td>
            <td>
              <div class="user-cell">
                <span class="user-avatar">{{ getInitials(log.user_name) }}</span>
                <span>{{ log.user_name || '系统' }}</span>
              </div>
            </td>
            <td>
              <span class="action-badge" :class="getActionClass(log.action)">
                {{ getActionLabel(log.action) }}
              </span>
            </td>
            <td class="detail-cell">{{ log.detail }}</td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="4" class="empty-state">
              <i class="ri-inbox-archive-line"></i>
              <p>暂无日志记录</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <div class="pagination-info">共 {{ total }} 条记录</div>
      <div class="pagination-controls">
        <button class="page-btn" @click="prevPage" :disabled="page <= 1">
          <i class="ri-arrow-left-s-line"></i>
        </button>
        <span class="page-indicator">第 {{ page }} / {{ totalPages }} 页</span>
        <button class="page-btn" @click="nextPage" :disabled="page >= totalPages">
          <i class="ri-arrow-right-s-line"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/utils/request'

interface Log {
  id: number
  user_id: number | null
  user_name: string | null
  action: string
  detail: string | null
  created_at: string
}

interface User {
  id: number
  real_name: string
}

const logs = ref<Log[]>([])
const users = ref<User[]>([])
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)

const filters = ref({
  userId: '',
  action: '',
  dateFrom: '',
  dateTo: '',
})

const actionOptions = [
  { value: 'LOGIN', label: '登录' },
  { value: 'LOGOUT', label: '退出' },
  { value: 'UPLOAD_KB', label: '上传知识库' },
  { value: 'CREATE_QUESTION', label: '创建试题' },
  { value: 'DELETE_QUESTION', label: '删除试题' },
  { value: 'GRADE_SUBMISSION', label: '批改作业' },
  { value: 'CHAT_MESSAGE', label: '答疑消息' },
  { value: 'CREATE_COURSE', label: '创建课程' },
  { value: 'ENROLL_STUDENT', label: '选课' },
]

const getActionLabel = (action: string) => {
  const option = actionOptions.find(o => o.value === action)
  return option?.label || action
}

const getActionClass = (action: string) => {
  const map: Record<string, string> = {
    'LOGIN': 'action-login',
    'LOGOUT': 'action-logout',
    'UPLOAD_KB': 'action-upload',
    'CREATE_QUESTION': 'action-create',
    'GRADE_SUBMISSION': 'action-grade',
  }
  return map[action] || ''
}

const formatDate = (iso: string) => {
  const date = new Date(iso)
  return date.toLocaleDateString('zh-CN')
}

const formatTime = (iso: string) => {
  const date = new Date(iso)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const getInitials = (name: string | null) => {
  if (!name) return '?'
  return name.charAt(0)
}

const fetchLogs = async () => {
  try {
    const params = new URLSearchParams({
      page: page.value.toString(),
      page_size: '20',
    })
    if (filters.value.userId) params.append('user_id', filters.value.userId)
    if (filters.value.action) params.append('action', filters.value.action)
    if (filters.value.dateFrom) params.append('start_date', filters.value.dateFrom)
    if (filters.value.dateTo) params.append('end_date', filters.value.dateTo)
    const data: any = await request.get(`/api/logs/operations?${params}`)
    const userNameMap = new Map<number, string>()
    for (const u of users.value) {
      userNameMap.set(u.id, u.real_name)
    }
    logs.value = (data.data || []).map((r: any) => ({
      ...r,
      user_name: r.user_id ? (userNameMap.get(r.user_id) || `用户${r.user_id}`) : null,
    }))
    total.value = data.total || 0
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch (error) {
    console.error('获取日志失败:', error)
  }
}

const fetchUsers = async () => {
  try {
    const data: any = await request.get('/api/accounts')
    const accounts = data.accounts || data || []
    users.value = Array.isArray(accounts) ? accounts : []
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const prevPage = () => {
  if (page.value > 1) {
    page.value--
    fetchLogs()
  }
}

const nextPage = () => {
  if (page.value < totalPages.value) {
    page.value++
    fetchLogs()
  }
}

onMounted(() => {
  fetchLogs()
  fetchUsers()
})
</script>

<style scoped>
.logs-page {
  padding: var(--space-6);
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-title h1 {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.page-title h1 i {
  color: var(--accent);
}

.page-subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: rgb(var(--card));
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.filter-group label {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.filter-group label i {
  font-size: 12px;
  color: var(--accent);
}

.filter-group select,
.filter-group input {
  height: 36px;
  padding: 0 var(--space-2);
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-family: var(--font-sans);
}

.date-range {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.date-range span {
  color: var(--text-muted);
}

/* 表格 */
.table-container {
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgb(var(--card));
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.data-table thead th {
  background: rgb(var(--background-tertiary));
  color: var(--text-secondary);
  font-weight: var(--font-medium);
  font-size: var(--text-xs);
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid rgb(var(--line));
  text-transform: uppercase;
  font-family: var(--font-mono);
  letter-spacing: var(--tracking-wide);
}

.data-table tbody td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid rgb(var(--line));
  color: var(--text-primary);
}

.data-table tbody tr:hover {
  background: rgba(var(--ink), 0.02);
}

.data-table tbody tr.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: none; }
}

.time-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-date {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.time-clock {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.user-avatar {
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

.action-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.action-login { background: rgba(91, 127, 255, 0.1); color: rgb(91, 127, 255); }
.action-logout { background: rgba(161, 161, 170, 0.1); color: rgb(161, 161, 170); }
.action-upload { background: rgba(16, 185, 129, 0.1); color: rgb(16, 185, 129); }
.action-create { background: rgba(139, 92, 246, 0.1); color: rgb(139, 92, 246); }
.action-grade { background: rgba(245, 158, 11, 0.1); color: rgb(245, 158, 11); }

.detail-cell {
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: var(--space-10);
  color: var(--text-muted);
}

.empty-state i {
  font-size: 48px;
  display: block;
  margin-bottom: var(--space-2);
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: var(--text-sm);
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: rgb(var(--card));
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  margin-top: var(--space-4);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.page-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  color: var(--text-secondary);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all var(--t-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: rgb(var(--ink));
  color: var(--text-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-indicator {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-group select,
  .filter-group input {
    width: 100%;
  }
  
  .date-range {
    flex-wrap: wrap;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .pagination {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style>
