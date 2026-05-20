import HomeView from '@/views/HomeView.vue'
import LivingProfileView from '@/views/LivingProfileView.vue'
import LoginView from '@/views/LoginView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'
import ProductSearchView from '@/views/ProductSearchView.vue'
import SignupView from '@/views/SignupView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/signup', name: 'Signup', component: SignupView },
  { path: '/products', name: 'ProductSearch', component: ProductSearchView },
  { path: '/products/:id', name: 'ProductDetail', component: ProductDetailView },
  { path: '/living-profile', name: 'LivingProfile', component: LivingProfileView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
