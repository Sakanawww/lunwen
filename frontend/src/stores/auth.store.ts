/**
 * 用户认证状态管理
 * 管理用户登录状态、用户信息和权限
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
}

export interface RegisterData {
  username: string
  real_name: string
  password: string
  role: 'student' | 'teacher' | 'admin'
}

export const useAuthStore = defineStore('auth', () => {
  // ========== 状态 ==========
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========
  
  /** 用户是否已登录 */
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  /** 用户角色 */
  const userRole = computed(() => user.value?.role || null)

  /** 是否为管理员 */
  const isAdmin = computed(() => user.value?.role === 'admin')

  /** 是否为教师 */
  const isTeacher = computed(() => 
    user.value?.role === 'teacher' || user.value?.role === 'admin'
  )

  /** 是否为学生 */
  const isStudent = computed(() => user.value?.role === 'student')

  // ========== 方法 ==========

  /**
   * 初始化认证状态（从 Cookie/LocalStorage 恢复）
   */
  function initAuth() {
    // 尝试从 localStorage 恢复
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('token')
    
    if (storedUser && storedToken) {
      try {
        user.value = JSON.parse(storedUser)
        token.value = storedToken
      } catch (e) {
        clearAuth()
      }
    }
  }

  /**
   * 用户登录
   * @param credentials 登录凭证
   */
  async function login(credentials: LoginCredentials) {
    isLoading.value = true
    error.value = null
    
    try {
      // 使用相对路径，通过 Vite 代理转发到后端
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(credentials),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || '登录失败')
      }
      
      const data = await response.json()
      setAuth(data.token, data.user)
      return data
    } catch (err: any) {
      error.value = err.message || '登录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户注册
   * @param data 注册数据
   */
  async function register(data: RegisterData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || '注册失败')
      }

      return { success: true }
    } catch (err: any) {
      error.value = err.message || '注册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 登出
   */
  async function logout() {
    try {
      if (token.value) {
        await fetch('/auth/logout', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token.value}` },
        }).catch(() => {})
      }
      clearAuth()
      window.location.href = '/login'
    } catch (err) {
      console.error('登出失败:', err)
      clearAuth()
    }
  }

  /**
   * 刷新用户信息（返回本地缓存，后端无 /auth/me 端点）
   */
  async function refreshUser() {
    if (!token.value) return null
    return user.value
  }

  /**
   * 设置认证信息
   */
  function setAuth(newToken: string, newUser: User) {
    token.value = newToken
    user.value = newUser
    
    // 持久化
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  /**
   * 清除认证信息
   */
  function clearAuth() {
    user.value = null
    token.value = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  /**
   * 更新用户信息（用于个人资料编辑）
   */
  function updateUser(updates: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...updates }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  // ========== 初始化 ==========
  
  initAuth()

  return {
    // 状态
    user,
    token,
    isLoading,
    error,
    
    // 计算属性
    isAuthenticated,
    userRole,
    isAdmin,
    isTeacher,
    isStudent,
    
    // 方法
    login,
    register,
    logout,
    refreshUser,
    setAuth,
    clearAuth,
    updateUser,
  }
})
