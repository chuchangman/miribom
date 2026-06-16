<template>
  <h1>즐겨찾기페이지</h1>
  <p v-if="isLoading">즐겨찾기를 불러오는 중입니다.</p>
  <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  <p v-else-if="favoriteProducts.length === 0">즐겨찾기한 제품이 없습니다.</p>
  <ul v-else>
    <li v-for="item in favoriteProducts" :key="item.product.id">
      <ProductCard
        :product="item.product"
        :is-bookmarked="item.isBookmarked"
        :is-bookmark-pending="pendingProductId === item.product.id"
        :manage-bookmark="true"
        @toggle-bookmark="toggleFavorite(item)"
      />
    </li>
  </ul>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ProductCard from '@/components/ProductCard.vue'
import { createBookmark, deleteBookmark, fetchBookmarks } from '@/services/bookmarkApi.js'

const favoriteProducts = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const pendingProductId = ref(null)

const mapBookmark = (bookmark) => ({
  bookmarkId: bookmark.id,
  isBookmarked: true,
  product: {
    id: String(bookmark.product.id),
    name: bookmark.product.title,
    imageUrl: bookmark.product.image,
    category: bookmark.product.category?.name || '',
    brand: bookmark.product.brand || '',
    price: bookmark.product.lprice || 0,
    description: '',
  },
})

const loadFavorites = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const bookmarks = await fetchBookmarks()
    favoriteProducts.value = bookmarks.map(mapBookmark)
  } catch (error) {
    errorMessage.value = error.message || '즐겨찾기를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const toggleFavorite = async (item) => {
  if (pendingProductId.value !== null) {
    return
  }

  pendingProductId.value = item.product.id
  errorMessage.value = ''

  try {
    if (item.isBookmarked) {
      await deleteBookmark(item.bookmarkId)
      item.bookmarkId = null
      item.isBookmarked = false
    } else {
      const bookmark = await createBookmark(Number(item.product.id))
      item.bookmarkId = bookmark.id
      item.isBookmarked = true
    }
  } catch (error) {
    errorMessage.value = error.message || '즐겨찾기 상태를 변경하지 못했습니다.'
  } finally {
    pendingProductId.value = null
  }
}

onMounted(loadFavorites)
</script>

<style scoped>
.error-message {
  color: red;
}
ul {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  list-style: none;
  padding: 0;
}
li {
  min-width: 0;
}
</style>
