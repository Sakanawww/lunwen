/**
 * 聊天状态管理
 * 管理对话历史、消息列表和会话状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/request'

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
      // TODO: 调用 API
      // const params = courseId ? { course_id: courseId } : {}
      // const data = await api.get<ChatSession[]>('/api/chat/sessions', { params })
      
      // 模拟数据
      await new Promise(resolve => setTimeout(resolve, 500))
      
      sessions.value = [
        { 
          id: 1, 
          course_id: 1, 
          course_name: '计算机科学基础',
          title: '关于递归的疑问', 
          created_at: '2026-09-08T10:00:00Z',
          updated_at: '2026-09-08T10:30:00Z',
          message_count: 12 
        },
        { 
          id: 2, 
          course_id: 1, 
          course_name: '计算机科学基础',
          title: '排序算法讨论', 
          created_at: '2026-09-07T14:00:00Z',
          updated_at: '2026-09-07T14:45:00Z',
          message_count: 8 
        }
      ]
      
      return sessions.value
    } catch (err: any) {
      error.value = err.message || '加载会话列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建新会话
   */
  async function createSession(courseId: number, title?: string) {
    try {
      // TODO: 调用 API
      // const data = await api.post<ChatSession>('/api/chat/sessions', { course_id: courseId, title })
      
      // 模拟创建
      const newSession: ChatSession = {
        id: Date.now(),
        course_id: courseId,
        course_name: '新课程',
        title: title || '新对话',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0
      }
      
      sessions.value.unshift(newSession)
      currentSessionId.value = newSession.id
      
      return newSession
    } catch (err: any) {
      error.value = err.message || '创建会话失败'
      throw err
    }
  }

  /**
   * 加载指定会话的消息
   */
  async function loadMessages(sessionId: number) {
    isLoading.value = true
    error.value = null
    
    try {
      // TODO: 调用 API
      // const data = await api.get<Message[]>(`/api/chat/sessions/${sessionId}/messages`)
      
      // 模拟加载
      await new Promise(resolve => setTimeout(resolve, 500))
      
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
   * 发送消息
   * @param content 消息内容
   * @param courseId 课程 ID（用于 RAG 检索）
   */
  async function sendMessage(content: string, courseId?: number) {
    if (!content.trim()) return
    
    isSending.value = true
    error.value = null
    
    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)
    
    try {
      // TODO: 调用 API 发送消息并获取回复
      // const response = await api.post<Message>('/api/chat/messages', {
      //   session_id: currentSessionId.value,
      //   content,
      //   course_id: courseId
      // })
      
      // 模拟 AI 回复
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const aiMessage: Message = {
        role: 'assistant',
        content: generateMockResponse(content),
        sources: ['课程讲义 Chapter ' + Math.floor(Math.random() * 5 + 1)],
        created_at: new Date().toISOString()
      }
      
      messages.value.push(aiMessage)
      
      // 更新会话
      if (currentSessionId.value) {
        const session = sessions.value.find(s => s.id === currentSessionId.value)
        if (session) {
          session.message_count++
          session.updated_at = new Date().toISOString()
        }
      }
      
      return aiMessage
    } catch (err: any) {
      error.value = err.message || '发送消息失败'
      
      // 移除失败的用户消息
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
   * 生成模拟回复（用于开发/测试）
   */
  function generateMockResponse(question: string): string {
    const responses = [
      `这是一个很好的问题！关于"${question}"，让我来详细解释一下：\n\n**核心概念**：\n这是理解该知识点的基础，需要掌握以下几个关键点...\n\n**应用场景**：\n在实际开发中，这个概念经常用于...\n\n**注意事项**：\n需要特别关注以下细节...\n\n如果您还有疑问，欢迎继续提问！`,
      `感谢提问！让我为您解答"${question}"：\n\n1. **定义**：这是首先要明确的概念\n2. **原理**：理解其工作机制\n3. **示例**：通过具体例子加深理解\n\n希望这个解释对您有帮助！`,
      `关于"${question}"，我从课程资料中找到以下信息：\n\n根据课程讲义，这个知识点主要涉及...\n\n**重点总结**：\n- 关键点 1\n- 关键点 2\n- 关键点 3\n\n建议您参考相关章节进行复习。`
    ]
    
    return responses[Math.floor(Math.random() * responses.length)]
  }

  /**
   * 导出对话记录
   */
  function exportChat(format: 'txt' | 'md' = 'txt'): string {
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
    createSession,
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
