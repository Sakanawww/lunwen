<template>
  <div class="dashboard-layout">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <!-- 左侧：Logo + 导航 -->
      <div class="header-left">
        <div class="logo">
          <span class="logo-text font-serif">课程助教系统</span>
        </div>

        <nav class="main-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
      </div>

      <!-- 右侧：用户菜单 -->
      <div class="header-right">
        <!-- 用户下拉菜单 -->
        <div class="user-menu">
          <span class="user-name">{{ user?.real_name }}</span>
          <span class="user-role">{{ user?.role }}</span>
          <button @click="handleLogout" class="btn-logout" title="退出登录">
            退出
          </button>
        </div>
      </div>
    </header>


    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useCourseStore } from '@/stores/course.store'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const courseStore = useCourseStore()

const user = computed(() => authStore.user)

const navItems = computed(() => {
  const role = user.value?.role
  if (!role) return []
  
  // 根据角色显示不同的导航
  if (role === 'student') {
    return [
      { path: '/chat', label: '智能答疑' },
      { path: '/practice', label: '在线练习' },
      { path: '/courses', label: '我的课程' },
    ]
  } else if (role === 'teacher') {
    return [
      { path: '/dashboard', label: '仪表盘' },
      { path: '/dashboard/students', label: '学生名单' },
      { path: '/knowledge', label: '知识库' },
      { path: '/grading', label: '作业批改' },
      { path: '/questions', label: '试题管理' },
    ]
  } else {
    // admin — 与 teacher 共享教学管理功能，额外拥有系统设置
    return [
      { path: '/dashboard', label: '学情看板' },
      { path: '/dashboard/students', label: '学生名单' },
      { path: '/knowledge', label: '知识库' },
      { path: '/grading', label: '作业批改' },
      { path: '/questions', label: '试题管理' },
      { path: '/admin', label: '系统设置' },
    ]
  }
})

// 侧边栏导航组（已移除）
const navGroups = computed(() => [])

const handleLogout = () => {
  authStore.logout()
}

// 挂载时加载数据
onMounted(async () => {
  await courseStore.fetchCourses()
  courseStore.restoreCurrentCourse()
})
</script>

<style scoped>
/* ========== 布局容器 ========== */
.dashboard-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: rgb(var(--paper));
}

/* ========== 顶部导航栏 ========== */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-h);
  padding: 0 var(--space-6);
  background: rgb(var(--card));
  border-bottom: 1px solid rgb(var(--line));
  box-shadow: 0 1px 2px rgba(var(--ink), 0.05);
  z-index: var(--z-header);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

.logo {
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
}

.main-nav {
  display: flex;
  gap: var(--space-1);
}

.nav-item {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgb(var(--line));
  color: var(--text-primary);
}

.nav-item.active {
  background: rgb(var(--green));
  color: rgb(var(--paper));
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.course-selector {
  height: 36px;
  padding: 0 var(--space-3);
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  background: rgb(var(--card));
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.course-selector:hover {
  border-color: rgb(var(--ink));
}

.course-selector:focus {
  outline: none;
  border-color: rgb(var(--ink));
  box-shadow: 0 0 0 2px rgb(var(--card)), 0 0 0 4px rgba(var(--ink), 0.1);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-left: var(--space-4);
  border-left: 1px solid rgb(var(--line));
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.user-role {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.btn-logout {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  background: transparent;
  border: 1px solid rgb(var(--line));
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background: var(--danger);
  border-color: var(--destructive);
  color: var(--danger-text);
}

/* ========== 侧边栏 ========== */
.app-sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: rgb(var(--card));
  border-right: 1px solid rgb(var(--line));
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-4) 0;
}

.nav-group {
  margin-bottom: var(--space-6);
}

.group-title {
  padding: 0 var(--space-4);
  margin-bottom: var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.nav-link {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-4);
  margin: var(--space-1) var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: rgb(var(--line));
  color: var(--text-primary);
}

.nav-link.active {
  background: rgb(var(--green));
  color: rgb(var(--paper));
}

.nav-label {
  flex: 1;
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid rgb(var(--line));
  text-align: center;
}

.version {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-family: var(--font-mono);
  letter-spacing: var(--tracking-wide);
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  background: rgb(var(--paper));
}

/* ========== 过渡动画 ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
