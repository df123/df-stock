import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/realtime',
    name: 'Realtime',
    component: () => import('../views/Realtime.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue')
  },
  {
    path: '/database',
    name: 'Database',
    component: () => import('../views/Database.vue')
  },
  {
    path: '/screening',
    name: 'Screening',
    component: () => import('../views/Screening.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
