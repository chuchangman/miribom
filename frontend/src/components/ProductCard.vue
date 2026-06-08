<template>
  <div class="product-card" @click="getProductDetailPage(props.product.id)">
    <button class="bookmark-button" type="button" @click.stop="toggleBookmark">
      {{ isBookmarked ? '♥' : '♡' }}
    </button>
    <img :src="props.product.imageUrl" :alt="props.product.name" />
    <h2>{{ props.product.name }}</h2>
    <p>{{ props.product.brand }}</p>
    <p>{{ props.product.price.toLocaleString() }}원</p>
    <p>{{ props.product.category }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isBookmarked = ref(false)

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const getProductDetailPage = (id) => {
  router.push({ name: 'ProductDetail', params: { id } })
}

const toggleBookmark = () => {
  isBookmarked.value = !isBookmarked.value
}
</script>

<style scoped>
.product-card {
  position: relative;
  border: 1px solid #ccc;
  padding: 16px;
  margin-bottom: 16px;
  cursor: pointer;
}
.bookmark-button {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background-color: white;
  cursor: pointer;
  font-size: 18px;
}
.bookmark-button:hover {
  background-color: #f0f0f0;
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
