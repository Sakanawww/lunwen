/**
 * useSSE - Server-Sent Events 组合式函数
 * 用于处理后端 SSE 流式响应（如 Agent 对话流）
 * 
 * @example
 * ```ts
 * const { connect, send, close, messages, isConnected } = useSSE('/api/chat/stream')
 * 
 * // 连接 SSE
 * await connect({ course_id: 1, session_id: 123 })
 * 
 * // 发送消息
 * await send({ message: '你好，请问...' })
 * 
 * // 监听消息
 * watch(messages, (newMessages) => {
 *   console.log('新消息:', newMessages)
 * })
 * 
 * // 关闭连接
 * close()
 * ```
 */

import { ref, computed, onUnmounted } from 'vue'

export interface SSEOptions {
  /** 自动重连 */
  reconnect?: boolean
  /** 重连间隔 (ms) */
  reconnectInterval?: number
  /** 最大重连次数 */
  maxReconnects?: number
  /** 连接超时 (ms) */
  timeout?: number
}

export interface SSEMessage {
  /** 消息 ID */
  id?: string
  /** 消息类型 */
  type: 'message' | 'error' | 'done' | 'connecting' | 'connected'
  /** 消息内容 */
  content?: string
  /** 额外数据 */
  data?: any
  /** 时间戳 */
  timestamp?: number
}

export function useSSE(url: string, options: SSEOptions = {}) {
  const {
    reconnect = true,
    reconnectInterval = 3000,
    maxReconnects = 5,
    timeout = 30000
  } = options

  // 状态
  const eventSource = ref<EventSource | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const isClosed = ref(false)
  const reconnectCount = ref(0)
  const messages = ref<SSEMessage[]>([])
  const error = ref<Error | null>(null)
  const reconnectTimer = ref<number | null>(null)
  const timeoutTimer = ref<number | null>(null)

  // 计算属性
  const hasError = computed(() => error.value !== null)
  const messageCount = computed(() => messages.value.length)

  // 添加消息
  const addMessage = (msg: SSEMessage) => {
    msg.timestamp = Date.now()
    messages.value.push(msg)
  }

  // 清除定时器
  const clearTimers = () => {
    if (reconnectTimer.value) {
      window.clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
    if (timeoutTimer.value) {
      window.clearTimeout(timeoutTimer.value)
      timeoutTimer.value = null
    }
  }

  // 关闭连接
  const close = () => {
    isClosed.value = true
    clearTimers()
    
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }
    
    isConnected.value = false
    isConnecting.value = false
  }

  // 重连逻辑
  const scheduleReconnect = () => {
    if (isClosed.value || !reconnect) return
    
    if (reconnectCount.value >= maxReconnects) {
      addMessage({
        type: 'error',
        content: `重连失败：已达到最大重连次数 (${maxReconnects})`,
        data: { reconnectCount: reconnectCount.value }
      })
      return
    }

    reconnectCount.value++
    isConnecting.value = true

    reconnectTimer.value = window.setTimeout(() => {
      connect()
    }, reconnectInterval)
  }

  // 连接 SSE
  const connect = (params?: Record<string, any>) => {
    if (eventSource.value) {
      console.warn('SSE: 已存在连接，请先关闭')
      return
    }

    isClosed.value = false
    isConnecting.value = true
    error.value = null

    // 构建 URL
    const targetUrl = new URL(url, window.location.origin)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          targetUrl.searchParams.set(key, String(value))
        }
      })
    }

    try {
      const es = new EventSource(targetUrl.toString())
      
      // 超时处理
      timeoutTimer.value = window.setTimeout(() => {
        if (isConnecting.value) {
          es.close()
          eventSource.value = null
          addMessage({
            type: 'error',
            content: '连接超时',
            data: { timeout }
          })
          scheduleReconnect()
        }
      }, timeout)

      // 连接打开
      es.onopen = () => {
        clearTimers()
        isConnected.value = true
        isConnecting.value = false
        reconnectCount.value = 0
        
        addMessage({
          type: 'connected',
          content: '已连接到服务器'
        })
      }

      // 接收消息
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          addMessage({
            type: 'message',
            content: data.content || data.message || event.data,
            data: data,
            id: data.id
          })
        } catch {
          addMessage({
            type: 'message',
            content: event.data
          })
        }
      }

      // 错误处理
      es.onerror = (err) => {
        clearTimers()
        isConnected.value = false
        isConnecting.value = false
        
        const errorMsg = err instanceof Error ? err.message : 'SSE 连接错误'
        error.value = new Error(errorMsg)
        
        addMessage({
          type: 'error',
          content: `连接错误：${errorMsg}`,
          data: { error: errorMsg }
        })

        es.close()
        eventSource.value = null
        
        // 尝试重连
        scheduleReconnect()
      }

      eventSource.value = es
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('未知错误')
      isConnecting.value = false
      
      addMessage({
        type: 'error',
        content: `连接失败：${error.value.message}`,
        data: { error: error.value }
      })
      
      scheduleReconnect()
    }
  }

  // 发送消息（通过单独的 POST 请求）
  const send = async (data: any, endpoint?: string) => {
    if (!isConnected.value) {
      throw new Error('SSE 未连接')
    }

    const targetEndpoint = endpoint || url
    
    try {
      const response = await fetch(targetEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '发送失败'
      addMessage({
        type: 'error',
        content: errorMsg,
        data: { error: err }
      })
      throw err
    }
  }

  // 清空消息
  const clearMessages = () => {
    messages.value = []
  }

  // 重置状态
  const reset = () => {
    close()
    messages.value = []
    error.value = null
    reconnectCount.value = 0
    isClosed.value = false
  }

  // 组件卸载时自动关闭
  onUnmounted(() => {
    close()
  })

  return {
    // 状态
    isConnected,
    isConnecting,
    isClosed,
    hasError,
    error,
    messages,
    messageCount,
    
    // 方法
    connect,
    send,
    close,
    clearMessages,
    reset,
    
    // 手动触发重连
    reconnect: () => {
      reconnectCount.value = 0
      scheduleReconnect()
    }
  }
}

export default useSSE
