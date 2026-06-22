<template>
  <div class="search-controls">
    <select v-model="selectedCategory" class="category-select" @change="changeCategory">
      <option value="">전체</option>
      <option v-for="category in categories" :key="category.id" :value="String(category.id)">
        {{ category.name }}
      </option>
    </select>
    <form @submit.prevent="handleSearch" class="search-form">
      <input
        type="text"
        class="search-input"
        placeholder="제품명 검색"
        v-model.trim="searchInput"
      />
      <button type="submit" class="text-button">검색</button>
    </form>
  </div>
  <p v-if="isLoading && products.length === 0">제품을 불러오는 중입니다.</p>
  <p v-else-if="errorMessage && products.length === 0" class="error-message">
    {{ errorMessage }}
  </p>
  <p v-else-if="products.length === 0">검색 결과가 없습니다.</p>
  <template v-else>
    <ul>
      <li v-for="product in products" :key="product.id">
        <ProductCard
          :product="product"
          :is-bookmarked="bookmarksByProductId.has(Number(product.id))"
          :is-bookmark-pending="bookmarkPendingProductId === Number(product.id)"
          :manage-bookmark="true"
          @toggle-bookmark="toggleProductBookmark"
        />
      </li>
    </ul>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="bookmarkErrorMessage" class="error-message">{{ bookmarkErrorMessage }}</p>
    <p v-if="isLoadingMore">제품을 더 불러오는 중입니다.</p>
    <div v-if="hasNext" ref="loadMoreTrigger" class="load-more-trigger" aria-hidden="true"></div>
  </template>
</template>

<script setup>
import { onBeforeRouteLeave, useRouter, useRoute } from 'vue-router'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ProductCard from '@/components/ProductCard.vue'
import { fetchProductCategories, fetchProducts } from '@/services/productApi.js'
import { useProductSearchState } from '@/composables/useProductSearchState.js'
import { createBookmark, deleteBookmark, fetchBookmarks } from '@/services/bookmarkApi.js'
import { useAuth } from '@/composables/useAuth.js'

const router = useRouter()
const route = useRoute()
const { isAuthInitialized, isLogin } = useAuth()
const { clearSearchState, restoreSearchState, saveSearchState } = useProductSearchState()
const initialRouteKey = route.fullPath
const restoredSearchState = restoreSearchState(initialRouteKey)

const searchInput = ref('')
const selectedCategory = ref('')
const categories = ref([])
const products = ref(restoredSearchState?.products || [])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const errorMessage = ref('')
const bookmarkErrorMessage = ref('')
const bookmarksByProductId = ref(new Map())
const bookmarkPendingProductId = ref(null)
const hasNext = ref(restoredSearchState?.hasNext ?? true)
const nextOffset = ref(restoredSearchState?.nextOffset ?? 0)
const loadMoreTrigger = ref(null)
const pageSize = 40
let observer = null
let productRequestId = 0
let activeRouteKey = initialRouteKey
let skipInitialLoad = Boolean(restoredSearchState)

const mapProduct = (product) => ({
  id: String(product.id),
  name: product.title,
  imageUrl: product.image,
  category: product.category?.name || '',
  brand: product.brand || '',
  price: product.lprice || 0,
  link: product.link,
})

const getCategoryId = () => {
  const categoryQuery = String(route.query.category || '')
  return /^\d+$/.test(categoryQuery) ? categoryQuery : null
}

const loadProducts = async ({ append = false } = {}) => {
  if (append && (isLoading.value || isLoadingMore.value || !hasNext.value)) {
    return
  }

  const requestId = ++productRequestId

  if (append) {
    isLoadingMore.value = true
  } else {
    isLoading.value = true
    products.value = []
    nextOffset.value = 0
    hasNext.value = true
  }
  errorMessage.value = ''

  try {
    const result = await fetchProducts({
      query: route.query.search || '',
      categoryId: getCategoryId(),
      limit: pageSize,
      offset: append ? nextOffset.value : 0,
    })

    if (requestId !== productRequestId) {
      return
    }

    const loadedProducts = result.results.map(mapProduct)
    products.value = append ? [...products.value, ...loadedProducts] : loadedProducts
    nextOffset.value = result.next_offset
    hasNext.value = result.has_next
  } catch (error) {
    if (requestId === productRequestId) {
      if (!append) {
        products.value = []
      }
      errorMessage.value = error.message || '제품을 불러오지 못했습니다.'
    }
  } finally {
    if (requestId === productRequestId) {
      isLoading.value = false
      isLoadingMore.value = false
    }
  }
}

const loadMoreProducts = () => {
  if (nextOffset.value !== null) {
    loadProducts({ append: true })
  }
}

const loadCategories = async () => {
  try {
    categories.value = await fetchProductCategories()

    const categoryQuery = String(route.query.category || '')
    if (categoryQuery && !/^\d+$/.test(categoryQuery)) {
      const matchedCategory = categories.value.find(
        (category) => category.name === categoryQuery,
      )

      if (matchedCategory) {
        router.replace({
          name: 'ProductSearch',
          query: {
            ...route.query,
            category: matchedCategory.id,
          },
        })
      }
    }
  } catch (error) {
    errorMessage.value = error.message || '카테고리를 불러오지 못했습니다.'
  }
}

const loadBookmarks = async () => {
  bookmarkErrorMessage.value = ''

  if (!isLogin.value) {
    bookmarksByProductId.value = new Map()
    return
  }

  try {
    const bookmarks = await fetchBookmarks()
    bookmarksByProductId.value = new Map(
      bookmarks.map((bookmark) => [bookmark.product.id, bookmark.id]),
    )
  } catch (error) {
    bookmarkErrorMessage.value = error.message || '즐겨찾기 상태를 불러오지 못했습니다.'
  }
}

const toggleProductBookmark = async (product) => {
  if (!isLogin.value) {
    router.push({ name: 'Login' })
    return
  }

  const productId = Number(product.id)
  if (bookmarkPendingProductId.value !== null) {
    return
  }

  bookmarkPendingProductId.value = productId
  bookmarkErrorMessage.value = ''

  try {
    const bookmarkId = bookmarksByProductId.value.get(productId)
    const updatedBookmarks = new Map(bookmarksByProductId.value)

    if (bookmarkId) {
      await deleteBookmark(bookmarkId)
      updatedBookmarks.delete(productId)
    } else {
      const bookmark = await createBookmark(productId)
      updatedBookmarks.set(productId, bookmark.id)
    }

    bookmarksByProductId.value = updatedBookmarks
  } catch (error) {
    bookmarkErrorMessage.value = error.message || '즐겨찾기 상태를 변경하지 못했습니다.'
  } finally {
    bookmarkPendingProductId.value = null
  }
}

const handleSearch = () => {
  // 검색 로직
  router.push({
    name: 'ProductSearch',
    query: {
      ...route.query,
      search: searchInput.value || undefined,
    },
  })
}
const changeCategory = () => {
  router.push({
    name: 'ProductSearch',
    query: {
      ...route.query,
      category: selectedCategory.value || undefined,
    },
  })
}

watch(
  () => [route.query.search, route.query.category],
  ([newSearch, newCategory]) => {
    searchInput.value = newSearch || ''
    selectedCategory.value = newCategory || ''

    if (skipInitialLoad && route.fullPath === activeRouteKey) {
      skipInitialLoad = false
      return
    }

    clearSearchState()
    activeRouteKey = route.fullPath
    loadProducts()
  },
  { immediate: true },
)

watch(loadMoreTrigger, (newTrigger, oldTrigger) => {
  if (!observer) {
    return
  }

  if (oldTrigger) {
    observer.unobserve(oldTrigger)
  }

  if (newTrigger) {
    observer.observe(newTrigger)
  }
})

watch(
  [isAuthInitialized, isLogin],
  ([isInitialized]) => {
    if (isInitialized) {
      loadBookmarks()
    }
  },
  { immediate: true },
)

onMounted(() => {
  loadCategories()

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        loadMoreProducts()
      }
    },
    { rootMargin: '200px' },
  )

  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }

  if (restoredSearchState) {
    nextTick(() => {
      window.scrollTo({ top: restoredSearchState.scrollY })
    })
  }
})

onBeforeRouteLeave((to) => {
  if (to.name === 'ProductDetail') {
    saveSearchState({
      routeKey: activeRouteKey,
      products: products.value,
      nextOffset: nextOffset.value,
      hasNext: hasNext.value,
      scrollY: window.scrollY,
    })
    return
  }

  clearSearchState()
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.search-controls {
  display: flex;
  gap: 1em;
  margin-bottom: 1em;
}
.category-select {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.5em;
  font-size: 1em;
  width: 130px;
}
.search-form {
  flex: 1;
  display: flex;
  justify-content: space-between;
  gap: 0.5em;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background-color: #fff;
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
  width: 200px;
}
.text-button {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
}
.error-message {
  color: red;
}
ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}
li {
  min-width: 0;
}
.load-more-trigger {
  height: 1px;
}
</style>
