import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth.store'
import { sanitizeInput } from './security'

// API 基础 URL - 开发环境使用 Vite 代理，生产环境可配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 token 和 CSRF 保护
request.interceptors.request.use(
  (config) => {
    // 添加认证 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加 CSRF token（如果存在）
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf_token='))
      ?.split('=')[1]
    
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 - 统一错误处理
request.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data
  },
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    
    // 401: 未授权，清除登录状态
    if (error.response?.status === 401) {
      authStore.logout()
      window.location.href = '/login'
      return Promise.reject(new Error('未授权，请重新登录'))
    }
    
    // 403: 权限不足
    if (error.response?.status === 403) {
      return Promise.reject(new Error('权限不足'))
    }
    
    // 422: 验证错误
    if (error.response?.status === 422) {
      const detail = (error.response.data as any)?.detail
      return Promise.reject(new Error(detail?.[0]?.msg || '验证失败'))
    }
    
    // 500: 服务器错误
    if (error.response?.status === 500) {
      return Promise.reject(new Error('服务器错误，请稍后重试'))
    }
    
    // 网络错误
    if (!error.response) {
      return Promise.reject(new Error('网络连接失败，请检查网络'))
    }
    
    return Promise.reject(error)
  }
)

export default request

// 快捷请求方法（响应拦截器已返回 response.data，这里直接透传）
export const api = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return request.get(url, config) as unknown as Promise<T>
  },

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.post(url, data, config) as unknown as Promise<T>
  },

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return request.put(url, data, config) as unknown as Promise<T>
  },

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return request.delete(url, config) as unknown as Promise<T>
  },

  // 上传文件
  upload<T = any>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<T> {
    return request.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }) as unknown as Promise<T>
  },
}
