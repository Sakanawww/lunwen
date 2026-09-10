<template>
  <div class="register-page">
    <!-- 左侧：品牌区域 -->
    <div class="register-brand">
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

    <!-- 右侧：注册表单 -->
    <div class="register-form-container">
      <div class="register-wrapper">
        <!-- 表单头部 -->
        <div class="register-header">
          <h2 class="form-title">创建账号</h2>
          <p class="form-subtitle">填写以下信息以注册新账号</p>
        </div>

        <!-- 注册表单 -->
        <form @submit.prevent="handleRegister" class="register-form">
          <!-- 用户名 -->
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
                :class="{ 'has-error': errorMessage }"
              />
            </div>
          </div>

          <!-- 真实姓名 -->
          <div class="form-group">
            <label for="real_name" class="form-label">
              <span class="label-text">真实姓名</span>
            </label>
            <div class="input-wrapper">
              <input
                id="real_name"
                v-model="form.real_name"
                type="text"
                class="form-input"
                placeholder="请输入真实姓名"
                required
                autocomplete="name"
                :class="{ 'has-error': errorMessage }"
              />
            </div>
          </div>

          <!-- 邮箱 -->
          <div class="form-group">
            <label for="email" class="form-label">
              <span class="label-text">邮箱</span>
            </label>
            <div class="input-wrapper">
              <input
                id="email"
                v-model="form.email"
                type="email"
                class="form-input"
                placeholder="请输入邮箱"
                autocomplete="email"
                :class="{ 'has-error': errorMessage }"
              />
            </div>
          </div>

          <!-- 角色 -->
          <div class="form-group">
            <label class="form-label">
              <span class="label-text">账号角色</span>
            </label>
            <div class="role-group">
              <label class="role-option">
                <input type="radio" value="student" v-model="form.role" />
                <span class="role-option-text"><i class="ri-graduation-cap-line"></i> 学生</span>
              </label>
              <label class="role-option">
                <input type="radio" value="teacher" v-model="form.role" />
                <span class="role-option-text"><i class="ri-presentation-line"></i> 教师</span>
              </label>
            </div>
          </div>

          <!-- 密码 -->
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
                autocomplete="new-password"
                :class="{ 'has-error': errorMessage }"
              />
            </div>
          </div>

          <!-- 确认密码 -->
          <div class="form-group">
            <label for="confirm_password" class="form-label">
              <span class="label-text">确认密码</span>
            </label>
            <div class="input-wrapper">
              <input
                id="confirm_password"
                v-model="form.confirmPassword"
                type="password"
                class="form-input"
                placeholder="请再次输入密码"
                required
                autocomplete="new-password"
                :class="{ 'has-error': errorMessage }"
              />
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="errorMessage" class="error-banner">
            <span class="error-icon">!</span>
            <span class="error-text">{{ errorMessage }}</span>
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            class="btn-register"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="loading-spinner"></span>
            <span class="btn-text">{{ isLoading ? '注册中...' : '注册' }}</span>
          </button>
        </form>

        <!-- 底部链接 -->
        <div class="register-footer">
          <span class="footer-text">已有账号？</span>
          <router-link to="/login" class="footer-link">立即登录</router-link>
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
import { useAuthStore } from '@/stores/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  real_name: '',
  email: '',
  role: 'student' as 'student' | 'teacher',
  password: '',
  confirmPassword: '',
})

const isLoading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  // 验证密码
  if (form.password !== form.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    await authStore.register({
      username: form.username,
      real_name: form.real_name,
      password: form.password,
      role: form.role,
    })
    router.push('/login')
  } catch (error: any) {
    errorMessage.value = error.message || '注册失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* ========== 页面布局 ========== */
.register-page {
  min-height: 100vh;
  display: flex;
  background: rgb(var(--paper));
}

/* ========== 左侧品牌区域 ========== */
.register-brand {
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
  font-size: var(--text-base);
  color: rgb(var(--paper));
  opacity: 0.7;
  font-weight: var(--font-normal);
  line-height: 1.6;
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
.register-form-container {
  width: 100%;
  max-width: 560px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-10);
  background: rgb(var(--paper));
}

.register-wrapper {
  width: 100%;
  max-width: 400px;
}

/* ========== 表单头部 ========== */
.register-header {
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
.register-form {
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

.form-input.has-error {
  border-color: var(--destructive);
}

.form-input.has-error:focus {
  box-shadow: 0 0 0 2px rgb(var(--card)), 0 0 0 4px rgba(var(--destructive), 0.15);
}

/* ========== 角色选择 ========== */
.role-group {
  display: flex;
  gap: var(--space-3);
}

.role-option {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 44px;
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  cursor: pointer;
  transition: all 0.2s ease;

  input[type="radio"] {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .role-option-text {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--text-primary);
    font-size: var(--text-base);

    i {
      color: var(--text-muted);
    }
  }

  &:hover {
    border-color: rgb(var(--ink));
  }

  /* 选中状态（原生 radio:checked 相邻标签） */
  &:has(input[type="radio"]:checked) {
    border-color: rgb(var(--ink));
    background: rgba(var(--ink), 0.06);

    .role-option-text {
      font-weight: var(--font-medium);

      i {
        color: rgb(var(--ink));
      }
    }
  }
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

/* ========== 注册按钮 ========== */
.btn-register {
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

.btn-register:hover:not(:disabled) {
  background: rgb(25, 75, 55);
  box-shadow: 0 3px 0 rgba(var(--ink), 0.25);
}

.btn-register:active:not(:disabled) {
  box-shadow: 0 1px 0 rgba(var(--ink), 0.15);
}

.btn-register:disabled {
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
.register-footer {
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
  .register-page {
    flex-direction: column;
  }

  .register-brand {
    min-height: 200px;
    padding: var(--space-6);
  }

  .brand-title {
    font-size: var(--text-2xl);
  }

  .brand-decoration {
    margin-top: var(--space-6);
  }

  .register-form-container {
    padding: var(--space-6);
  }

  .register-wrapper {
    max-width: 100%;
  }
}
</style>
