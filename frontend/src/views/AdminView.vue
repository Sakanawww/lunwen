<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title font-serif">系统管理</h1>
      <p class="page-subtitle">管理系统配置、用户权限与系统日志</p>
    </div>

    <!-- 管理选项卡 -->
    <div class="tabs-container">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- 系统概览 -->
    <div v-show="activeTab === 'overview'" class="tab-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalTeachers }}</div>
            <div class="stat-label">教师数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalStudents }}</div>
            <div class="stat-label">学生数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCourses }}</div>
            <div class="stat-label">课程数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalQuestions }}</div>
            <div class="stat-label">试题数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDocuments }}</div>
            <div class="stat-label">文档数</div>
          </div>
        </div>
      </div>

      <!-- 系统状态 -->
      <div class="card">
        <h2 class="card-title"><i class="ri-server-line"></i> 系统状态</h2>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">API 服务</span>
            <span class="status-badge success">运行中</span>
          </div>
          <div class="status-item">
            <span class="status-label">数据库</span>
            <span class="status-badge success">正常</span>
          </div>
          <div class="status-item">
            <span class="status-label">Redis 缓存</span>
            <span class="status-badge success">正常</span>
          </div>
          <div class="status-item">
            <span class="status-label">向量数据库</span>
            <span class="status-badge success">正常</span>
          </div>
          <div class="status-item">
            <span class="status-label">LLM 服务</span>
            <span class="status-badge success">正常</span>
          </div>
          <div class="status-item">
            <span class="status-label">磁盘使用</span>
            <span class="status-badge warning">65%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户管理 -->
    <div v-show="activeTab === 'users'" class="tab-content">
      <div class="card">
        <div class="section-head">
          <h2 class="card-title"><i class="ri-user-settings-line"></i> 用户管理</h2>
          <button class="btn btn-primary" @click="showUserModal = true">
            <i class="ri-add-line"></i> 添加用户
          </button>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>真实姓名</th>
                <th>角色</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td class="td-mono">{{ user.id }}</td>
                <td>
                  <div class="user-cell">
                    <div class="avatar">{{ user.real_name[0] }}</div>
                    <span>{{ user.username }}</span>
                  </div>
                </td>
                <td>{{ user.real_name }}</td>
                <td>
                  <span class="role-badge" :class="user.role">
                    {{ roleLabels[user.role] }}
                  </span>
                </td>
                <td>
                  <span class="status-badge success">正常</span>
                </td>
                <td class="td-mono">{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="actions">
                    <button class="btn btn-ghost btn-sm" @click="editUser(user)" title="编辑">
                      <i class="ri-edit-line"></i>
                    </button>
                    <button class="btn btn-ghost btn-sm" @click="deleteUser(user)" title="删除">
                      <i class="ri-delete-bin-line"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 系统配置 -->
    <div v-show="activeTab === 'settings'" class="tab-content">
      <div class="settings-grid">
        <div class="card">
          <h2 class="card-title"><i class="ri-brain-line"></i> LLM 配置</h2>
          <form @submit.prevent="saveLLMSettings" class="settings-form">
            <div class="form-group">
              <label for="llm-provider">模型提供商</label>
              <select id="llm-provider" v-model="llmSettings.provider" class="form-select">
                <option value="qwen">Qwen (通义千问)</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
              </select>
            </div>

            <div class="form-group">
              <label for="llm-model">模型名称</label>
              <input
                id="llm-model"
                v-model="llmSettings.model"
                type="text"
                class="form-input"
                placeholder="例如：qwen-plus"
              />
            </div>

            <div class="form-group">
              <label for="llm-api-key">API Key</label>
              <input
                id="llm-api-key"
                v-model="llmSettings.apiKey"
                type="password"
                class="form-input"
                placeholder="sk-..."
              />
            </div>

            <div class="form-group">
              <label for="llm-base-url">API Base URL</label>
              <input
                id="llm-base-url"
                v-model="llmSettings.baseUrl"
                type="text"
                class="form-input"
                placeholder="https://dashscope.aliyuncs.com/compatible-mode/v1"
              />
            </div>

            <div class="form-group">
              <label for="llm-temperature">Temperature</label>
              <input
                id="llm-temperature"
                v-model.number="llmSettings.temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                class="form-input"
              />
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary">
                <i class="ri-save-3-line"></i> 保存配置
              </button>
            </div>
          </form>
        </div>

        <div class="card">
          <h2 class="card-title"><i class="ri-settings-3-line"></i> 系统设置</h2>
          <form @submit.prevent="saveSystemSettings" class="settings-form">
            <div class="form-group">
              <label for="max-file-size">最大上传文件大小 (MB)</label>
              <input
                id="max-file-size"
                v-model.number="systemSettings.maxFileSize"
                type="number"
                min="1"
                max="100"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="chunk-size">文档分块大小</label>
              <input
                id="chunk-size"
                v-model.number="systemSettings.chunkSize"
                type="number"
                min="100"
                max="2000"
                step="100"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="chunk-overlap">分块重叠</label>
              <input
                id="chunk-overlap"
                v-model.number="systemSettings.chunkOverlap"
                type="number"
                min="0"
                max="500"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="session-timeout">会话超时 (分钟)</label>
              <input
                id="session-timeout"
                v-model.number="systemSettings.sessionTimeout"
                type="number"
                min="5"
                max="1440"
                class="form-input"
              />
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary">
                <i class="ri-save-3-line"></i> 保存设置
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 系统日志 -->
    <div v-show="activeTab === 'logs'" class="tab-content">
      <div class="card">
        <div class="section-head">
          <h2 class="card-title"><i class="ri-file-list-3-line"></i> 系统日志</h2>
          <div class="filters">
            <select v-model="logFilter.level" class="form-select form-select-sm">
              <option value="">全部级别</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
            </select>
            <button class="btn btn-secondary btn-sm" @click="loadLogs">
              <i class="ri-refresh-line"></i> 刷新
            </button>
          </div>
        </div>

        <div class="log-container">
          <div
            v-for="log in filteredLogs"
            :key="log.id"
            class="log-entry"
            :class="log.level.toLowerCase()"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-level" :class="log.level.toLowerCase()">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户编辑弹窗 -->
    <div v-if="showUserModal" class="modal-backdrop" @click.self="showUserModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '添加用户' }}</h3>
          <button class="btn-close" @click="showUserModal = false">
            <i class="ri-close-line"></i>
          </button>
        </div>

        <form @submit.prevent="saveUser" class="modal-body">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="userForm.username"
              type="text"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label for="real_name">真实姓名</label>
            <input
              id="real_name"
              v-model="userForm.real_name"
              type="text"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">密码 {{ editingUser ? '(留空则不修改)' : '' }}</label>
            <input
              id="password"
              v-model="userForm.password"
              type="password"
              class="form-input"
              :required="!editingUser"
            />
          </div>

            <div class="form-group">
              <label for="role">角色</label>
              <select id="role" v-model="userForm.role" class="form-select">
                <option value="student">学生</option>
                <option value="teacher">教师</option>
                <option value="admin">管理员</option>
              </select>
            </div>
          </form>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showUserModal = false">
            取消
          </button>
          <button type="submit" form="userForm" class="btn btn-primary" @click="saveUser">
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/utils/request'

interface User {
  id: number
  username: string
  real_name: string
  role: 'student' | 'teacher' | 'admin'
  created_at: string
}

interface LogEntry {
  id: number
  timestamp: string
  level: 'INFO' | 'WARNING' | 'ERROR'
  message: string
}

const roleLabels: Record<string, string> = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

const tabs = [
  { id: 'overview', label: '系统概览', icon: 'ri-dashboard-line' },
  { id: 'users', label: '用户管理', icon: 'ri-user-settings-line' },
  { id: 'settings', label: '系统配置', icon: 'ri-settings-3-line' },
  { id: 'logs', label: '系统日志', icon: 'ri-file-list-3-line' }
]

const activeTab = ref('overview')

// 系统统计
const stats = ref({
  totalUsers: 0,
  totalTeachers: 0,
  totalStudents: 0,
  totalCourses: 0,
  totalQuestions: 0,
  totalDocuments: 0
})

// 用户列表
const users = ref<User[]>([])
const showUserModal = ref(false)
const editingUser = ref<User | null>(null)
const userForm = ref({
  username: '',
  real_name: '',
  password: '',
  role: 'student' as 'student' | 'teacher' | 'admin',
})

// LLM 配置
const llmSettings = ref({
  provider: 'qwen',
  model: 'qwen-plus',
  apiKey: '',
  baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  temperature: 0.7
})

// 系统配置
const systemSettings = ref({
  maxFileSize: 50,
  chunkSize: 500,
  chunkOverlap: 50,
  sessionTimeout: 120
})

// 日志
const logs = ref<LogEntry[]>([])
const logFilter = ref({
  level: ''
})

const filteredLogs = computed(() => {
  if (!logFilter.value.level) return logs.value
  return logs.value.filter(log => log.level === logFilter.value.level)
})

// 方法
const loadStats = async () => {
  try {
    const data: any = await api.get('/api/accounts')
    const accounts = data.accounts || data || []
    const users = Array.isArray(accounts) ? accounts : []
    stats.value.totalUsers = users.length
    stats.value.totalTeachers = users.filter((u: any) => u.role === 'teacher').length
    stats.value.totalStudents = users.filter((u: any) => u.role === 'student').length
    try {
      const courses: any = await api.get('/api/courses')
      const c = Array.isArray(courses) ? courses : (courses.courses || [])
      stats.value.totalCourses = c.length
      // 遍历所有课程累计文档和试题数（替代原先硬编码 course_id=1）
      let totalDocs = 0
      let totalQs = 0
      for (const course of c) {
        try {
          const docs: any = await api.get(`/api/kb/docs/${course.id}`)
          totalDocs += (Array.isArray(docs) ? docs : []).length
        } catch { /* 课程可能无文档 */ }
        try {
          const q: any = await api.get(`/api/question/list/${course.id}`)
          totalQs += (Array.isArray(q) ? q.length : 0)
        } catch { /* 课程可能无试题 */ }
      }
      stats.value.totalDocuments = totalDocs
      stats.value.totalQuestions = totalQs
    } catch { stats.value.totalCourses = 0 }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadUsers = async () => {
  try {
    const data: any = await api.get('/api/accounts')
    const accounts = data.accounts || data || []
    users.value = (Array.isArray(accounts) ? accounts : []).map((u: any) => ({
      id: u.id,
      username: u.username,
      real_name: u.real_name,
      role: u.role,
      created_at: u.created_at || '',
    }))
  } catch (error) {
    console.error('加载用户列表失败:', error)
    users.value = []
  }
}

const loadLogs = async () => {
  try {
    const data: any = await api.get('/api/logs/operations', { params: { page: 1, page_size: 50 } })
    const items = data.data || []
    logs.value = items.map((r: any) => ({
      id: r.id,
      timestamp: r.created_at || '',
      level: r.status === 'error' ? 'ERROR' : 'INFO',
      message: `${r.action}${r.detail ? '：' + r.detail : ''}`,
    }))
  } catch (error) {
    console.error('加载日志失败:', error)
    logs.value = []
  }
}

const editUser = (user: User) => {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    real_name: user.real_name,
    password: '',
    role: user.role,
  }
  showUserModal.value = true
}

const deleteUser = async (user: User) => {
  if (!confirm(`确定要删除用户「${user.real_name}」吗？此操作不可恢复。`)) return
  try {
    await api.delete(`/api/accounts/${user.id}`)
    await loadUsers()
    await loadStats()
  } catch (error) {
    console.error('删除用户失败:', error)
    alert('删除失败，可能权限不足或不能删除自己')
  }
}

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await api.put(`/api/accounts/${editingUser.value.id}`, {
        real_name: userForm.value.real_name,
        role: userForm.value.role,
        ...(userForm.value.password ? { password: userForm.value.password } : {}),
      })
    } else {
      await api.post('/api/accounts', {
        username: userForm.value.username,
        password: userForm.value.password,
        real_name: userForm.value.real_name,
        role: userForm.value.role,
      })
    }
    showUserModal.value = false
    editingUser.value = null
    await loadUsers()
    await loadStats()
  } catch (error) {
    console.error('保存用户失败:', error)
    alert('保存失败，请检查权限或网络')
  }
}

const saveLLMSettings = async () => {
  alert('LLM 配置请通过 .env 环境变量修改，修改后重启服务生效')
}

const saveSystemSettings = async () => {
  alert('系统配置请通过 .env 环境变量修改，修改后重启服务生效')
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleTimeString('zh-CN', { hour12: false })
}

onMounted(() => {
  loadStats()
  loadUsers()
  loadLogs()
})
</script>

<style lang="scss" scoped>
.admin-page {
  padding: var(--space-6);
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-6);

  .page-title {
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .page-subtitle {
    font-size: var(--text-base);
    color: var(--text-secondary);
    margin: var(--space-2) 0 0 0;
  }
}

.tabs-container {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  border-bottom: 1px solid var(--border);
  padding-bottom: var(--space-2);
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  &.active {
    background: rgb(var(--green));
    color: rgb(var(--paper));
  }
}

.tab-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(var(--space-1)); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.stat-info {
  .stat-value {
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    font-family: var(--font-mono);
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
  margin-bottom: var(--space-6);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0 0 var(--space-4) 0;

  i {
    color: rgb(var(--green));
  }
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.status-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.success {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.warning {
    background: rgba(245, 158, 11, 0.1);
    color: rgb(184, 106, 0);
  }

  &.inactive {
    background: var(--bg-tertiary);
    color: var(--text-muted);
  }
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

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);

  .avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: var(--radius-full);
    background: rgb(var(--green));
    color: rgb(var(--paper));
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
  }
}

.role-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);

  &.admin {
    background: rgba(139, 92, 246, 0.1);
    color: rgb(124, 58, 237);
  }

  &.teacher {
    background: rgba(59, 130, 246, 0.1);
    color: rgb(37, 99, 235);
  }

  &.student {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }
}

.actions {
  display: flex;
  gap: var(--space-1);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-6);
}

.settings-form {
  .form-group {
    margin-bottom: var(--space-4);

    label {
      display: block;
      font-size: var(--text-sm);
      font-weight: var(--font-medium);
      color: var(--text-primary);
      margin-bottom: var(--space-2);
    }

    .form-input,
    .form-select {
      width: 100%;
      height: 40px;
      padding: 0 var(--space-3);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: var(--bg-card);
      font-size: var(--text-base);
      font-family: var(--font-sans);
      color: var(--text-primary);
      transition: all 0.2s ease;

      &:focus {
        outline: none;
        border-color: rgb(var(--green));
        box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.15);
      }
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      font-size: var(--text-sm);
      color: var(--text-primary);
      cursor: pointer;

      input[type="checkbox"] {
        width: 16px;
        height: 16px;
        cursor: pointer;
      }
    }
  }

  .form-actions {
    margin-top: var(--space-6);
  }
}

.form-select-sm {
  height: 32px;
  padding: 0 var(--space-2);
  font-size: var(--text-xs);
}

.filters {
  display: flex;
  gap: var(--space-2);
}

.log-container {
  max-height: 500px;
  overflow-y: auto;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

.log-entry {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border);

  .log-time {
    color: var(--text-muted);
    white-space: nowrap;
  }

  .log-level {
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);

    &.info {
      background: rgba(59, 130, 246, 0.1);
      color: rgb(37, 99, 235);
    }

    &.warning {
      background: rgba(245, 158, 11, 0.1);
      color: rgb(184, 106, 0);
    }

    &.error {
      background: rgba(239, 68, 68, 0.1);
      color: rgb(185, 28, 28);
    }
  }

  .log-message {
    flex: 1;
    color: var(--text-secondary);
  }
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.modal {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border);

  h3 {
    font-size: var(--text-lg);
    font-weight: var(--font-medium);
    color: var(--text-primary);
    margin: 0;
  }

  .btn-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }
  }
}

.modal-body {
  padding: var(--space-5);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border);
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

  &.btn-ghost {
    background: transparent;
    color: var(--text-secondary);

    &:hover {
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }
  }
}
</style>
