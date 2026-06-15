<template>
  <button type="button" class="back-button" @click="goBack">← 이전으로</button>
  <p v-if="isLoading">제품 정보를 불러오는 중입니다.</p>
  <div v-else-if="errorMessage">
    <h1>{{ errorMessage }}</h1>
  </div>
  <div v-else-if="!product">
    <h1>제품을 찾을 수 없습니다.</h1>
  </div>
  <div v-else>
    <section class="product-hero">
      <div class="image">
        <img :src="product.image" :alt="product.title" />
      </div>
      <div class="info">
        <p>{{ product.title }}</p>
        <p>{{ product.brand }}</p>
        <p>{{ (product.lprice || 0).toLocaleString() }} 원</p>
        <p>{{ product.category?.name }}</p>
        <a :href="product.link" target="_blank" rel="noopener noreferrer">네이버 상품 보기</a>
        <button
          type="button"
          class="bookmark-button"
          :disabled="isBookmarkPending"
          @click="toggleBookmark"
        >
          {{ bookmarkId ? '♥ 즐겨찾기 해제' : '♡ 즐겨찾기 추가' }}
        </button>
        <p v-if="bookmarkErrorMessage" class="error-message">{{ bookmarkErrorMessage }}</p>
      </div>
    </section>
    <section class="product-ratings">
      <p>평점 : 0</p>
    </section>
    <section class="product-reviews">
      <p>리뷰 : 0</p>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchProductDetail } from '@/services/productApi.js'
import { createBookmark, deleteBookmark, fetchBookmarks } from '@/services/bookmarkApi.js'
import { useAuth } from '@/composables/useAuth.js'

const route = useRoute()
const router = useRouter()
const { isAuthInitialized, isLogin } = useAuth()
const product = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const bookmarkId = ref(null)
const isBookmarkPending = ref(false)
const bookmarkErrorMessage = ref('')

const loadProduct = async () => {
  isLoading.value = true
  errorMessage.value = ''
  bookmarkId.value = null
  bookmarkErrorMessage.value = ''

  try {
    product.value = await fetchProductDetail(route.params.id)
  } catch (error) {
    product.value = null
    errorMessage.value = error.message || '제품 상세 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  if (window.history.state?.back) {
    router.back()
    return
  }

  router.push({ name: 'ProductSearch' })
}

const loadBookmarkState = async () => {
  bookmarkErrorMessage.value = ''

  if (!isAuthInitialized.value || !isLogin.value || !product.value) {
    bookmarkId.value = null
    return
  }

  try {
    const bookmarks = await fetchBookmarks()
    const bookmark = bookmarks.find(
      (item) => item.product.id === Number(product.value.id),
    )
    bookmarkId.value = bookmark?.id || null
  } catch (error) {
    bookmarkErrorMessage.value = error.message || '즐겨찾기 상태를 불러오지 못했습니다.'
  }
}

const toggleBookmark = async () => {
  if (!isLogin.value) {
    router.push({ name: 'Login' })
    return
  }

  if (isBookmarkPending.value) {
    return
  }

  isBookmarkPending.value = true
  bookmarkErrorMessage.value = ''

  try {
    if (bookmarkId.value) {
      await deleteBookmark(bookmarkId.value)
      bookmarkId.value = null
    } else {
      const bookmark = await createBookmark(Number(product.value.id))
      bookmarkId.value = bookmark.id
    }
  } catch (error) {
    bookmarkErrorMessage.value = error.message || '즐겨찾기 상태를 변경하지 못했습니다.'
  } finally {
    isBookmarkPending.value = false
  }
}

watch(() => route.params.id, loadProduct, { immediate: true })
watch([isAuthInitialized, isLogin, product], loadBookmarkState)
</script>

<style scoped>
.error-message {
  color: red;
}
.back-button {
  margin-bottom: 20px;
  border: none;
  background: none;
  padding: 0;
  color: #2563eb;
  font-size: 1rem;
  cursor: pointer;
}
.back-button:hover {
  text-decoration: underline;
}
.product-hero {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}
.image {
  width: 300px;
  height: 300px;
  border-radius: 16px;
  background-color: #f3f7ff;
  overflow: hidden;

  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}
.image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.bookmark-button {
  align-self: flex-start;
  border: 1px solid #2563eb;
  border-radius: 8px;
  background-color: white;
  padding: 8px 12px;
  color: #2563eb;
  cursor: pointer;
}
.bookmark-button:disabled {
  cursor: pointer;
  opacity: 0.6;
}
</style>
