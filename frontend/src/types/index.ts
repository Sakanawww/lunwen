/**
 * 类型定义
 * 项目通用的 TypeScript 类型和接口
 */

// ========== 用户相关 ==========

export interface User {
  id: number
  username: string
  real_name: string
  role: 'student' | 'teacher' | 'admin' | 'assistant'
  created_at?: string
}

export interface Student extends User {
  role: 'student'
  student_no: string
  class_name?: string
}

export interface Teacher extends User {
  role: 'teacher' | 'admin'
  teacher_no: string
  department?: string
}

// ========== 课程相关 ==========

export interface Course {
  id: number
  name: string
  code?: string
  teacher_id?: number
  teacher_name?: string
  description?: string
  created_at?: string
  student_count?: number
}

export interface CourseUser {
  id: number
  course_id: number
  user_id: number
  role: 'owner' | 'teacher' | 'assistant' | 'student'
  created_at?: string
}

export interface Enrollment {
  id: number
  student_id: number
  course_id: number
}

// ========== 知识库相关 ==========

export interface KnowledgeDoc {
  id: number
  course_id: number
  title: string
  file_name?: string
  chunk_num: number
  upload_by?: number
  created_at?: string
}

export interface KnowledgeChunk {
  id: number
  doc_id: number
  seq: number
  content: string
  source?: string
}

// ========== 会话与消息 ==========

export interface Session {
  id: number
  user_id: number
  course_id?: number
  title?: string
  is_deleted?: number
  deleted_at?: string
  created_at?: string
}

export interface Message {
  id?: number
  session_id?: number
  role: 'user' | 'assistant' | 'agent' | 'system'
  content: string
  sources?: string[]
  created_at?: string
}

// ========== 作业与批改 ==========

export interface Assignment {
  id: number
  course_id: number
  title: string
  description?: string
  deadline?: string
  created_at?: string
}

export interface Submission {
  id: number
  assignment_id: number
  student_id: number
  content: string
  status: 'pending' | 'graded'
  submitted_at?: string
}

export interface GradingRecord {
  id: number
  submission_id: number
  score?: number
  feedback?: string
  grade_by: 'ai' | 'teacher'
  graded_at?: string
}

// ========== 试题相关 ==========

export interface Question {
  id: number
  course_id: number
  type: 'choice' | 'fill' | 'short'
  stem: string
  options?: string
  answer: string
  difficulty: number
  created_by?: number
  source: 'ai' | 'manual'
  is_deleted?: number
  deleted_at?: string
  created_at?: string
}

export interface LearningRecord {
  id: number
  student_id: number
  course_id: number
  question_id?: number
  is_correct?: number
  score?: number
  created_at?: string
}

// ========== Agent 配置 ==========

export interface AgentConfig {
  id: number
  name: string
  role_desc?: string
  model?: string
  enabled: number
  route_keywords?: string
  sort_order: number
  updated_at?: string
}

// ========== 系统日志 ==========

export interface SystemLog {
  id: number
  user_id?: number
  action: string
  detail?: string
  status?: string
  ip?: string
  created_at?: string
}

// ========== API 响应 ==========

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PageResponse<T = any> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ========== 表单项 ==========

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  real_name: string
  password: string
  role: 'student' | 'teacher' | 'admin'
}

export interface UploadForm {
  course_id: number
  file: File
}

// ========== 通用类型 ==========

export type Role = 'student' | 'teacher' | 'admin' | 'assistant'

export type Status = 'pending' | 'processing' | 'completed' | 'failed'

export interface Option {
  value: string | number
  label: string
  disabled?: boolean
}

export interface SelectOption extends Option {
  icon?: string
}
