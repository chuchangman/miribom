import FavoriteView from '@/views/FavoriteView.vue'
import HomeView from '@/views/HomeView.vue'
import LikedView from '@/views/LikedView.vue'
import LivingProfileView from '@/views/LivingProfileView.vue'
import LoginView from '@/views/LoginView.vue'
import MyPageView from '@/views/MyPageView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'
import ProductSearchView from '@/views/ProductSearchView.vue'
import ShortsView from '@/views/ShortsView.vue'
import SignupView from '@/views/SignupView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/signup', name: 'Signup', component: SignupView },
  { path: '/products', name: 'ProductSearch', component: ProductSearchView },
  { path: '/products/:id', name: 'ProductDetail', component: ProductDetailView },
  { path: '/living-profile', name: 'LivingProfile', component: LivingProfileView },
  { path: '/shorts', name: 'Shorts', component: ShortsView },
  { path: '/mypage', name: 'MyPage', component: MyPageView },
  { path: '/favorites', name: 'Favorite', component: FavoriteView },
  { path: '/likes', name: 'Liked', component: LikedView },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
