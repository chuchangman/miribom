<template>
  <div class="product-card" @click="getProductDetailPage(props.product.id)">
    <button
      class="bookmark-button"
      type="button"
      :disabled="isBookmarkPending"
      @click.stop="toggleBookmark"
    >
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
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
  isBookmarked: {
    type: Boolean,
    default: false,
  },
  manageBookmark: {
    type: Boolean,
    default: false,
  },
  isBookmarkPending: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['toggle-bookmark'])

const getProductDetailPage = (id) => {
  router.push({ name: 'ProductDetail', params: { id } })
}

const toggleBookmark = () => {
  if (props.isBookmarkPending) {
    return
  }

  emit('toggle-bookmark', props.product)
}
</script>

<style scoped>
.product-card {
  position: relative;
  box-sizing: border-box;
  height: 430px;
  border: 1px solid #ccc;
  padding: 16px;
  cursor: pointer;
  overflow: hidden;
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
.bookmark-button:disabled {
  cursor: pointer;
  opacity: 0.6;
}
.product-card img {
  width: 100%;
  height: 220px;
  display: block;
  object-fit: contain;
  background-color: white;
}
.product-card h2 {
  margin: 8px 0;
  min-height: 2.8em;
  font-size: 1.1em;
  line-height: 1.4;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.product-card p {
  margin: 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.product-card:hover {
  cursor: pointer;
  background-color: #f9f9f9;
}
</style>
