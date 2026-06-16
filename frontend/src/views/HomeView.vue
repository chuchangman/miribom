<template>
  <div class="home-layout">
    <section class="home-main">
      <h1>구매 전, 실제 사용 영상으로 <span class="highlight">미리 봄</span></h1>
      <h3>크기 · 작동음 · 공간 배치를 짧은 영상으로 확인하세요</h3>

      <form class="search-form" @submit.prevent="search">
        <input
          v-model.trim="searchQuery"
          type="text"
          class="search-input"
          placeholder="제품명, 카테고리로 검색하세요"
        />
        <button type="submit" class="text-button">검색</button>
      </form>

      <nav class="popular-searches">
        인기검색어 :
        <RouterLink to="/products?search=건조기">건조기</RouterLink>
        <RouterLink to="/products?search=영상기">영상기</RouterLink>
        <RouterLink to="/products?search=냉장고">냉장고</RouterLink>
      </nav>

      <hr />

      <section class="category-section">
        <h2>카테고리</h2>
        <p>원하는 가전을 골라보세요</p>
        <p v-if="isLoadingCategories">카테고리를 불러오는 중입니다.</p>
        <p v-else-if="categoryErrorMessage" class="error-message">
          {{ categoryErrorMessage }}
        </p>
        <div v-else class="category-list">
          <CategoryCard
            v-for="category in displayedCategories"
            :key="category.id"
            :category="category"
          />
        </div>
      </section>
    </section>

    <aside class="favorite-panel">
      <div class="favorite-header">
        <h2>즐겨찾기한 제품</h2>
        <RouterLink v-if="isLogin" to="/favorites">전체 보기</RouterLink>
      </div>

      <p v-if="!isLogin" class="favorite-message">
        <RouterLink to="/login">로그인</RouterLink>이 필요한 서비스입니다.
      </p>
      <p v-else-if="isLoadingFavorites" class="favorite-message">
        즐겨찾기를 불러오는 중입니다.
      </p>
      <p v-else-if="favoriteErrorMessage" class="favorite-message error-message">
        {{ favoriteErrorMessage }}
      </p>
      <p v-else-if="favoriteProducts.length === 0" class="favorite-message">
        즐겨찾기한 제품이 없습니다.
      </p>
      <div v-else class="favorite-list">
        <HomeFavoriteItem
          v-for="product in favoriteProducts"
          :key="product.id"
          :product="product"
        />
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import CategoryCard from '@/components/CategoryCard.vue'
import HomeFavoriteItem from '@/components/HomeFavoriteItem.vue'
import { useAuth } from '@/composables/useAuth.js'
import { fetchBookmarks } from '@/services/bookmarkApi.js'
import { fetchProductCategories } from '@/services/productApi.js'

const router = useRouter()
const { isAuthInitialized, isLogin } = useAuth()

const searchQuery = ref('')
const categories = ref([])
const isLoadingCategories = ref(false)
const categoryErrorMessage = ref('')
const favoriteProducts = ref([])
const isLoadingFavorites = ref(false)
const favoriteErrorMessage = ref('')

const displayedCategories = computed(() => categories.value.slice(0, 8))

function search() {
  router.push({
    name: 'ProductSearch',
    query: searchQuery.value ? { search: searchQuery.value } : {},
  })
}

const loadCategories = async () => {
  isLoadingCategories.value = true
  categoryErrorMessage.value = ''

  try {
    categories.value = await fetchProductCategories()
  } catch (error) {
    categoryErrorMessage.value = error.message || '카테고리를 불러오지 못했습니다.'
  } finally {
    isLoadingCategories.value = false
  }
}

const mapBookmarkProduct = (bookmark) => ({
  id: String(bookmark.product.id),
  name: bookmark.product.title,
  imageUrl: bookmark.product.image,
  price: bookmark.product.lprice || 0,
})

const loadFavorites = async () => {
  favoriteErrorMessage.value = ''

  if (!isLogin.value) {
    favoriteProducts.value = []
    return
  }

  isLoadingFavorites.value = true

  try {
    const bookmarks = await fetchBookmarks()
    favoriteProducts.value = bookmarks.slice(0, 4).map(mapBookmarkProduct)
  } catch (error) {
    favoriteErrorMessage.value = error.message || '즐겨찾기를 불러오지 못했습니다.'
  } finally {
    isLoadingFavorites.value = false
  }
}

watch(
  [isAuthInitialized, isLogin],
  ([isInitialized]) => {
    if (isInitialized) {
      loadFavorites()
    }
  },
  { immediate: true },
)

onMounted(loadCategories)
</script>

<style scoped>
.home-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 28px;
  align-items: start;
}

.home-main {
  min-width: 0;
}

h1 {
  margin: 0 0 0.5em;
  font-size: 2em;
}

h3 {
  margin-bottom: 1em;
  color: #64748b;
  font-size: 1.05em;
  font-weight: 500;
}

.highlight {
  color: #2563eb;
}

.search-form {
  display: flex;
  justify-content: space-between;
  gap: 0.5em;
  margin-bottom: 1em;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background-color: white;
  padding: 0.5em 0.75em;
}

.search-input {
  min-width: 0;
  flex: 1;
  border: 0;
  background-color: transparent;
  padding: 0.5em;
  outline: none;
  font-size: 1em;
}

.text-button {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
}

.popular-searches a {
  margin-left: 0.75em;
  color: #334155;
  text-decoration: none;
}

.popular-searches a:hover,
.favorite-header a:hover,
.favorite-message a:hover {
  text-decoration: underline;
}

hr {
  margin: 28px 0;
  border: 0;
  border-top: 1px solid #e2e8f0;
}

.category-section > h2 {
  margin-bottom: 6px;
}

.category-section > p {
  margin-top: 0;
  color: #64748b;
}

.category-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.category-list :deep(.category-card) {
  box-sizing: border-box;
  width: 100%;
  min-height: 104px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-color: #e2e8f0;
  border-radius: 14px;
  background-color: #fff;
}

.favorite-panel {
  min-height: 340px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background-color: #fff;
  padding: 22px;
  box-shadow: 0 8px 24px rgb(15 23 42 / 6%);
}

.favorite-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.favorite-header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.favorite-header a,
.favorite-message a {
  color: #2563eb;
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
}

.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.favorite-message {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  color: #64748b;
  text-align: center;
}

.error-message {
  color: #dc2626;
}

@media (max-width: 1000px) {
  .home-layout {
    grid-template-columns: 1fr;
  }

  .favorite-panel {
    width: auto;
  }
}

@media (max-width: 720px) {
  .category-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
