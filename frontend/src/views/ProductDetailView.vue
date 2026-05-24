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
    <section class="product-hero">
      <div class="image">
        <img :src="product.imageUrl" :alt="product.name" />
      </div>
      <div class="info">
        <p>{{ product.name }}</p>
        <p>{{ product.brand }}</p>
        <p>{{ product.price.toLocaleString() }} 원</p>
        <p>{{ product.category }}</p>
        <p>{{ product.description }}</p>
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

<style scoped>
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
</style>
