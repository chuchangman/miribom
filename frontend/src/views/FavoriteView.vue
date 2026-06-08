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
