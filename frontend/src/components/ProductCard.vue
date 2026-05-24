<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const getProductDetailPage = (id) => {
  router.push({ name: 'ProductDetail', params: { id } })
}

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <div class="product-card" @click="getProductDetailPage(props.product.id)">
    <img :src="props.product.imageUrl" alt="Product Image" />
    <h2>{{ props.product.name }}</h2>
    <p>{{ props.product.brand }}</p>
    <p>{{ props.product.price }}</p>
    <p>{{ props.product.category }}</p>
  </div>
</template>

<style scoped>
.product-card {
  border: 1px solid #ccc;
  padding: 16px;
  margin-bottom: 16px;
}
.product-card img {
  width: 100%;
  height: auto;
}
.product-card h2 {
  margin: 8px 0;
}
.product-card p {
  margin: 4px 0;
}
.product-card:hover {
  cursor: pointer;
  background-color: #f9f9f9;
}
</style>
