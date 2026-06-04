<template>
  <h1>즐겨찾기페이지</h1>
  <ul>
    <li v-for="product in favoriteProducts" :key="product.id">
      <ProductCard :product="product" />
    </li>
  </ul>
</template>

<script setup>
import mockProducts from '@/data/mockProducts'
import ProductCard from '@/components/ProductCard.vue'

const favoriteProducts = mockProducts.slice(0, 4)
</script>

<style scoped>
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
