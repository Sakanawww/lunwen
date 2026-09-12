/**
 * 课程状态管理
 * 管理用户可选的课程列表和当前激活课程
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Course } from '@/types'
import { api } from '@/utils/request'

export interface CourseWithTeacher extends Course {
  teacher_name?: string
  student_count?: number
}

export const useCourseStore = defineStore('course', () => {
  // ========== 状态 ==========
  const courses = ref<CourseWithTeacher[]>([])
  const currentCourseId = ref<number | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========
  
  /** 当前激活的课程 */
  const currentCourse = computed(() => 
    courses.value.find(c => c.id === currentCourseId.value) || null
  )

  /** 是否有可选课程 */
  const hasCourses = computed(() => courses.value.length > 0)

  // ========== 方法 ==========

  /**
   * 获取用户可选的课程列表
   * 支持教师/管理员/学生不同角色
   */
  async function fetchCourses() {
    isLoading.value = true
    error.value = null
    
    try {
      // 使用相对路径，通过 Vite 代理转发到后端
      const response = await fetch('/api/courses', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })
      
      if (!response.ok) {
        if (response.status === 401) {
          // 未授权，清除认证并跳转登录
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          throw new Error('未授权，请重新登录')
        }
        const err = await response.json().catch(() => ({ detail: '加载失败' }))
        throw new Error(err.detail || '加载课程失败')
      }
      
      const data = await response.json()
      courses.value = data
      
      // 自动选择第一个课程
      if (data.length > 0 && currentCourseId.value === null) {
        currentCourseId.value = data[0].id
        persistCurrentCourse()
      }
      
      return data
    } catch (err: any) {
      error.value = err.message || '加载课程失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 设置当前激活的课程
   * @param courseId 课程 ID
   */
  function setActiveCourse(courseId: number) {
    currentCourseId.value = courseId
    persistCurrentCourse()
  }

  /**
   * 清除当前课程选择
   */
  function clearCurrentCourse() {
    currentCourseId.value = null
    localStorage.removeItem('currentCourseId')
  }

  /**
   * 从本地存储恢复课程选择
   */
  function restoreCurrentCourse() {
    const saved = localStorage.getItem('currentCourseId')
    if (saved) {
      const id = Number(saved)
      // 验证课程是否存在
      const exists = courses.value.some(c => c.id === id)
      if (exists) {
        currentCourseId.value = id
      }
    }
  }

  /**
   * 清除认证信息（用于 401 错误）
   */
  function clearAuth() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // 触发重新登录
    window.location.href = '/login'
  }

  /**
   * 持久化当前课程选择
   */
  function persistCurrentCourse() {
    if (currentCourseId.value !== null) {
      localStorage.setItem('currentCourseId', String(currentCourseId.value))
    }
  }

  /**
   * 添加课程到列表（用于实时更新）
   */
  function addCourse(course: CourseWithTeacher) {
    if (!courses.value.some(c => c.id === course.id)) {
      courses.value.push(course)
    }
  }

  /**
   * 从列表中移除课程
   */
  function removeCourse(courseId: number) {
    courses.value = courses.value.filter(c => c.id !== courseId)
    
    // 如果移除的是当前课程，清除选择
    if (currentCourseId.value === courseId) {
      currentCourseId.value = null
      localStorage.removeItem('currentCourseId')
    }
  }

  /**
   * 更新课程信息
   */
  function updateCourse(courseId: number, updates: Partial<CourseWithTeacher>) {
    const index = courses.value.findIndex(c => c.id === courseId)
    if (index !== -1) {
      courses.value[index] = { ...courses.value[index], ...updates }
    }
  }

  // ========== 初始化 ==========
  
  // 恢复本地存储的课程选择
  restoreCurrentCourse()

  return {
    // 状态
    courses,
    currentCourseId,
    isLoading,
    error,
    
    // 计算属性
    currentCourse,
    hasCourses,
    
    // 方法
    fetchCourses,
    setActiveCourse,
    clearCurrentCourse,
    restoreCurrentCourse,
    addCourse,
    removeCourse,
    updateCourse,
  }
})
