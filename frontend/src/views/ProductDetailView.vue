<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import mockProducts from '@/data/mockProducts'

const route = useRoute()

const product = computed(() => {
  return mockProducts.find((value) => route.params.id === value.id)
})
</script>

<template>
  <div v-if="!product">
    <h1>제품을 찾을 수 없습니다.</h1>
  </div>
  <div v-else>
    <h1>{{ product.id }}번째제품상세페이지</h1>
    <p>{{ product.name }}</p>
    <p>{{ product.brand }}</p>
    <p>{{ product.price }}</p>
  </div>
</template>
