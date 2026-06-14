<template>
  <nav>
    <RouterLink to="/" class="sidebar-logo">
      <img :src="miribomLogo" alt="미리봄 로고" />
    </RouterLink>
    <div class="product-searching">
      <p>탐색</p>
      <RouterLink to="/" class="sidebar-link">홈</RouterLink>
      <RouterLink to="/products" class="sidebar-link">둘러보기</RouterLink>
      <RouterLink to="/shorts" class="sidebar-link">숏폼</RouterLink>
    </div>
    <div class="user-action" v-if="isLogin">
      <p>내 활동</p>
      <RouterLink to="/favorites" class="sidebar-link">즐겨찾기</RouterLink>
      <RouterLink to="/likes" class="sidebar-link">좋아요</RouterLink>
      <RouterLink to="/review" class="sidebar-link">후기 등록</RouterLink>
    </div>
    <div class="category">
      <p>카테고리</p>
      <RouterLink
        v-for="category in categories"
        :key="category.id"
        :to="{ name: 'ProductSearch', query: { category: category.id } }"
        class="sidebar-link"
      >
        {{ category.name }}
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { fetchProductCategories } from '@/services/productApi.js'
import miribomLogo from '@/assets/images/miribom-logo.svg'

const { isLogin } = useAuth()
const categories = ref([])

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
nav {
  position: sticky;
  top: 0;
  width: 150px;
  height: 100vh;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background-color: #f0f0f0;
  padding: 0.5rem;
  box-sizing: border-box;
}
nav p {
  margin: 16px 0 8px;
  font-size: 12px;
  font-weight: 700;
  color: #777;
}

.sidebar-link {
  display: block;
  padding: 8px 10px;
  margin-bottom: 4px;
  text-decoration: none;
  color: #333;
  border-radius: 6px;
}

.sidebar-link:hover {
  background-color: #e0e0e0;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 0;
}

.sidebar-logo img {
  width: 90px;
  height: auto;
  display: block;
  object-fit: contain;
  border: none;
  padding: 0px;
  margin: 0px;
}
</style>
