import { createRouter, createWebHistory } from 'vue-router'
import SupplyChain from '../components/SupplyChain.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'SupplyChain',
      component: SupplyChain
    }
  ]
})

export default router

