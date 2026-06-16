<template>
  <nav class="app-sidebar" aria-label="주요 메뉴">
    <RouterLink to="/" class="sidebar-logo" @click="handleNavigationClick($event, '/')">
      <img :src="miribomLogo" alt="미리봄 로고" />
    </RouterLink>

    <div class="sidebar-section">
      <p class="sidebar-section__title">탐색</p>
      <RouterLink
        to="/"
        class="sidebar-link"
        active-class="sidebar-link--active"
        @click="handleNavigationClick($event, '/')"
      >
        홈
      </RouterLink>
      <RouterLink
        to="/products"
        class="sidebar-link"
        active-class="sidebar-link--active"
        @click="handleNavigationClick($event, '/products')"
      >
        둘러보기
      </RouterLink>
      <RouterLink
        to="/shorts"
        class="sidebar-link"
        active-class="sidebar-link--active"
        @click="handleNavigationClick($event, '/shorts')"
      >
        숏폼 시청
      </RouterLink>
    </div>

    <div v-if="isLogin" class="sidebar-section">
      <p class="sidebar-section__title">내 활동</p>
      <RouterLink
        to="/favorites"
        class="sidebar-link"
        active-class="sidebar-link--active"
        @click="handleNavigationClick($event, '/favorites')"
      >
        즐겨찾기
      </RouterLink>
      <RouterLink
        to="/likes"
        class="sidebar-link"
        active-class="sidebar-link--active"
        @click="handleNavigationClick($event, '/likes')"
      >
        좋아요
      </RouterLink>
      <RouterLink
        to="/review"
        class="sidebar-link"
        active-class="sidebar-link--active"
        @click="handleNavigationClick($event, '/review')"
      >
        후기 등록
      </RouterLink>
    </div>

    <div class="sidebar-section">
      <p class="sidebar-section__title">카테고리</p>
      <RouterLink
        v-for="category in categories"
        :key="category.id"
        :to="{ name: 'ProductSearch', query: { category: category.id } }"
        class="sidebar-link"
        :class="{ 'sidebar-link--active': isCategorySelected(category.id) }"
        @click="
          handleNavigationClick($event, {
            name: 'ProductSearch',
            query: { category: category.id },
          })
        "
      >
        {{ category.name }}
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import miribomLogo from '@/assets/images/miribom-logo.svg'
import { useAuth } from '@/composables/useAuth'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import { fetchProductCategories } from '@/services/productApi.js'

const route = useRoute()
const router = useRouter()
const { isLogin } = useAuth()
const { confirmUnsavedNavigation } = useUnsavedChanges()
const categories = ref([])

const isCategorySelected = (categoryId) =>
  String(route.query.category) === String(categoryId)

const handleNavigationClick = (event, target) => {
  if (route.fullPath === router.resolve(target).fullPath) {
    event.preventDefault()

    if (confirmUnsavedNavigation()) {
      window.location.reload()
    }
  }
}

const loadCategories = async () => {
  try {
    categories.value = await fetchProductCategories()
  } catch {
    categories.value = []
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.app-sidebar {
  position: sticky;
  top: 0;
  width: clamp(170px, 18vw, 240px);
  height: 100vh;
  flex-shrink: 0;
  overflow-y: auto;
  padding: var(--space-4) var(--space-3) var(--space-8);
  border-right: 1px solid var(--color-border);
  background-color: var(--color-surface);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4) 0;
}

.sidebar-logo img {
  width: 90px;
  height: auto;
  display: block;
  object-fit: contain;
}

.sidebar-section + .sidebar-section {
  margin-top: var(--space-5);
}

.sidebar-section__title {
  margin: 0 0 var(--space-2);
  padding: 0 var(--space-3);
  color: var(--color-text-tertiary);
  font-size: var(--font-size-caption);
  font-weight: 700;
  letter-spacing: 0.04em;
}

.sidebar-link {
  display: flex;
  min-height: 40px;
  align-items: center;
  margin-bottom: var(--space-1);
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-body);
  font-weight: 500;
  text-decoration: none;
  transition:
    background-color var(--transition-fast),
    color var(--transition-fast);
}

.sidebar-link:hover {
  background-color: var(--gray-50);
  color: var(--color-text);
}

.sidebar-link--active {
  background-color: var(--color-primary-light);
  color: var(--color-primary-600);
  font-weight: 700;
}

.sidebar-link--active:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary-600);
}

@media (max-width: 720px) {
  .app-sidebar {
    width: 152px;
  }

  .sidebar-link {
    padding-inline: var(--space-2);
  }
}
</style>
