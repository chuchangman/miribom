<script setup>
import { RouterLink } from 'vue-router'
import mockProducts from '@/data/mockProducts'
</script>

<template>
  <h1>제품검색페이지</h1>
  <ul>
    <li v-for="product in mockProducts" :key="product.id">
      <RouterLink :to="{ name: 'ProductDetail', params: { id: product.id } }">{{
        product.name
      }}</RouterLink>
    </li>
  </ul>
</template>
