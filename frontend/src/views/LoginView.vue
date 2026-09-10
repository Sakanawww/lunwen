<template>
  <div class="login-page">
    <!-- 左侧：品牌区域 -->
    <div class="login-brand">
      <div class="brand-content">
        <h1 class="brand-title font-serif">课程助教系统</h1>
        <p class="brand-subtitle">基于 Agent 的智能教学辅助平台</p>
        
        <!-- 装饰性元素 -->
        <div class="brand-decoration">
          <div class="decoration-line"></div>
          <div class="decoration-dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：登录表单 -->
    <div class="login-form-container">
      <div class="login-wrapper">
        <!-- 表单头部 -->
        <div class="login-header">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-subtitle">请登录您的账号以继续</p>
        </div>

        <!-- 登录表单 -->
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- 用户名输入框 -->
          <div class="form-group">
            <label for="username" class="form-label">
              <span class="label-text">用户名</span>
            </label>
            <div class="input-wrapper">
              <input
                id="username"
                v-model="form.username"
                type="text"
                class="form-input"
                placeholder="请输入用户名"
                required
                autocomplete="username"
              />
            </div>
          </div>

          <!-- 密码输入框 -->
          <div class="form-group">
            <label for="password" class="form-label">
              <span class="label-text">密码</span>
            </label>
            <div class="input-wrapper">
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-input"
                placeholder="请输入密码"
                required
                autocomplete="current-password"
              />
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="errorMessage" class="error-banner" role="alert">
            <span class="error-icon">!</span>
            <span class="error-text">{{ errorMessage }}</span>
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            class="btn-login"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="loading-spinner"></span>
            <span class="btn-text">{{ isSubmitting ? '登录中...' : '登录' }}</span>
          </button>
        </form>

        <!-- 底部链接 -->
        <div class="login-footer">
          <span class="footer-text">还没有账号？</span>
          <router-link to="/register" class="footer-link">立即注册</router-link>
        </div>

        <!-- 版本信息 -->
        <div class="version-info">
          <span class="version-text">v2.0.0</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const form = reactive({
  username: 'student',
  password: '123456',
})

const isSubmitting = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    console.log('开始登录...')
    
    // 直接使用 axios 发送请求
    const response = await axios.post('http://127.0.0.1:8000/auth/login', {
      username: form.username,
      password: form.password,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,  // 携带 cookie
    })
    
    console.log('登录响应:', response.data)
    
    const result = response.data
    
    // 保存 token 到 localStorage
    localStorage.setItem('token', result.token)
    
    // 保存用户信息到 localStorage
    localStorage.setItem('user', JSON.stringify(result.user))
    
    console.log('登录成功，token:', result.token)
    console.log('用户信息:', result.user)
    
    // 根据用户角色决定跳转目标页面
    const role = result.user?.role
    let targetPath = '/dashboard'
    
    if (role === 'student') {
      targetPath = '/chat'  // 学生跳转到智能答疑
    } else if (role === 'teacher') {
      targetPath = '/dashboard'
    } else if (role === 'admin') {
      targetPath = '/dashboard'
    }
    
    // 直接跳转，确保新页面加载完整状态
    window.location.href = targetPath
    
  } catch (error: any) {
    console.error('登录失败:', error)
    if (error.response?.status === 401) {
      errorMessage.value = '用户名或密码错误'
    } else if (error.code === 'ERR_NETWORK') {
      errorMessage.value = '无法连接到服务器'
    } else {
      errorMessage.value = error.message || '登录失败'
    }
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* ========== 页面布局 ========== */
.login-page {
  min-height: 100vh;
  display: flex;
  background: rgb(var(--paper));
}

/* ========== 左侧品牌区域 ========== */
.login-brand {
  flex: 1;
  background: rgb(var(--ink));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-10);
  position: relative;
  overflow: hidden;
}

.brand-content {
  max-width: 400px;
  color: rgb(var(--paper));
}

.brand-title {
  font-size: 32px;
  font-weight: var(--font-normal);
  margin-bottom: var(--space-6);
  letter-spacing: var(--tracking-tight);
  color: rgb(var(--paper));
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.brand-subtitle {
  font-size: var(--text-lg);
  color: rgb(var(--paper));
  opacity: 0.9;
  font-weight: var(--font-normal);
  line-height: 1.6;
  margin-bottom: var(--space-6);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
}

.brand-decoration {
  margin-top: var(--space-10);
}

.decoration-line {
  width: 48px;
  height: 2px;
  background: rgb(var(--green));
  margin-bottom: var(--space-4);
}

.decoration-dots {
  display: flex;
  gap: var(--space-2);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: rgb(var(--paper));
  opacity: 0.5;
}

/* ========== 右侧表单区域 ========== */
.login-form-container {
  width: 100%;
  max-width: 560px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-10);
  background: rgb(var(--paper));
}

.login-wrapper {
  width: 100%;
  max-width: 400px;
}

/* ========== 表单头部 ========== */
.login-header {
  margin-bottom: var(--space-8);
}

.form-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  letter-spacing: var(--tracking-tight);
}

.form-subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
  font-weight: var(--font-normal);
}

/* ========== 表单样式 ========== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.label-text {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  letter-spacing: var(--tracking-normal);
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 var(--space-4);
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-input:focus {
  outline: none;
  border-color: rgb(var(--ink));
  box-shadow: 0 0 0 2px rgb(var(--card)), 0 0 0 4px rgba(var(--ink), 0.15);
}

/* ========== 错误提示 ========== */
.error-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--danger);
  border: 1px solid var(--destructive);
  border-radius: var(--radius-md);
}

.error-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: var(--radius-full);
  background: var(--destructive);
  color: white;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
}

.error-text {
  font-size: var(--text-sm);
  color: var(--danger-text);
  font-weight: var(--font-medium);
}

/* ========== 登录按钮 ========== */
.btn-login {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  height: 44px;
  width: 100%;
  background: rgb(var(--green));
  border: none;
  border-radius: var(--radius-md);
  color: rgb(var(--paper));
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 0 rgba(var(--ink), 0.2);
}

.btn-login:hover:not(:disabled) {
  background: rgb(25, 75, 55);
  box-shadow: 0 3px 0 rgba(var(--ink), 0.25);
}

.btn-login:active:not(:disabled) {
  box-shadow: 0 1px 0 rgba(var(--ink), 0.15);
}

.btn-login:disabled {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
}

.btn-text {
  letter-spacing: var(--tracking-wide);
}

/* ========== 加载动画 ========== */
.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(var(--paper), 0.3);
  border-top-color: rgb(var(--paper));
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ========== 底部链接 ========== */
.login-footer {
  text-align: center;
  padding-top: var(--space-4);
  border-top: 1px solid rgb(var(--line));
}

.footer-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.footer-link {
  color: rgb(var(--green));
  font-weight: var(--font-medium);
  margin-left: var(--space-2);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: rgb(25, 75, 55);
  text-decoration: underline;
}

/* ========== 版本信息 ========== */
.version-info {
  margin-top: var(--space-8);
  text-align: center;
}

.version-text {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-family: var(--font-mono);
  letter-spacing: var(--tracking-wide);
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }

  .login-brand {
    min-height: 200px;
    padding: var(--space-6);
  }

  .brand-title {
    font-size: var(--text-2xl);
  }

  .brand-decoration {
    margin-top: var(--space-6);
  }

  .login-form-container {
    padding: var(--space-6);
  }

  .login-wrapper {
    max-width: 100%;
  }
}
</style>
