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
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
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

// 简化的路由守卫 - 仅检查 token 是否存在
router.beforeEach((to, _from, next) => {
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
  
  // 公开路由
  if (publicRoutes.includes(to.path)) {
    if (isAuthenticated) {
      next('/dashboard')
      return
    }
    next()
    return
  }
  
  // 需要认证的路由
  if (!isAuthenticated) {
    next('/login')
    return
  }
  
  // 检查角色
  if (to.meta.roles && user) {
    const roles = to.meta.roles as string[]
    if (!roles.includes(user.role)) {
      next('/dashboard')
      return
    }
  }
  
  next()
})

export default router
