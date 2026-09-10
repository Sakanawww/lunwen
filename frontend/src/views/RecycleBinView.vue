<template>
  <div class="recycle-bin-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-delete-bin-2-line"></i> 回收站</h1>
        <p class="page-subtitle">查看和管理已删除的会话</p>
      </div>
    </div>

    <!-- 回收站列表 -->
    <div class="card">
      <div class="section-head">
        <h2 class="card-title"><i class="ri-history-line"></i> 已删除会话</h2>
        <div class="actions">
          <button class="btn btn-secondary" @click="batchRestore" :disabled="selectedIds.length === 0">
            <i class="ri-restore-line"></i>
            <span>批量恢复</span>
          </button>
          <button class="btn btn-danger" @click="batchDelete" :disabled="selectedIds.length === 0">
            <i class="ri-delete-bin-line"></i>
            <span>彻底删除</span>
          </button>
        </div>
      </div>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <div class="search-box">
          <i class="ri-search-line"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索会话标题..."
            class="search-input"
          />
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th class="th-checkbox">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th>会话标题</th>
              <th>课程</th>
              <th>删除时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="session in filteredSessions"
              :key="session.id"
            >
              <td>
                <input
                  type="checkbox"
                  :value="session.id"
                  v-model="selectedIds"
                />
              </td>
              <td>
                <div class="session-title">
                  <i class="ri-chat-1-line"></i>
                  <span>{{ session.title }}</span>
                </div>
              </td>
              <td class="td-mono">{{ session.course_name || '—' }}</td>
              <td class="td-mono">{{ formatDeletedAt(session.deleted_at) }}</td>
              <td>
                <div class="actions-cell">
                  <button
                    class="btn btn-sm btn-secondary"
                    @click="restoreSession(session.id)"
                    title="恢复"
                  >
                    <i class="ri-restore-line"></i>
                  </button>
                  <button
                    class="btn btn-sm btn-danger"
                    @click="deleteSession(session.id)"
                    title="彻底删除"
                  >
                    <i class="ri-delete-bin-line"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredSessions.length === 0">
              <td colspan="5" class="empty-state">
                <i class="ri-inbox-line"></i>
                <p>暂无已删除会话</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat.store'
import { useCourseStore } from '@/stores/course.store'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const courseStore = useCourseStore()

const { deletedSessions } = storeToRefs(chatStore)
const courses = computed(() => courseStore.courses)

const searchQuery = ref('')
const selectedIds = ref<number[]>([])

const filteredSessions = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return deletedSessions.value.filter(session =>
    session.title.toLowerCase().includes(query)
  )
})

const allSelected = computed(() => {
  return filteredSessions.value.length > 0 &&
    filteredSessions.value.every(s => selectedIds.value.includes(s.id))
})

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredSessions.value.map(s => s.id)
  }
}

const formatDeletedAt = (dateStr: string) => {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const restoreSession = async (sessionId: number) => {
  try {
    await chatStore.restoreSession(sessionId)
  } catch (error) {
    console.error('恢复失败:', error)
  }
}

const deleteSession = async (sessionId: number) => {
  if (!confirm('确定要彻底删除该会话吗？此操作不可恢复。')) return
  try {
    await chatStore.deleteSession(sessionId, true)
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const batchRestore = async () => {
  if (selectedIds.value.length === 0) return
  try {
    for (const id of selectedIds.value) {
      await chatStore.restoreSession(id)
    }
    selectedIds.value = []
  } catch (error) {
    console.error('批量恢复失败:', error)
  }
}

const batchDelete = async () => {
  if (selectedIds.value.length === 0) return
  if (!confirm(`确定要彻底删除 ${selectedIds.value.length} 个会话吗？此操作不可恢复。`)) return
  try {
    for (const id of selectedIds.value) {
      await chatStore.deleteSession(id, true)
    }
    selectedIds.value = []
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.recycle-bin-view {
  padding: var(--space-6);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-6);

  .page-title h1 {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);

    i {
      color: var(--danger);
    }
  }

  .page-subtitle {
    margin-top: var(--space-2);
    font-size: var(--text-base);
    color: var(--text-secondary);
  }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  gap: var(--space-3);

  .card-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);

    i {
      color: var(--accent);
    }
  }

  .actions {
    display: flex;
    gap: var(--space-2);
  }
}

.search-bar {
  margin-bottom: var(--space-4);

  .search-box {
    position: relative;
    max-width: 320px;

    .search-input {
      width: 100%;
      height: 40px;
      padding: 0 var(--space-4) 0 var(--space-9);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius-md);
      background: var(--bg-input);
      color: var(--text-primary);
      font-size: var(--text-sm);

      &:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: var(--shadow-glow);
      }
    }

    i {
      position: absolute;
      left: var(--space-3);
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: var(--text-base);
    }
  }
}

.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);

  th {
    background: var(--bg-table-head);
    color: var(--text-secondary);
    font-weight: var(--font-semibold);
    padding: var(--space-3) var(--space-4);
    text-align: left;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }

  tbody td {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);

    &:first-child {
      width: 40px;
      text-align: center;
    }
  }

  tbody tr:hover {
    background: var(--bg-hover);
  }

  .th-checkbox {
    width: 40px;
    text-align: center;
  }

  .session-title {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-weight: var(--font-medium);
    color: var(--text-primary);

    i {
      color: var(--accent);
    }
  }

  .td-mono {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  .actions-cell {
    display: flex;
    gap: var(--space-2);
  }

  .empty-state {
    text-align: center;
    padding: var(--space-10);
    color: var(--text-muted);

    i {
      font-size: 48px;
      color: var(--border-strong);
      display: block;
      margin-bottom: var(--space-3);
    }

    p {
      margin: 0;
      font-size: var(--text-base);
    }
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--t-fast);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.btn-sm {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
  }

  &.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-strong);

    &:hover:not(:disabled) {
      background: var(--bg-hover);
      border-color: var(--accent);
    }
  }

  &.btn-danger {
    background: var(--danger-soft);
    color: var(--danger);
    border: 1px solid var(--danger-border);

    &:hover:not(:disabled) {
      background: var(--danger);
      color: var(--primary-foreground);
    }
  }
}
</style>
