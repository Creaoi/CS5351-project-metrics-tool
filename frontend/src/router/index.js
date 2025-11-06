import { createRouter, createWebHistory } from 'vue-router'
import Analyze from '@/views/Analyze.vue'
import Dashboard from '@/views/Dashboard.vue'

const routes = [
  { path: '/', name: 'Analyze', component: Analyze },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard }, // 小写
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
