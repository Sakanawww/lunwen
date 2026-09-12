/**
 * 聊天状态管理
 * 管理对话历史、消息列表和会话状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Message {
  id?: number
  role: 'user' | 'assistant' | 'system'
  content: string
  sources?: string[]
  created_at?: string
}

export interface ChatSession {
  id: number
  course_id: number
  course_name?: string
  title?: string
  created_at: string
  updated_at: string
  message_count: number
}

export const useChatStore = defineStore('chat', () => {
  // ========== 状态 ==========
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<number | null>(null)
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isSending = ref(false)
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========
  
  /** 当前会话 */
  const currentSession = computed(() => 
    sessions.value.find(s => s.id === currentSessionId.value) || null
  )

  /** 是否有消息 */
  const hasMessages = computed(() => messages.value.length > 0)

  /** 用户消息数量 */
  const userMessageCount = computed(() => 
    messages.value.filter(m => m.role === 'user').length
  )

  // ========== 方法 ==========

  /**
   * 获取会话列表
   */
  async function fetchSessions(courseId?: number) {
    isLoading.value = true
    error.value = null

    try {
      const url = courseId ? `/api/sessions?course_id=${courseId}` : '/api/sessions'
      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` },
      })
      if (!res.ok) throw new Error('加载会话列表失败')
      sessions.value = await res.json()
      return sessions.value
    } catch (err: any) {
      error.value = err.message || '加载会话列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载指定会话的消息
   */
  async function loadMessages(sessionId: number) {
    isLoading.value = true
    error.value = null

    try {
      const res = await fetch(`/api/sessions/${sessionId}/messages`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` },
      })
      if (!res.ok) throw new Error('加载消息失败')
      const data = await res.json()
      messages.value = (Array.isArray(data) ? data : []).map((m: any) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        sources: m.sources ? (typeof m.sources === 'string' ? JSON.parse(m.sources) : m.sources) : [],
        created_at: m.created_at,
      }))
      currentSessionId.value = sessionId
      return messages.value
    } catch (err: any) {
      error.value = err.message || '加载消息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 发送消息（SSE 流式由 ChatView 直接处理，此处为非流式兼容入口）
   */
  async function sendMessage(content: string, courseId?: number) {
    if (!content.trim()) return

    isSending.value = true
    error.value = null

    const userMessage: Message = {
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)

    try {
      const body = JSON.stringify({
        question: content.trim(),
        course_id: courseId,
        session_id: currentSessionId.value,
      })
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body,
      })
      if (!res.ok) throw new Error('发送消息失败')

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''
      let sources: string[] = []

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          const chunk = decoder.decode(value, { stream: true })
          for (const line of chunk.split('\n')) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') break
              try {
                const parsed = JSON.parse(data)
                if (parsed.session_id) currentSessionId.value = parsed.session_id
                if (parsed.token) fullContent += parsed.token
                if (parsed.text) fullContent = parsed.text
                if (parsed.sources) sources = parsed.sources
              } catch { /* skip */ }
            }
          }
        }
      }

      const aiMessage: Message = {
        role: 'assistant',
        content: fullContent,
        sources,
        created_at: new Date().toISOString()
      }
      messages.value.push(aiMessage)
      return aiMessage
    } catch (err: any) {
      error.value = err.message || '发送消息失败'
      messages.value.pop()
      throw err
    } finally {
      isSending.value = false
    }
  }

  /**
   * 清空当前会话
   */
  function clearMessages() {
    messages.value = []
  }

  /**
   * 删除会话（软删除进回收站；permanent=true 则彻底删除）
   */
  async function deleteSession(sessionId: number, permanent: boolean = false) {
    try {
      const res = await fetch(`/api/sessions/${sessionId}?permanent=${permanent ? 1 : 0}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })
      if (!res.ok) throw new Error('删除会话失败')

      sessions.value = sessions.value.filter(s => s.id !== sessionId)

      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
        messages.value = []
      }
      await refreshDeletedSessions()
    } catch (err: any) {
      error.value = err.message || '删除会话失败'
      throw err
    }
  }

  /**
   * 从回收站恢复会话
   */
  async function restoreSession(sessionId: number) {
    try {
      const res = await fetch(`/api/sessions/${sessionId}/restore`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })
      if (!res.ok) throw new Error('恢复会话失败')
      await refreshDeletedSessions()
    } catch (err: any) {
      error.value = err.message || '恢复会话失败'
      throw err
    }
  }

  /** 已删除会话列表（回收站） */
  const deletedSessions = ref<any[]>([])

  async function refreshDeletedSessions() {
    try {
      const res = await fetch('/api/sessions/deleted', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })
      if (!res.ok) return
      deletedSessions.value = await res.json()
    } catch (e) {
      console.error('加载回收站失败:', e)
    }
  }

  /**
   * 导出对话记录
   */
  function exportChat(_fmt: 'txt' | 'md' = 'txt'): string {
    if (messages.value.length === 0) {
      return ''
    }
    
    const lines = messages.value.map(m => {
      const role = m.role === 'user' ? '我' : 'AI 助教'
      const time = m.created_at ? new Date(m.created_at).toLocaleString('zh-CN') : ''
      let content = `[${role}] ${time}\n${m.content}`
      
      if (m.sources?.length) {
        content += `\n参考来源：${m.sources.join(', ')}`
      }
      
      return content
    })
    
    const header = `# 对话记录\n\n课程：${currentSession.value?.course_name || '未指定'}\n时间：${new Date().toLocaleString('zh-CN')}\n\n---\n\n`
    
    return header + lines.join('\n\n---\n\n')
  }

  return {
    // 状态
    sessions,
    currentSessionId,
    messages,
    isLoading,
    isSending,
    error,
    
    // 计算属性
    currentSession,
    hasMessages,
    userMessageCount,
    
    // 方法
    fetchSessions,
    loadMessages,
    sendMessage,
    clearMessages,
    deleteSession,
    restoreSession,
    deletedSessions,
    refreshDeletedSessions,
    exportChat,
  }
})
