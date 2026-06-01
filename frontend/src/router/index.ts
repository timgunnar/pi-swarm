import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
        { path: 'nodes', name: 'nodes', component: () => import('@/views/Nodes.vue') },
        { path: 'nodes/:name', name: 'node-detail', component: () => import('@/views/NodeDetail.vue'), props: true },
        { path: 'models', name: 'models', component: () => import('@/views/Models.vue') },
        { path: 'logs', name: 'logs', component: () => import('@/views/Logs.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/views/Settings.vue') },
      ],
    },
  ],
})

export default router
