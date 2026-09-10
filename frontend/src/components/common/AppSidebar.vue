<template>
  <aside class="app-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <span class="logo-text" :class="{ 'logo-text-collapsed': isCollapsed }">
          {{ isCollapsed ? '助教' : '课程助教系统' }}
        </span>
      </div>
      <button
        v-if="showCollapseBtn"
        class="collapse-btn"
        @click="toggleCollapse"
        type="button"
        :aria-label="isCollapsed ? '展开侧边栏' : '收起侧边栏'"
      >
        <ChevronLeftIcon :class="{ 'flipped': isCollapsed }" />
      </button>
    </div>

    <nav class="sidebar-nav">
      <div v-for="(section, index) in navSections" :key="index" class="nav-section">
        <div v-if="section.title" class="nav-section-title">
          <span>{{ isCollapsed ? section.shortTitle || section.title[0] : section.title }}</span>
        </div>
        <ul class="nav-list">
          <li v-for="item in section.items" :key="item.path" class="nav-item">
            <router-link
              :to="item.path"
              class="nav-link"
              :class="{ active: isActive(item.path) }"
              :title="isCollapsed ? item.label : ''"
            >
              <component :is="item.icon" v-if="item.icon" class="nav-icon" />
              <span class="nav-label" :class="{ 'label-hidden': isCollapsed }">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info" :class="{ 'info-hidden': isCollapsed }">
        <Avatar :name="user?.real_name" :size="32" />
        <div class="user-details">
          <div class="user-name">{{ user?.real_name }}</div>
          <div class="user-role">{{ roleLabel }}</div>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout" type="button" :title="isCollapsed ? '退出登录' : ''">
        <LogoutIcon class="logout-icon" />
        <span v-if="!isCollapsed" class="logout-label">退出登录</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import Avatar from '@/components/common/Avatar.vue'

const route = useRoute()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const props = withDefaults(defineProps<{
  isCollapsed?: boolean
  showCollapseBtn?: boolean
}>(), {
  isCollapsed: false,
  showCollapseBtn: true
})

const emit = defineEmits<{
  'update:isCollapsed': [value: boolean]
  'logout': []
}>()

const isCollapsed = computed({
  get: () => props.isCollapsed,
  set: (value) => emit('update:isCollapsed', value)
})

const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    student: '学生',
    teacher: '教师',
    admin: '管理员',
    assistant: '助教'
  }
  return roleMap[user.value?.role || ''] || ''
})

const toggleCollapse = () => {
  emit('update:isCollapsed', !isCollapsed.value)
}

const handleLogout = () => {
  emit('logout')
  authStore.logout()
}

// 导航项配置 - 根据角色动态生成
const navSections = computed(() => {
  const role = user.value?.role
  
  if (role === 'student') {
    return [
      {
        title: '学习',
        shortTitle: '学',
        items: [
          { path: '/chat', label: '智能答疑', icon: 'ChatIcon' },
          { path: '/practice', label: '答题练习', icon: 'PracticeIcon' },
          { path: '/sessions', label: '对话历史', icon: 'HistoryIcon' }
        ]
      },
      {
        title: '我的',
        shortTitle: '我',
        items: [
          { path: '/records', label: '学习记录', icon: 'RecordIcon' },
          { path: '/profile', label: '个人中心', icon: 'ProfileIcon' }
        ]
      }
    ]
  }
  
  if (role === 'teacher' || role === 'assistant') {
    return [
      {
        title: '教学',
        shortTitle: '教',
        items: [
          { path: '/dashboard', label: '仪表盘', icon: 'DashboardIcon' },
          { path: '/knowledge', label: '知识库', icon: 'KnowledgeIcon' },
          { path: '/grading', label: '批改作业', icon: 'GradingIcon' }
        ]
      },
      {
        title: '管理',
        shortTitle: '管',
        items: [
          { path: '/questions', label: '试题管理', icon: 'QuestionIcon' },
          { path: '/students', label: '学生管理', icon: 'StudentIcon' }
        ]
      }
    ]
  }
  
  // admin
  return [
    {
      title: '系统',
      shortTitle: '系',
      items: [
        { path: '/admin', label: '管理后台', icon: 'AdminIcon' },
        { path: '/agents', label: 'Agent 配置', icon: 'AgentIcon' },
        { path: '/logs', label: '系统日志', icon: 'LogIcon' }
      ]
    }
  ]
})

const isActive = (path: string) => {
  return route.path.startsWith(path)
}

const emitDefine = defineEmits(['update:isCollapsed', 'logout'])
</script>

<script lang="ts">
// 图标组件
const ChevronLeftIcon = {
  template: `
    <svg class="chevron-left-svg" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const LogoutIcon = {
  template: `
    <svg class="logout-icon-svg" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M11.5 13.5L14.5 10.5M14.5 10.5L11.5 7.5M14.5 10.5H7M10 17.5C6.5 17.5 3.5 17 3.5 10.5C3.5 4 6.5 3.5 10 3.5C13.5 3.5 16.5 4 16.5 10.5C16.5 17 13.5 17.5 10 17.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

// 占位图标
const ChatIcon = { template: '<span></span>' }
const PracticeIcon = { template: '<span></span>' }
const HistoryIcon = { template: '<span></span>' }
const RecordIcon = { template: '<span></span>' }
const ProfileIcon = { template: '<span></span>' }
const DashboardIcon = { template: '<span></span>' }
const KnowledgeIcon = { template: '<span></span>' }
const GradingIcon = { template: '<span></span>' }
const QuestionIcon = { template: '<span></span>' }
const StudentIcon = { template: '<span></span>' }
const AdminIcon = { template: '<span></span>' }
const AgentIcon = { template: '<span></span>' }
const LogIcon = { template: '<span></span>' }
</script>

<style lang="scss" scoped>
.app-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 100;

  &.collapsed {
    width: var(--sidebar-collapsed-width);
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--navbar-height);
  padding: 0 var(--space-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  flex: 1;
  overflow: hidden;

  .logo-text {
    font-family: var(--font-serif);
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: rgb(var(--paper));
    white-space: nowrap;
    letter-spacing: var(--tracking-tight);
    transition: opacity 0.2s ease;

    &.logo-text-collapsed {
      opacity: 0;
      width: 0;
    }
  }
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }

  .chevron-left-svg {
    width: 16px;
    height: 16px;
    color: rgb(var(--paper));
    transition: transform 0.3s ease;

    &.flipped {
      transform: rotate(180deg);
    }
  }
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4) 0;
}

.nav-section {
  margin-bottom: var(--space-6);

  &:last-child {
    margin-bottom: 0;
  }
}

.nav-section-title {
  padding: 0 var(--space-4);
  margin-bottom: var(--space-2);

  span {
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    color: rgba(255, 255, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    white-space: nowrap;
    overflow: hidden;
  }
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4);
  margin: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 20px;
    background: rgb(var(--green));
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    transition: width 0.2s ease;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgb(var(--paper));
  }

  &.active {
    background: rgba(var(--green), 0.2);
    color: rgb(var(--paper));

    &::before {
      width: 3px;
    }
  }

  .nav-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    opacity: 0.8;
  }

  .nav-label {
    white-space: nowrap;
    overflow: hidden;
    transition: opacity 0.2s ease;

    &.label-hidden {
      opacity: 0;
      width: 0;
    }
  }
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  margin-bottom: var(--space-3);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  transition: opacity 0.2s ease;

  &.info-hidden {
    .user-details {
      opacity: 0;
      width: 0;
    }
  }

  .user-details {
    flex: 1;
    overflow: hidden;
    transition: all 0.2s ease;

    .user-name {
      font-size: var(--text-sm);
      font-weight: var(--font-medium);
      color: rgb(var(--paper));
      white-space: nowrap;
    }

    .user-role {
      font-size: var(--text-xs);
      color: rgba(255, 255, 255, 0.5);
      white-space: nowrap;
    }
  }
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  color: rgba(255, 255, 255, 0.7);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgb(var(--paper));
    border-color: rgba(255, 255, 255, 0.3);
  }

  .logout-icon {
    width: 18px;
    height: 18px;
  }

  .logout-label {
    white-space: nowrap;
  }
}

// 滚动条样式
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
