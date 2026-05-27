<script setup>
import { useRouter, RouterLink } from 'vue-router'
import { ref } from 'vue'
import CategoryCard from '@/components/CategoryCard.vue'

const router = useRouter()

const searchQuery = ref('')

function search() {
  router.push({
    name: 'ProductSearch',
    query: searchQuery.value ? { search: searchQuery.value } : {},
  })
}
</script>

<template>
  <h1>구매 전, 실제 사용 영상으로 <span class="highlight">미리봄</span></h1>
  <h3>크기 · 작동음 · 공간 배치를 짧은 영상으로 확인하세요</h3>
  <form @submit.prevent="search" class="search-form">
    <input type="text" class="search-input" v-model.trim="searchQuery" placeholder="제품명 검색" />
    <button type="submit" class="text-button">검색</button>
  </form>
  <nav>
    인기검색어 :
    <RouterLink to="/products?search=건조기">건조기</RouterLink>
    <RouterLink to="/products?search=세탁기">세탁기</RouterLink>
    <RouterLink to="/products?search=냉장고">냉장고</RouterLink>
  </nav>
  <hr />
  <div>
    <h2>카테고리</h2>
    <p>원하는 가전을 골라보세요.</p>
    <div class="category-list">
      <CategoryCard category="세탁·건조" />
      <CategoryCard category="냉장고" />
      <CategoryCard category="주방소가전" />
      <CategoryCard category="청소기" />
      <CategoryCard category="계절가전" />
      <CategoryCard category="제습기·가습기" />
      <CategoryCard category="PC주변기기" />
      <CategoryCard category="빔프로젝터" />
    </div>
  </div>
</template>

<style scoped>
h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
}
h3 {
  font-size: 1.2em;
  margin-bottom: 1em;
}
.highlight {
  color: blue;
}
.search-form {
  margin-bottom: 1em;
  border: 1px solid #ccc;
  padding: 0.5em;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  gap: 0.5em;
}
.search-input {
  flex: 1;
  border: 0px;
  padding: 0.5em;
  font-size: 1em;
  width: 200px;
  margin-right: 0.5em;
}
.text-button {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
}
nav a {
  margin-right: 1em;
  text-decoration: none;
  color: black;
}
nav a:hover {
  text-decoration: underline;
}

.category-list {
  display: flex;
  gap: 1em;
  flex-direction: row;
  flex-wrap: wrap;
}
</style>
