import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
  },
  {
    path: '/',
    component: () => import('@/layouts/DashboardLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { roles: ['teacher', 'admin'] },
      },
      {
        path: 'dashboard/hot-questions',
        name: 'HotQuestions',
        component: () => import('@/views/HotQuestionsView.vue'),
        meta: { roles: ['teacher', 'admin'] },
      },
      {
        path: 'dashboard/students',
        name: 'Students',
        component: () => import('@/views/StudentsView.vue'),
        meta: { roles: ['teacher', 'admin'] },
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/ChatView.vue'),
        meta: { roles: ['student', 'teacher', 'admin'] },
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/KnowledgeView.vue'),
        meta: { roles: ['teacher', 'admin'] },
      },
      {
        path: 'grading',
        name: 'Grading',
        component: () => import('@/views/GradingView.vue'),
        meta: { roles: ['teacher', 'admin'] },
      },
      {
        path: 'questions',
        name: 'Questions',
        component: () => import('@/views/QuestionsView.vue'),
        meta: { roles: ['teacher', 'admin'] },
      },
      {
        path: 'practice',
        name: 'Practice',
        component: () => import('@/views/PracticeView.vue'),
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/CoursesView.vue'),
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('@/views/AdminView.vue'),
        meta: { roles: ['admin'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置守卫 - 使用返回值模式（Vue Router 4.3+ 推荐）
router.beforeEach((to, _from) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  let user: any = null
  
  if (userStr) {
    try {
      user = JSON.parse(userStr)
    } catch {
      user = null
    }
  }
  
  const isAuthenticated = !!token && !!user
  const publicRoutes = ['/login', '/register']
  
  // 公开路由 - 已登录用户访问登录页时重定向
  if (to.path === '/login' || to.path === '/register') {
    if (isAuthenticated) {
      // 根据角色重定向到不同页面
      const role = user?.role
      if (role === 'student') return '/chat'
      return '/dashboard'
    }
    return true
  }
  
  // 需要认证的路由
  if (!isAuthenticated) {
    return '/login'
  }
  
  // 检查角色
  if (to.meta.roles && user) {
    const roles = to.meta.roles as string[]
    if (!roles.includes(user.role)) {
      // 角色不符，重定向到首页
      return '/chat'
    }
  }
  
  return true
})

export default router
