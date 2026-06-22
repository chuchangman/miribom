<template>
  <div class="product-card" @click="getProductDetailPage(props.product.id)">
    <button
      class="bookmark-button"
      :class="{ 'bookmark-button--active': isBookmarked }"
      type="button"
      :disabled="isBookmarkPending"
      @click.stop="toggleBookmark"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M6 4.75C6 3.78 6.78 3 7.75 3h8.5C17.22 3 18 3.78 18 4.75v15.5l-6-4.2-6 4.2V4.75Z" />
      </svg>
      <span class="sr-only">{{ isBookmarked ? '즐겨찾기 해제' : '즐겨찾기 추가' }}</span>
    </button>
    <div class="product-image-area">
      <img :src="props.product.imageUrl" :alt="props.product.name" />
    </div>
    <div class="product-info">
      <span v-if="props.product.category" class="category-badge">
        {{ props.product.category }}
      </span>
      <h2>{{ props.product.name }}</h2>
      <p class="product-price">{{ props.product.price.toLocaleString() }} <span>원</span></p>
    </div>
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
  height: 360px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background-color: #fff;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 10px 24px rgb(15 23 42 / 5%);
  transition:
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}
.bookmark-button {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 1;
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
  border-radius: 50%;
  background-color: white;
  color: var(--color-text-secondary);
  cursor: pointer;
  box-shadow: 0 6px 14px rgb(15 23 42 / 10%);
  transition:
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}
.bookmark-button:hover {
  background-color: #f8fbff;
  color: var(--color-primary-600);
  transform: translateY(-1px);
}
.bookmark-button svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
  stroke-linejoin: round;
}
.bookmark-button:disabled {
  cursor: pointer;
  opacity: 0.6;
}
.bookmark-button--active {
  color: var(--color-primary-600);
  background-color: #f3f7ff;
}
.bookmark-button--active svg {
  fill: currentColor;
}
.product-card .bookmark-button svg path {
  vector-effect: non-scaling-stroke;
}
.product-image-area {
  height: 198px;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at center, rgb(59 130 246 / 10%), transparent 42%),
    linear-gradient(135deg, #f8fbff 0%, #eaf2ff 100%);
}
.product-card img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  padding: 28px;
}
.product-info {
  padding: 16px 18px 22px;
}
.category-badge {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  background-color: #f3f7ff;
  color: var(--color-text-secondary);
  font-size: 0.78rem;
  font-weight: 700;
}
.product-card h2 {
  margin: 10px 0 0;
  min-height: 2.7em;
  color: var(--color-text);
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.4;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.product-price {
  margin: 12px 0 0;
  color: var(--color-text);
  font-size: 1.26rem;
  font-weight: 900;
  letter-spacing: -0.03em;
}
.product-price span {
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0;
}
.product-card:hover {
  cursor: pointer;
  border-color: var(--color-primary-200);
  background-color: #f8fbff;
  box-shadow: 0 14px 30px rgb(15 23 42 / 9%);
  transform: translateY(-2px);
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
