import FavoriteView from '@/views/FavoriteView.vue'
import HomeView from '@/views/HomeView.vue'
import LikedView from '@/views/LikedView.vue'
import LivingProfileView from '@/views/LivingProfileView.vue'
import LoginView from '@/views/LoginView.vue'
import MyPageView from '@/views/MyPageView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'
import ProductSearchView from '@/views/ProductSearchView.vue'
import ProfileEditView from '@/views/ProfileEditView.vue'
import ReviewCreateView from '@/views/ReviewCreateView.vue'
import ShortsView from '@/views/ShortsView.vue'
import SignupView from '@/views/SignupView.vue'
import { useAuth } from '@/composables/useAuth'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView, meta: { guestOnly: true } },
  { path: '/signup', name: 'Signup', component: SignupView, meta: { guestOnly: true } },
  { path: '/products', name: 'ProductSearch', component: ProductSearchView },
  { path: '/products/:id', name: 'ProductDetail', component: ProductDetailView },
  {
    path: '/living-profile',
    name: 'LivingProfile',
    component: LivingProfileView,
    meta: { requiresAuth: true },
  },
  { path: '/shorts', name: 'Shorts', component: ShortsView },
  { path: '/mypage', name: 'MyPage', component: MyPageView, meta: { requiresAuth: true } },
  {
    path: '/favorites',
    name: 'Favorite',
    component: FavoriteView,
    meta: { requiresAuth: true },
  },
  { path: '/likes', name: 'Liked', component: LikedView, meta: { requiresAuth: true } },
  {
    path: '/profile-edit',
    name: 'ProfileEdit',
    component: ProfileEditView,
    meta: { requiresAuth: true },
  },
  {
    path: '/review',
    name: 'ReviewCreate',
    component: ReviewCreateView,
    meta: { requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }

    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const { checkAuth, hasLivingProfile } = useAuth()
  const isAuthenticated = await checkAuth()

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'Login' }
  }

  if (isAuthenticated && !hasLivingProfile.value && to.name !== 'LivingProfile') {
    return { name: 'LivingProfile', query: { mode: 'onboarding' } }
  }

  if (to.meta.guestOnly && isAuthenticated) {
    return { name: 'Home' }
  }

  return true
})

export default router
