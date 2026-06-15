<template>
  <button type="button" class="favorite-item" @click="goProductDetail">
    <span class="favorite-image">
      <img :src="product.imageUrl" :alt="product.name" />
    </span>
    <span class="favorite-info">
      <strong>{{ product.name }}</strong>
      <span>{{ product.price.toLocaleString() }}원</span>
    </span>
  </button>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

const goProductDetail = () => {
  router.push({ name: 'ProductDetail', params: { id: props.product.id } })
}
</script>

<style scoped>
.favorite-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #dbe4f0;
  border-radius: 12px;
  background-color: #f8fafc;
  padding: 10px;
  text-align: left;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.favorite-item:hover {
  border-color: #93b4f5;
  background-color: #f3f7ff;
  box-shadow: 0 6px 14px rgb(37 99 235 / 12%);
  transform: translateX(3px);
}

.favorite-image {
  width: 68px;
  height: 68px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 10px;
  background-color: #f3f6fb;
}

.favorite-image img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
}

.favorite-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.favorite-info strong {
  display: -webkit-box;
  overflow: hidden;
  font-size: 1rem;
  line-height: 1.35;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.favorite-info span {
  font-size: 0.95rem;
  font-weight: 700;
  color: #2563eb;
}
</style>
