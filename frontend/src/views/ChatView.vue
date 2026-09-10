<template>
  <div class="chat-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-message-3-line"></i> 智能答疑</h1>
        <p class="page-subtitle">与 AI 助教进行课程问答，获取即时帮助</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="newChat" title="新建对话">
          <i class="ri-add-line"></i>
          <span>新对话</span>
        </button>
        <button class="btn btn-secondary" @click="clearChat" title="清空对话">
          <i class="ri-delete-bin-line"></i>
          <span>清空</span>
        </button>
        <button class="btn btn-secondary" @click="exportChat" title="导出对话">
          <i class="ri-download-line"></i>
          <span>导出</span>
        </button>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-body">
      <!-- 历史会话侧栏 -->
      <aside v-if="sessions.length > 0" class="session-sidebar">
        <div class="session-sidebar-header">
          <span class="session-sidebar-title">历史记录</span>
        </div>
        <div class="session-list">
          <button
            v-for="s in sessions"
            :key="s.id"
            class="session-item"
            :class="{ active: s.id === currentSessionId }"
            :title="s.title"
            @click="selectSession(s.id)"
          >
            <i class="ri-chat-history-line session-item-icon"></i>
            <div class="session-item-body">
              <span class="session-item-title">{{ s.title }}</span>
              <span class="session-item-time">{{ s.created_at }}</span>
            </div>
            <i class="ri-close-line session-item-del" @click.stop="removeSession(s.id)" title="删除会话"></i>
          </button>
        </div>
      </aside>

      <!-- 消息列表 -->
      <div class="chat-container">
        <!-- 消息列表 -->
        <div ref="messagesContainer" class="messages-container">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="ri-customer-service-2-line"></i>
          </div>
          <p class="empty-text">开始提问吧，我会尽力帮助您</p>
          <div class="empty-hints">
            <span class="hint-tag">课程概念</span>
            <span class="hint-tag">知识点解析</span>
            <span class="hint-tag">作业帮助</span>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-avatar">
            <span v-if="message.role === 'user'">
              <i class="ri-user-line"></i>
            </span>
            <span v-else>
              <i class="ri-robot-line"></i>
            </span>
          </div>
          <div class="message-content">
            <div class="message-bubble">
              <p class="message-text">{{ message.content }}</p>
            </div>
            <!-- 溯源信息 -->
            <div v-if="message.sources && message.sources.length > 0" class="sources">
              <span class="sources-label"><i class="ri-link"></i> 参考来源:</span>
              <div class="sources-list">
                <span
                  v-for="(source, idx) in message.sources"
                  :key="idx"
                  class="source-tag"
                >
                  {{ source }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="message assistant loading">
          <div class="message-avatar">
            <i class="ri-robot-line"></i>
          </div>
          <div class="message-content">
            <div class="message-bubble loading">
              <span class="loading-dot"></span>
              <span class="loading-dot delay-1"></span>
              <span class="loading-dot delay-2"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-wrapper">
          <textarea
            ref="inputRef"
            v-model="inputMessage"
            class="chat-input"
            placeholder="请输入您的问题，按 Enter 发送..."
            :disabled="isLoading"
            @keydown.enter.exact.prevent="handleSend"
            @input="autoResize"
            rows="1"
          ></textarea>
          <button
            class="btn-send"
            :disabled="!inputMessage.trim() || isLoading"
            @click="handleSend"
          >
            <i class="ri-send-plane-fill"></i>
            <span>发送</span>
          </button>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useCourseStore } from '@/stores/course.store'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

interface SessionInfo {
  id: number
  title: string
  course_id: number | null
  created_at: string | null
}

const courseStore = useCourseStore()

// 状态
const messages = ref<Message[]>([])
const sessions = ref<SessionInfo[]>([])
const currentSessionId = ref<number | null>(null)
const loadingSessionId = ref<number | null>(null)
const isLoading = ref(false)
const isSessionLoading = ref(false)
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

// 调试模式
const DEBUG = true

const log = (...args: any[]) => {
  if (DEBUG) console.log('[Chat]', ...args)
}

// 自动调整输入框高度
const autoResize = () => {
  const el = inputRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 发送消息
const handleSend = async () => {
  const content = inputMessage.value.trim()
  if (!content || isLoading.value) return

  log('发送消息:', content)

  // 添加用户消息
  messages.value.push({ role: 'user', content })
  inputMessage.value = ''
  autoResize()
  await scrollToBottom()

  // 调用 API
  isLoading.value = true
  
  // 添加一个临时的助手消息用于显示流式响应
  const assistantMessage: Message = { role: 'assistant', content: '', sources: [] }
  messages.value.push(assistantMessage)
  
  try {
    // 确保课程已加载
    if (courseStore.courses.length === 0) {
      log('课程列表为空，正在加载...')
      await courseStore.fetchCourses()
      log('课程加载完成，数量:', courseStore.courses.length)
    }
    
    // 确保有选中的课程
    let finalCourseId = courseStore.currentCourseId
    if (!finalCourseId) {
      // 自动选择第一个课程
      if (courseStore.courses.length > 0) {
        finalCourseId = courseStore.courses[0].id
        courseStore.setActiveCourse(finalCourseId)
        log('自动选择课程:', finalCourseId)
      } else {
        throw new Error('请先选择课程')
      }
    }

    log('使用课程 ID:', finalCourseId)

    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      credentials: 'include',  // 携带 cookie
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',  // 后端能处理，虽然会触发预检但现代浏览器会重试
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
      },
      body: JSON.stringify({
        question: content,
        course_id: finalCourseId,
        // 已有会话则沿用，否则后端会自动创建新会话
        session_id: currentSessionId.value,
      }),
    })

    log('响应状态:', response.status)

    if (!response.ok) {
      log('响应失败，状态码:', response.status)
      let errorDetail = '请求失败'
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || errorDetail
        log('错误详情:', errorDetail)
      } catch (e) {
        log('无法解析错误响应')
      }
      throw new Error(errorDetail)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应流')
    }

    const decoder = new TextDecoder()
    let fullContent = ''
    let sources: string[] = []
    let tokenCount = 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            log('流式传输完成')
            break
          }

          try {
            const parsed = JSON.parse(data)
            
            // 处理元数据帧（包含完整内容和溯源）
            if (parsed.text !== undefined) {
              fullContent = parsed.text || fullContent
              sources = parsed.sources || []
              log('收到元数据，来源数量:', sources.length)
            }
            
            // 处理 token 流
            if (parsed.token) {
              fullContent += parsed.token
              tokenCount++
              if (tokenCount <= 5 || tokenCount % 20 === 0) {
                log(`Token ${tokenCount}:`, parsed.token)
              }
            }

            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg.role === 'assistant') {
              lastMsg.content = fullContent
              if (sources.length > 0) {
                lastMsg.sources = sources
              }
            }
            
            await scrollToBottom()
          } catch (e) {
            log('解析错误:', e)
          }
        }
      }
    }

    // 发送完成后刷新历史会话列表
    await fetchSessionList()
  } catch (error) {
    log('发送消息失败:', error)
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg.role === 'assistant') {
      const errorMsg = (error as Error).message
      log('错误详情:', errorMsg)
      lastMsg.content = '抱歉，处理您的请求时出现了问题：' + errorMsg + '，请稍后重试。'
    }
    isLoading.value = false
  } finally {
    // 确保加载状态被清除
    isLoading.value = false
    log('请求完成')
  }
}

// 清空对话
const clearChat = () => {
  if (confirm('确定要清空当前对话吗？')) {
    messages.value = []
  }
}

// 导出对话
const exportChat = () => {
  if (messages.value.length === 0) {
    alert('暂无对话内容可导出')
    return
  }

  const content = messages.value.map(m => {
    const role = m.role === 'user' ? '我' : 'AI 助教'
    return `[${role}]\n${m.content}${m.sources?.length ? `\n参考来源：${m.sources.join(', ')}` : ''}`
  }).join('\n\n---\n\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `对话记录_${new Date().toLocaleDateString()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// ========== 历史会话 ==========

const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
})

/** 拉取当前用户的历史会话列表 */
const fetchSessionList = async () => {
  try {
    const res = await fetch('/api/sessions', { method: 'GET', credentials: 'include', headers: authHeaders() })
    if (res.ok) {
      sessions.value = await res.json()
    }
  } catch (e) {
    log('加载历史会话失败:', e)
  }
}

/** 加载指定会话的所有消息 */
const loadMessages = async (sessionId: number) => {
  isSessionLoading.value = true
  loadingSessionId.value = sessionId
  try {
    const res = await fetch(`/api/sessions/${sessionId}/messages`, {
      method: 'GET',
      credentials: 'include',
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error(`加载消息失败 (${res.status})`)
    const data = await res.json()
    messages.value = data.map((m: any) => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content || '',
      sources: Array.isArray(m.sources) ? m.sources : (m.sources ? JSON.parse(m.sources) : []),
    }))
    await scrollToBottom()
  } catch (e) {
    log('加载消息失败:', e)
    alert('加载历史对话失败，请稍后重试')
  } finally {
    isSessionLoading.value = false
    loadingSessionId.value = null
  }
}

/** 新建对话（清空当前消息并取消会话绑定） */
const newChat = () => {
  if (messages.value.length > 0 && !confirm('确定要开始新对话吗？当前内容将被清空')) return
  currentSessionId.value = null
  messages.value = []
  inputMessage.value = ''
}

/** 切换历史会话 */
const selectSession = async (id: number) => {
  if (id === currentSessionId.value) return
  currentSessionId.value = id
  await loadMessages(id)
}

/** 删除历史会话（软删除） */
const removeSession = async (id: number) => {
  if (!confirm('确定要删除该历史会话吗？')) return
  try {
    await fetch(`/api/sessions/${id}?permanent=0`, {
      method: 'DELETE',
      credentials: 'include',
      headers: authHeaders(),
    })
    sessions.value = sessions.value.filter(s => s.id !== id)
    if (currentSessionId.value === id) {
      currentSessionId.value = null
      messages.value = []
    }
  } catch (e) {
    log('删除会话失败:', e)
    alert('删除会话失败，请稍后重试')
  }
}

onMounted(async () => {
  log('页面加载，初始化...')

  // 加载课程列表
  if (courseStore.courses.length === 0) {
    try {
      await courseStore.fetchCourses()
      log('课程加载完成，数量:', courseStore.courses.length)
    } catch (e) {
      log('加载课程失败:', e)
    }
  }

  // 确保有选中的课程
  if (!courseStore.currentCourseId && courseStore.courses.length > 0) {
    courseStore.setActiveCourse(courseStore.courses[0].id)
    log('自动选择课程:', courseStore.courses[0].id)
  }

  // 加载历史会话列表
  await fetchSessionList()

  log('当前课程 ID:', courseStore.currentCourseId)
  log('课程列表:', courseStore.courses.map(c => c.name))
})
</script>

<style lang="scss" scoped>
.chat-view {
  padding: var(--space-6);
  max-width: 900px;
  margin: 0 auto;
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

// 页面标题
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

  .header-actions {
    display: flex;
    gap: var(--space-2);
  }
}

// 聊天主体（侧栏 + 会话区）
.chat-body {
  flex: 1;
  display: flex;
  gap: var(--space-4);
  min-height: 0;
}

// 历史会话侧栏
.session-sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;

  .session-sidebar-header {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-muted);
  }

  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-2);
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .session-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    border: none;
    border-radius: var(--radius-md);
    background: transparent;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    transition: all 0.2s ease;

    &:hover {
      background: var(--bg-tertiary);
    }

    &.active {
      background: rgba(var(--green), 0.12);
      border: 1px solid rgb(var(--green));
    }

    .session-item-icon {
      color: var(--text-muted);
      font-size: var(--text-base);
    }

    .session-item-body {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;

      .session-item-title {
        font-size: var(--text-sm);
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .session-item-time {
        font-size: var(--text-xs);
        color: var(--text-muted);
      }
    }

    .session-item-del {
      display: none;
      color: var(--text-muted);
      font-size: var(--text-base);
      padding: var(--space-1);
      border-radius: var(--radius-sm);

      &:hover {
        color: var(--danger);
        background: var(--bg-tertiary);
      }
    }

    &:hover .session-item-del {
      display: inline-block;
    }
  }
}

// 聊天容器
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

// 消息列表
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);

  .empty-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: rgba(var(--green), 0.1);
    display: grid;
    place-items: center;
    font-size: 32px;
    color: rgb(var(--green));
    margin-bottom: var(--space-4);
  }

  .empty-text {
    font-size: var(--text-base);
    margin-bottom: var(--space-4);
  }

  .empty-hints {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
    justify-content: center;
  }

  .hint-tag {
    padding: var(--space-1) var(--space-3);
    background: var(--bg-tertiary);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    color: var(--text-secondary);
  }
}

// 消息样式
.message {
  display: flex;
  gap: var(--space-3);
  max-width: 80%;

  &.user {
    align-self: flex-end;
    flex-direction: row-reverse;
  }

  &.assistant {
    align-self: flex-start;
  }
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: grid;
  place-items: center;
  font-size: 18px;
  color: var(--text-secondary);

  .user & {
    background: linear-gradient(135deg, rgb(var(--green)), rgb(52, 211, 153));
    color: white;
  }

  .assistant & {
    background: linear-gradient(135deg, rgb(139, 92, 246), rgb(167, 139, 250));
    color: white;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.message-bubble {
  background: var(--bg-tertiary);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  
  .user & {
    background: rgb(var(--green));
    color: rgb(var(--paper));
    border-color: rgb(var(--green));
  }
}

.message-text {
  font-size: var(--text-base);
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0;
}

// 溯源信息
.sources {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  font-size: var(--text-xs);

  .sources-label {
    color: var(--text-muted);
    font-family: var(--font-mono);
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
  }

  .sources-list {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1);
  }

  .source-tag {
    display: inline-flex;
    align-items: center;
    padding: var(--space-1) var(--space-2);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    font-family: var(--font-mono);
    color: var(--text-secondary);
    transition: all 0.2s ease;

    &:hover {
      border-color: rgb(var(--green));
      color: var(--text-primary);
    }
  }
}

// 加载动画
.loading .message-bubble {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-3) var(--space-4);
}

.loading-dot {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: var(--radius-full);
  animation: bounce 1.4s infinite ease-in-out both;

  &.delay-1 {
    animation-delay: -0.32s;
  }

  &.delay-2 {
    animation-delay: -0.16s;
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

// 输入区域
.input-container {
  border-top: 1px solid var(--border);
  padding: var(--space-4);
  background: var(--bg-card);
}

.input-wrapper {
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: var(--space-3);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--text-primary);
  resize: none;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: rgb(var(--green));
    box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px rgba(var(--ink), 0.15);
  }

  &:disabled {
    background: var(--bg-tertiary);
    cursor: not-allowed;
  }
}

.btn-send {
  height: 44px;
  padding: 0 var(--space-5);
  background: rgb(var(--green));
  color: rgb(var(--paper));
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);

  i {
    font-size: var(--text-lg);
  }

  &:hover:not(:disabled) {
    background: rgb(25, 75, 55);
  }

  &:disabled {
    background: var(--bg-tertiary);
    color: var(--text-muted);
    cursor: not-allowed;
  }
}

// 按钮样式
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-primary);

  &:hover {
    background: var(--bg-tertiary);
    border-color: rgb(var(--green));
  }
}

// 滚动条样式
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(var(--ink), 0.2);
  border-radius: var(--radius-full);
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--ink), 0.3);
}
</style>
