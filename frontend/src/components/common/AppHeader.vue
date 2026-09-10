<template>
  <header class="app-header">
    <div class="header-left">
      <button v-if="showSidebarToggle" class="sidebar-toggle" @click="toggleSidebar" type="button">
        <MenuIcon class="menu-icon" />
      </button>
      
      <div class="logo">
        <span class="logo-text">课程助教系统</span>
      </div>
      
      <nav class="main-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <component :is="item.icon" v-if="item.icon" class="nav-icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </div>

    <div class="header-right">
      <div v-if="showCourseSelector" class="course-selector">
        <DropdownSelect
          v-model="currentCourse"
          :options="courseOptions"
          placeholder="选择课程"
          :disabled="courseOptions.length === 0"
        />
      </div>

      <button class="icon-btn" type="button" @click="handleNotifications">
        <BellIcon class="icon" />
        <span v-if="unreadCount" class="badge">{{ unreadCount }}</span>
      </button>

      <div class="user-menu">
        <DropdownMenu>
          <template #trigger>
            <div class="user-trigger">
              <Avatar :name="user?.real_name" :size="32" />
              <span class="user-name">{{ user?.real_name }}</span>
              <ChevronDownIcon class="chevron" />
            </div>
          </template>
          <DropdownItem to="/profile">
            <UserIcon class="item-icon" />
            <span>个人中心</span>
          </DropdownItem>
          <DropdownDivider />
          <DropdownItem @click="handleLogout" class="danger">
            <LogoutIcon class="item-icon" />
            <span>退出登录</span>
          </DropdownItem>
        </DropdownMenu>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useCourseStore } from '@/stores/course.store'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import DropdownMenu from '@/components/common/DropdownMenu.vue'
import DropdownItem from '@/components/common/DropdownItem.vue'
import DropdownDivider from '@/components/common/DropdownDivider.vue'
import Avatar from '@/components/common/Avatar.vue'

const route = useRoute()
const authStore = useAuthStore()
const courseStore = useCourseStore()

const user = computed(() => authStore.user)
const courses = computed(() => courseStore.courses)
const currentCourse = computed({
  get: () => courseStore.currentCourseId,
  set: (value) => courseStore.setActiveCourse(value as number)
})

const props = withDefaults(defineProps<{
  showSidebarToggle?: boolean
  showCourseSelector?: boolean
}>(), {
  showSidebarToggle: true,
  showCourseSelector: true
})

const emit = defineEmits<{
  'sidebar-toggle': []
  'logout': []
}>()

const showCourseSelector = computed(() => {
  return props.showCourseSelector && courses.value.length > 0
})

const courseOptions = computed(() => {
  return courses.value.map(c => ({ value: c.id, label: c.name }))
})

const navItems = computed(() => {
  const role = user.value?.role
  if (role === 'student') {
    return [
      { path: '/chat', label: '答疑', icon: 'ChatIcon' },
      { path: '/practice', label: '练习', icon: 'PracticeIcon' }
    ]
  }
  if (role === 'teacher' || role === 'admin') {
    return [
      { path: '/dashboard', label: '仪表盘', icon: 'DashboardIcon' },
      { path: '/knowledge', label: '知识库', icon: 'KnowledgeIcon' },
      { path: '/grading', label: '批改', icon: 'GradingIcon' },
      { path: '/questions', label: '试题', icon: 'QuestionIcon' }
    ]
  }
  return [
    { path: '/admin', label: '管理', icon: 'AdminIcon' }
  ]
})

const isActive = (path: string) => {
  return route.path.startsWith(path)
}

const toggleSidebar = () => {
  emit('sidebar-toggle')
}

const handleNotifications = () => {
  // TODO: 实现通知面板
  console.log('Notifications clicked')
}

const handleLogout = () => {
  emit('logout')
  authStore.logout()
}

const emitDefine = defineEmits(['sidebar-toggle', 'logout'])
</script>

<script lang="ts">
// 图标组件
const MenuIcon = {
  template: `
    <svg class="menu-icon-svg" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 6H16M4 10H16M4 14H16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const BellIcon = {
  template: `
    <svg class="bell-icon-svg" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 2.5C7 2.5 5 4.5 5 7.5V10.5C5 11.5 4.5 12 4 12.5M15 12.5C14.5 12 14 11.5 14 10.5V7.5C14 4.5 12 2.5 9 2.5M6.5 15.5C6.5 16.5 7.5 17.5 8.5 17.5H10.5C11.5 17.5 12.5 16.5 12.5 15.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const ChevronDownIcon = {
  template: `
    <svg class="chevron-down-svg" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const UserIcon = {
  template: `
    <svg class="user-icon-svg" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 9.5C11.933 9.5 13.5 7.933 13.5 6C13.5 4.067 11.933 2.5 10 2.5C8.067 2.5 6.5 4.067 6.5 6C6.5 7.933 8.067 9.5 10 9.5ZM3.5 17.5C3.5 15.5 6 13.5 10 13.5C14 13.5 16.5 15.5 16.5 17.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
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

// 占位图标组件
const ChatIcon = { template: '<span></span>' }
const PracticeIcon = { template: '<span></span>' }
const DashboardIcon = { template: '<span></span>' }
const KnowledgeIcon = { template: '<span></span>' }
const GradingIcon = { template: '<span></span>' }
const QuestionIcon = { template: '<span></span>' }
const AdminIcon = { template: '<span></span>' }
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--navbar-height);
  padding: 0 var(--space-6);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-tertiary);
  }

  .menu-icon {
    width: 20px;
    height: 20px;
    color: var(--text-primary);
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-right: var(--space-4);
  margin-right: var(--space-4);
  border-right: 1px solid var(--border);

  .logo-text {
    font-family: var(--font-serif);
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    letter-spacing: var(--tracking-tight);
  }
}

.main-nav {
  display: flex;
  gap: var(--space-2);
  margin-left: var(--space-4);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(var(--green), 0.1);
    color: rgb(var(--green));
  }

  &.active {
    background: rgb(var(--green));
    color: rgb(var(--paper));
  }

  .nav-icon {
    width: 18px;
    height: 18px;
  }
}

.course-selector {
  width: 180px;
}

.icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-tertiary);
  }

  .icon {
    width: 20px;
    height: 20px;
    color: var(--text-primary);
  }

  .badge {
    position: absolute;
    top: 6px;
    right: 8px;
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    background: rgb(var(--destructive));
    border-radius: 8px;
    font-size: 10px;
    font-weight: var(--font-semibold);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.user-menu {
  margin-left: var(--space-2);
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-tertiary);
  }

  .user-name {
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--text-primary);
  }

  .chevron {
    width: 16px;
    height: 16px;
    color: var(--text-secondary);
  }
}

// 图标 SVG 样式
.menu-icon-svg,
.bell-icon-svg,
.chevron-down-svg,
.user-icon-svg,
.logout-icon-svg {
  width: 100%;
  height: 100%;
  color: currentColor;
}
</style>
