<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, watch } from 'vue'
import mockProducts from '@/data/mockProducts'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const route = useRoute()

const searchInput = ref('')
const selectedCategory = ref('')

const filteredProducts = computed(() => {
  const searchQuery = route.query.search || ''
  const category = route.query.category || ''

  if (!searchQuery && !category) {
    return mockProducts
  }

  return mockProducts.filter((product) => {
    const matchesSearch = searchQuery
      ? product.name.toLowerCase().includes(searchQuery.toLowerCase())
      : true
    const matchesCategory = category ? product.category === category : true
    return matchesSearch && matchesCategory
  })
})

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
  () => route.query.search,
  (newSearch) => {
    searchInput.value = newSearch || ''
  },
  { immediate: true },
)

watch(
  () => route.query.category,
  (newCategory) => {
    selectedCategory.value = newCategory || ''
  },
  { immediate: true },
)
</script>

<template>
  <h1>제품검색페이지</h1>
  <select v-model="selectedCategory" @change="changeCategory">
    <option value="">전체</option>
    <option value="세탁·건조">세탁·건조</option>
    <option value="냉장고">냉장고</option>
    <option value="주방소가전">주방소가전</option>
    <option value="청소기">청소기</option>
    <option value="계절가전">계절가전</option>
    <option value="제습기·가습기">제습기·가습기</option>
    <option value="PC주변기기">PC주변기기</option>
    <option value="빔프로젝터">빔프로젝터</option>
  </select>
  <form @submit.prevent="handleSearch">
    <input type="text" placeholder="제품명 검색" v-model.trim="searchInput" />
    <button type="submit">검색</button>
  </form>
  <p v-if="filteredProducts.length === 0">검색 결과가 없습니다.</p>
  <ul v-else>
    <li v-for="product in filteredProducts" :key="product.id">
      <ProductCard :product="product" />
    </li>
  </ul>
</template>

<style scoped>
form {
  margin-bottom: 16px;
}
input {
  padding: 8px;
  margin-bottom: 8px;
}
button {
  padding: 8px 16px;
}
ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
}
li {
  margin-bottom: 16px;
  width: calc(25% - 16px);
  margin-right: 16px;
}
</style>
