import { createRouter, createWebHashHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false,
      hideForAuth: true // 已登录用户隐藏此页面
    }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true }, // 需要登录才能访问
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../pages/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'image-analysis',
        name: 'ImageAnalysis',
        component: () => import('../pages/ImageAnalysis.vue'),
        meta: { title: '图片识别' }
      },
      {
        path: 'data-analysis',
        name: 'Analysis',
        component: () => import('../pages/Analysis.vue'),
        meta: { title: '数据分析' }
      },
      {
        path: 'health',
        name: 'Health',
        component: () => import('../pages/Health.vue'),
        meta: { title: '心理健康' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('../pages/History.vue'),
        meta: { title: '历史记录' }
      },
      {
        path: 'video',
        name: 'VideoAnalysis',
        component: () => import('../pages/VideoAnalysis.vue'),
        meta: { title: '视频分析' }
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('../pages/User.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'about',
        name: 'About',
        component: () => import('../pages/About.vue'),
        meta: { title: '关于我们' }
      },
      {
        path: 'help',
        name: 'Help',
        component: () => import('../pages/About.vue'), // 暂时重用About页面
        meta: { title: '帮助中心' }
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('../pages/Admin.vue'),
        meta: { 
          title: '管理员面板',
          requiresAdmin: true
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫 - 认证检查和页面标题设置
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} · FaceLens`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 已登录，验证token有效性
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      // token无效，清除用户信息并跳转到登录页
      userStore.clearUser()
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  // 检查管理员权限
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    ElMessage.error('权限不足，只有管理员可以访问此页面')
    next('/')
    return
  }
  
  // 检查是否已登录用户访问登录页面
  if (to.meta.hideForAuth && userStore.isLoggedIn) {
    // 已登录用户访问登录页，重定向到首页
    next('/')
    return
  }
  
  next()
})

export default router
